"""Run: python trace_avenuecorp.py — exact trace of calc for Avenuecorp"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

HEADERS = {'trading account:','profit & loss a/c','gross profit :',
           'gross profit c/o','gross profit b/f','nett profit','net profit'}

rows = conn.execute("""
    SELECT ledger_name, mis_group, tally_group, net FROM pl_data
    WHERE company_id=3
      AND ((year>2025) OR (year=2025 AND month>=4))
      AND ((year<2026) OR (year=2026 AND month<=3))
""").fetchall()

print(f"Total rows fetched: {len(rows)}")

cos=0; cos_found=False
cos_detail = []

for r in rows:
    tg=str(r['tally_group'] or '').lower().strip()
    mg=str(r['mis_group']   or '').lower().strip()
    ln=str(r['ledger_name'] or '').lower().strip()
    v =abs(r['net'] or 0)

    if tg in HEADERS or mg in HEADERS: continue

    # Cost of Sales group total capture
    if tg == 'cost of sales :' and ln == 'cost of sales :':
        cos += v; cos_found=True
        cos_detail.append(('GROUP_TOTAL', r['ledger_name'], v))
        continue

    # After skip
    if mg == '_group_total_': continue
    if ln == tg: continue

    # Any other cost of sales rows?
    if tg == 'cost of sales :':
        cos += v; cos_detail.append(('INDIVIDUAL', r['ledger_name'], v))
        continue

print(f"\ncos_found = {cos_found}")
print(f"cos total = {cos/1e7:.4f} Cr")
print(f"\nCOS rows:")
for type_, name, val in cos_detail[:20]:
    print(f"  [{type_}] '{name}' = {val/1e7:.4f} Cr")
if len(cos_detail) > 20:
    print(f"  ... {len(cos_detail)-20} more rows")

# Now check ALL tally_groups in data
print(f"\nAll unique tally_groups in Avenuecorp FY25-26:")
tgs = {}
for r in rows:
    tg = str(r['tally_group'] or '')
    tgs[tg] = tgs.get(tg, 0) + abs(r['net'] or 0)
for k,v in sorted(tgs.items(), key=lambda x: -x[1]):
    print(f"  '{k}': {v/1e7:.4f} Cr")

conn.close()
