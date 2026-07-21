"""
Sync Engine — Fixed Parser
Key fix: Skip Tally group HEADER rows, store only individual LEDGER rows
"""
import re
import logging
import requests
from datetime import datetime, timedelta
from core.db        import get_conn
from core.config    import TALLY_URL
from core.constants import MONTHS, SKIP_TALLY_GROUPS, COGS_GROUPS
from core.utils     import month_label
from sync.tally_connect import (
    get_all_companies, fetch_pl_data, fetch_bs_data, tally_date
)
from sync.masters_loader import get_mis_group

log = logging.getLogger(__name__)

# ── FIXED XML PARSER ───────────────────────────────────────
def parse_pl_xml(xml_text: str) -> list:
    """
    Parse Tally P&L XML.
    Tracks current_group from DSPACCNAME headers.
    Stores individual LEDGER rows (inside BSNAME blocks).
    Handles COGS breakdown: Purchase Accounts, Opening Stock, Closing Stock.
    """
    rows          = []
    lines         = xml_text.split('\n')
    current_group = ''
    i             = 0

    while i < len(lines):
        line = lines[i].strip()

        # Group header — update current_group tracker
        if '<DSPACCNAME>' in line and '<BSNAME>' not in (
                lines[i-1].strip() if i > 0 else ''):
            for j in range(i, min(i+4, len(lines))):
                m = re.search(r'<DSPDISPNAME>(.*?)</DSPDISPNAME>', lines[j])
                if m:
                    current_group = m.group(1).strip()
                    break

        # Individual ledger row
        if '<BSNAME>' in line:
            ledger = ''
            value  = 0.0

            for j in range(i, min(i+6, len(lines))):
                m = re.search(r'<DSPDISPNAME>(.*?)</DSPDISPNAME>', lines[j])
                if m:
                    ledger = m.group(1).strip()
                    break

            for j in range(i, min(i+8, len(lines))):
                m = re.search(r'<BSSUBAMT>(.*?)</BSSUBAMT>', lines[j])
                if m and m.group(1).strip():
                    value = _sf(m.group(1))
                    break

            if not ledger:
                i += 1
                continue

            lg = ledger.lower().strip()
            cg = current_group.lower().strip()

            # Skip known P&L section headers
            if lg in SKIP_TALLY_GROUPS:
                i += 1
                continue

            # Skip if ledger == group (group total row) EXCEPT for
            # Opening Stock and Closing Stock which are both group and ledger
            if lg == cg and lg not in ('opening stock', 'less: closing stock',
                                        'closing stock'):
                i += 1
                continue

            rows.append({
                'ledger':      ledger,
                'tally_group': current_group,
                'debit':       abs(value) if value < 0 else 0,
                'credit':      abs(value) if value > 0 else 0,
                'net':         value
            })

        i += 1

    # Deduplicate by (ledger, tally_group) — same ledger can appear in
    # multiple groups (e.g. 'Opening Stock' under 'Cost of Sales :' and
    # 'Opening Stock' group)
    seen = {}
    for r in rows:
        key = (r['ledger'], r['tally_group'])
        seen[key] = r
    return list(seen.values())

def _sf(v):
    try:
        return float(re.sub(r'[^\d.\-]', '', str(v or '')) or '0')
    except:
        return 0.0

# ── MAIN SYNC ──────────────────────────────────────────────
def sync_company_now(company_id: int) -> dict:
    """
    Lightweight on-demand sync for a SINGLE company (as opposed to
    sync_all(), which loops every company — too slow to call on every
    page load). Used by portal_pages/sidebar.py's auto-sync-on-refresh
    hook, so simply reloading a page can pick up new/back-dated Tally
    entries without the user visiting Sync Status and clicking manually.

    Reuses the exact same _sync_company() used by sync_all(), so the
    fiscal-year-lookback fix (see _sync_company / _lookback_start's
    docstrings) applies here too.
    """
    conn = get_conn()
    row = conn.execute(
        "SELECT tally_name, last_sync FROM companies WHERE id=?", (company_id,)
    ).fetchone()
    if not row:
        conn.close()
        return {'status': 'error', 'message': 'Company not found'}

    name, last_sync = row['tally_name'], row['last_sync']
    try:
        records = _sync_company(company_id, name, last_sync, conn)
        conn.execute("""
            UPDATE companies SET sync_status='ok',
            last_sync=datetime('now') WHERE id=?
        """, (company_id,))
        conn.commit()
        conn.close()
        return {'status': 'ok', 'records': records}
    except Exception as e:
        log.error("[AutoSync] Error syncing %s: %s", name, e, exc_info=True)
        conn.execute(
            "UPDATE companies SET sync_status='error' WHERE id=?", (company_id,)
        )
        conn.commit()
        conn.close()
        return {'status': 'error', 'message': str(e)}


def sync_all(progress_callback=None, tenant_id: int = 1) -> dict:
    companies = get_all_companies()
    if not companies:
        return {'status': 'error',
                'message': 'No companies found. Open a company in Tally first.'}

    conn    = get_conn()
    results = []

    for idx, co in enumerate(companies):
        name = co['name']
        if progress_callback:
            progress_callback(name, idx+1, len(companies))

        conn.execute("""
            INSERT INTO companies (tally_name, display_name, sync_status, tenant_id)
            VALUES (?,?,'syncing',?)
            ON CONFLICT(tenant_id, tally_name) DO UPDATE SET
                display_name=excluded.display_name, sync_status='syncing'
        """, (name, name, tenant_id))
        conn.commit()

        row       = conn.execute(
            "SELECT id, last_sync FROM companies WHERE tenant_id=? AND tally_name=?", (tenant_id, name)
        ).fetchone()
        cid       = row['id']
        last_sync = row['last_sync']

        try:
            records = _sync_company(cid, name, last_sync, conn)
            conn.execute("""
                UPDATE companies SET sync_status='ok',
                last_sync=datetime('now') WHERE id=?
            """, (cid,))
            conn.commit()
            results.append({'company': name, 'status': 'ok', 'records': records})
        except Exception as e:
            log.error("[Sync] Error %s: %s", name, e, exc_info=True)
            conn.execute(
                "UPDATE companies SET sync_status='error' WHERE id=?", (cid,)
            )
            conn.commit()
            results.append({'company': name, 'status': 'error', 'error': str(e)})

    conn.close()
    ok = sum(1 for r in results if r.get('status') == 'ok')
    return {'status': 'ok', 'synced': ok, 'total': len(results), 'results': results}

def _lookback_start(now: datetime) -> datetime:
    """
    Returns 1-Apr of the PREVIOUS fiscal year (Indian FY: Apr→Mar).

    Covers the current FY *and* the one before it (~12-24 months
    depending on where `now` falls in the FY). This matters because
    accountants commonly post adjusting/closing entries into a
    just-ended FY for months AFTER the new FY has already started
    (right through audit/filing season) — a "current FY only" window
    stops reaching those entries the moment the calendar rolls into
    the new FY. (This was caught in production: an entry posted into
    Mar-2026 was missed by re-sync once `now` moved into Jul-2026,
    because that's already inside FY 2026-27 and the old window no
    longer looked back into FY 2025-26 at all.)
    """
    current_fy_start_year  = now.year if now.month >= 4 else now.year - 1
    previous_fy_start_year = current_fy_start_year - 1
    return datetime(previous_fy_start_year, 4, 1)


def _sync_company(company_id, company_name, last_sync, conn) -> int:
    now = datetime.now()
    if last_sync is None:
        # Brand-new company: pull full history.
        start = datetime(now.year - 3, 4, 1)
    else:
        # INCREMENTAL SYNC — always re-fetch from 1-Apr of the PREVIOUS
        # fiscal year (not just the last-synced month, and not just the
        # current FY — see _lookback_start's docstring for why).
        #
        # Every write here is an UPSERT keyed on
        # (company_id, ledger_name, year, month) — see _sync_pl_monthly
        # / _sync_bs_monthly — so re-fetching already-correct months is
        # perfectly safe; it just overwrites with Tally's current
        # figures rather than duplicating rows.
        lookback = _lookback_start(now)
        last_dt  = datetime.fromisoformat(last_sync)
        start    = min(lookback, last_dt.replace(day=1))

    records  = 0
    records += _sync_pl_monthly(company_id, company_name, start, now, conn)
    records += _sync_bs_monthly(company_id, company_name, start, now, conn)
    records += _sync_ageing_company(company_id, company_name, conn)
    return records

def _sync_pl_monthly(company_id, company_name, start_dt, end_dt, conn) -> int:
    records = 0
    cur     = start_dt.replace(day=1)

    while cur <= end_dt:
        if cur.month == 12:
            nxt = cur.replace(year=cur.year+1, month=1, day=1)
        else:
            nxt = cur.replace(month=cur.month+1, day=1)
        month_end = nxt - timedelta(days=1)

        try:
            xml_text = fetch_pl_data(company_name,
                                     tally_date(cur),
                                     tally_date(month_end))
            rows = parse_pl_xml(xml_text)

            for r in rows:
                tg, mg = get_mis_group(r['ledger'], r.get('tally_group', ''))
                conn.execute("""
                    INSERT INTO pl_data
                        (company_id, ledger_name, tally_group, mis_group,
                         year, month, month_label, debit, credit, net)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(company_id, ledger_name, year, month)
                    DO UPDATE SET
                        tally_group=excluded.tally_group,
                        mis_group=excluded.mis_group,
                        debit=excluded.debit, credit=excluded.credit,
                        net=excluded.net, updated_at=datetime('now')
                """, (company_id, r['ledger'], tg, mg,
                      cur.year, cur.month,
                      month_label(cur.year, cur.month),
                      r.get('debit', 0), r.get('credit', 0), r.get('net', 0)))
                records += 1
            conn.commit()
        except Exception as e:
            log.error("[Sync] P&L %s %s: %s", company_name, cur.strftime('%b-%y'), e, exc_info=True)

        cur = nxt
    return records

def _sync_bs_monthly(company_id, company_name, start_dt, end_dt, conn) -> int:
    records = 0
    cur     = start_dt.replace(day=1)

    while cur <= end_dt:
        if cur.month == 12:
            nxt = cur.replace(year=cur.year+1, month=1, day=1)
        else:
            nxt = cur.replace(month=cur.month+1, day=1)
        month_end = nxt - timedelta(days=1)

        try:
            xml_text = fetch_bs_data(company_name,
                                     tally_date(cur),
                                     tally_date(month_end))
            rows = parse_bs_xml(xml_text)
            for r in rows:
                tg, mg = get_mis_group(r['ledger'], r.get('tally_group', ''))
                conn.execute("""
                    INSERT INTO bs_data
                        (company_id, ledger_name, tally_group, mis_group,
                         year, month, month_label, closing_bal)
                    VALUES (?,?,?,?,?,?,?,?)
                    ON CONFLICT(company_id, ledger_name, year, month)
                    DO UPDATE SET
                        closing_bal=excluded.closing_bal,
                        updated_at=datetime('now')
                """, (company_id, r['ledger'], tg, mg,
                      cur.year, cur.month,
                      month_label(cur.year, cur.month),
                      r.get('balance', 0)))
                records += 1
            conn.commit()
        except Exception as e:
            log.error("[Sync] BS %s %s: %s", company_name, cur.strftime('%b-%y'), e, exc_info=True)

        cur = nxt
    return records


# ── AGEING SYNC (Bills Receivable / Bills Payable) ─────────────────────────

def _parse_tally_date(d: str):
    """Parse Tally date strings like '1-Apr-25' or '01-04-2025'"""
    if not d:
        return None
    for fmt in ('%d-%b-%y', '%d-%b-%Y', '%d-%m-%Y', '%Y%m%d'):
        try:
            return datetime.strptime(d.strip(), fmt).strftime('%Y-%m-%d')
        except Exception:
            continue
    return None


def _fetch_ageing_xml(report_name: str, company_name: str) -> str:
    """Fetch Bills Receivable or Bills Payable XML from Tally"""
    xml_req = f"""<ENVELOPE>
<HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER>
<BODY><EXPORTDATA><REQUESTDESC>
<REPORTNAME>{report_name}</REPORTNAME>
<STATICVARIABLES>
<SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
<SVCURRENTCOMPANY>{company_name}</SVCURRENTCOMPANY>
</STATICVARIABLES>
</REQUESTDESC></EXPORTDATA></BODY></ENVELOPE>"""
    resp = requests.post(TALLY_URL,
                         data=xml_req.encode('utf-8'),
                         headers={'Content-Type': 'application/xml'},
                         timeout=30)
    return resp.text


def _parse_bills(xml_text: str) -> list:
    """Parse BILLFIXED blocks from Tally ageing XML response"""
    bills = []
    blocks = xml_text.split('<BILLFIXED>')
    for block in blocks[1:]:
        try:
            date    = re.search(r'<BILLDATE>(.*?)</BILLDATE>', block)
            ref     = re.search(r'<BILLREF>(.*?)</BILLREF>', block)
            party   = re.search(r'<BILLPARTY>(.*?)</BILLPARTY>', block)
            after   = block.split('</BILLFIXED>')[-1] if '</BILLFIXED>' in block else block
            amt     = re.search(r'<BILLCL>(.*?)</BILLCL>', after)
            due     = re.search(r'<BILLDUE>(.*?)</BILLDUE>', after)
            overdue = re.search(r'<BILLOVERDUE>(.*?)</BILLOVERDUE>', after)

            if not (date and party and amt):
                continue
            amount = float(amt.group(1).strip()) if amt else 0
            if abs(amount) < 1:
                continue

            bills.append({
                'party_name':   party.group(1).strip() if party else '',
                'bill_ref':     ref.group(1).strip() if ref else '',
                'bill_date':    _parse_tally_date(date.group(1).strip()) if date else None,
                'due_date':     _parse_tally_date(due.group(1).strip()) if due else None,
                'amount':       abs(amount),
                'days_overdue': int(overdue.group(1).strip()) if overdue else 0,
            })
        except Exception:
            continue
    return bills


def _sync_ageing_company(company_id: int, company_name: str, conn) -> int:
    """
    Sync Bills Receivable (customer) and Bills Payable (vendor) ageing
    data from Tally for the given company.
    Returns total number of bill records inserted.
    """
    synced_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total     = 0

    for party_type, report_name in [
        ('customer', 'Bills Receivable'),
        ('vendor',   'Bills Payable'),
    ]:
        try:
            xml_text = _fetch_ageing_xml(report_name, company_name)
            if 'LINEERROR' in xml_text:
                log.warning("[Ageing] %s for '%s': Tally error in response", report_name, company_name)
                continue

            bills = _parse_bills(xml_text)
            log.info("[Ageing] %s | %s: %d bills", company_name, party_type, len(bills))

            # Clear old data then insert fresh
            conn.execute(
                "DELETE FROM ageing_data WHERE company_id=? AND party_type=?",
                (company_id, party_type)
            )
            for b in bills:
                conn.execute("""
                    INSERT INTO ageing_data
                        (company_id, party_type, party_name, bill_ref,
                         bill_date, due_date, amount, days_overdue, synced_at)
                    VALUES (?,?,?,?,?,?,?,?,?)
                """, (company_id, party_type, b['party_name'], b['bill_ref'],
                      b['bill_date'], b['due_date'], b['amount'],
                      b['days_overdue'], synced_at))
            conn.commit()
            total += len(bills)

        except Exception as e:
            log.error("[Ageing] Error syncing %s for '%s': %s", report_name, company_name, e)

    return total


# ── FIXED XML PARSER ───────────────────────────────────────
def parse_pl_xml(xml_text: str) -> list:
    """
    Parse Tally P&L XML.
    KEY FIX: Track parent group properly.
    Store INDIVIDUAL LEDGER rows only.
    DSPDISPNAME under BSNAME = individual ledger
    DSPDISPNAME directly = group header (track as parent, don't store)
    """
    rows          = []
    lines         = xml_text.split('\n')
    current_group = ''
    i             = 0

    while i < len(lines):
        line = lines[i].strip()

        # Group header row (direct DSPACCNAME, not inside BSNAME)
        if '<DSPACCNAME>' in line and '<BSNAME>' not in (
            lines[i-1].strip() if i > 0 else ''):
            for j in range(i, min(i+4, len(lines))):
                m = re.search(r'<DSPDISPNAME>(.*?)</DSPDISPNAME>', lines[j])
                if m:
                    current_group = m.group(1).strip()
                    break

        # Individual ledger row (inside BSNAME block)
        if '<BSNAME>' in line:
            ledger = ''
            value  = 0.0

            # Get ledger name
            for j in range(i, min(i+6, len(lines))):
                m = re.search(r'<DSPDISPNAME>(.*?)</DSPDISPNAME>', lines[j])
                if m:
                    ledger = m.group(1).strip()
                    break

            # Get value (BSSUBAMT = individual amount)
            for j in range(i, min(i+8, len(lines))):
                m = re.search(r'<BSSUBAMT>(.*?)</BSSUBAMT>', lines[j])
                if m and m.group(1).strip():
                    value = _sf(m.group(1))
                    break

            # Skip if ledger name == group name (it's a sub-group header, not ledger)
            if ledger and ledger != current_group:
                # Skip known section headers
                if ledger.lower().strip() not in SKIP_TALLY_GROUPS:
                    rows.append({
                        'ledger':      ledger,
                        'tally_group': current_group,
                        'debit':       abs(value) if value < 0 else 0,
                        'credit':      abs(value) if value > 0 else 0,
                        'net':         value
                    })

        i += 1

    # Deduplicate by ledger name (keep last occurrence)
    seen = {}
    for r in rows:
        seen[r['ledger']] = r
    return list(seen.values())

def parse_bs_xml(xml_text: str) -> list:
    """Parse Balance Sheet XML — same structure as P&L"""
    rows          = []
    lines         = xml_text.split('\n')
    current_group = ''
    i             = 0

    while i < len(lines):
        line = lines[i].strip()

        if '<DSPACCNAME>' in line:
            for j in range(i, min(i+4, len(lines))):
                m = re.search(r'<DSPDISPNAME>(.*?)</DSPDISPNAME>', lines[j])
                if m:
                    current_group = m.group(1).strip()
                    break

        if '<BSNAME>' in line:
            ledger = ''
            value  = 0.0
            for j in range(i, min(i+6, len(lines))):
                m = re.search(r'<DSPDISPNAME>(.*?)</DSPDISPNAME>', lines[j])
                if m:
                    ledger = m.group(1).strip()
                    break
            for j in range(i, min(i+8, len(lines))):
                m = re.search(r'<BSSUBAMT>(.*?)</BSSUBAMT>', lines[j])
                if m and m.group(1).strip():
                    value = _sf(m.group(1))
                    break
                m2 = re.search(r'<BSMAINAMT>(.*?)</BSMAINAMT>', lines[j])
                if m2 and m2.group(1).strip():
                    value = _sf(m2.group(1))
                    break
            if ledger and ledger != current_group:
                rows.append({
                    'ledger':      ledger,
                    'tally_group': current_group,
                    'balance':     value
                })

        i += 1

    seen = {}
    for r in rows:
        seen[r['ledger']] = r
    return list(seen.values())
