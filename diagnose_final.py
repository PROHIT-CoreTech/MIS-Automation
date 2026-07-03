"""
Run: python diagnose_final.py
Exact comparison: Portal vs Tally
"""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), 'data', 'mis_portal.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# USP FY25-26
rows = conn.execute("""
    SELECT tally_group, mis_group,
           SUM(net) as net_sum
    FROM pl_data
    WHERE company_id=2
      AND ((year=2025 AND month>=4) OR (year=2026 AND month<=3))
    GROUP BY tally_group, mis_group
    ORDER BY tally_group, ABS(SUM(net)) DESC
""", ).fetchall()

conn.close()

TALLY = {
    'sales':     680_005_522.66,
    'dir_inc':    39_382_054.81,
    'gp':        194_904_677.95,
    'ind_exp':    72_009_881.92,
    'ind_inc':     1_559_462.83,
    'np':        124_454_258.86,
}

# ── REVENUE ───────────────────────────────────────────────
print("="*70)
print("1. REVENUE (Sales Accounts group total)")
print("="*70)
sa_total = 0
for r in rows:
    if str(r['tally_group']).lower() == 'sales accounts' and \
       str(r['mis_group']).lower() == 'sales accounts':
        sa_total += abs(r['net_sum'] or 0)
        print(f"   USED  | {r['tally_group']:25s} | {r['mis_group']:25s} | {abs(r['net_sum']):>15,.2f}")

print(f"\n   Portal Revenue  = {sa_total:>15,.2f}")
print(f"   Tally  Revenue  = {TALLY['sales']:>15,.2f}")
print(f"   Diff            = {sa_total - TALLY['sales']:>+15,.2f}")

# ── DIRECT INCOMES ─────────────────────────────────────────
print("\n" + "="*70)
print("2. DIRECT INCOMES (part of GP — Trading Account Credit)")
print("="*70)
di_total = 0
di_group = 0
for r in rows:
    if str(r['tally_group']).lower() == 'direct incomes':
        mg = str(r['mis_group']).lower()
        val = abs(r['net_sum'] or 0)
        if mg == 'direct incomes':
            di_group = val
            tag = "GROUP TOTAL"
        else:
            di_total += val
            tag = "LEDGER"
        print(f"   {tag:12s}| {r['tally_group']:25s} | {r['mis_group']:25s} | {val:>15,.2f}")

used_di = max(di_group, di_total)
print(f"\n   Group Total      = {di_group:>15,.2f}  ← USED (max)")
print(f"   Ledger Sum       = {di_total:>15,.2f}")
print(f"   Portal Dir Inc   = {used_di:>15,.2f}")
print(f"   Tally  Dir Inc   = {TALLY['dir_inc']:>15,.2f}")
print(f"   Diff (EXTRA)     = {used_di - TALLY['dir_inc']:>+15,.2f}  ← This inflates GP")

# ── COST OF SALES ──────────────────────────────────────────
print("\n" + "="*70)
print("3. COST OF SALES (COGS)")
print("="*70)
cos_total = 0
for r in rows:
    if str(r['tally_group']).lower() == 'cost of sales :':
        cos_total += abs(r['net_sum'] or 0)
        print(f"   USED  | {r['tally_group']:25s} | {r['mis_group']:25s} | {abs(r['net_sum']):>15,.2f}")

tally_cogs = TALLY['sales'] + TALLY['dir_inc'] + 21_09_63_668 - \
             (8_19_21_969.50 + 63_24_09_075.35 + 2_11_15_522.67) + TALLY['gp']
# simpler: COGS = Sales + DirInc - GP
tally_cos = TALLY['sales'] + TALLY['dir_inc'] - TALLY['gp']
print(f"\n   Portal COGS      = {cos_total:>15,.2f}")
print(f"   Tally  COGS      = {tally_cos:>15,.2f}")
print(f"   Diff             = {cos_total - tally_cos:>+15,.2f}")

# ── GP SUMMARY ─────────────────────────────────────────────
print("\n" + "="*70)
print("4. GROSS PROFIT SUMMARY")
print("="*70)
portal_gp = sa_total + used_di - cos_total
print(f"   Portal GP = {sa_total:,.2f} + {used_di:,.2f} - {cos_total:,.2f}")
print(f"             = {portal_gp:>15,.2f}")
print(f"   Tally  GP = {TALLY['gp']:>15,.2f}")
print(f"   DIFF      = {portal_gp - TALLY['gp']:>+15,.2f}")
print(f"\n   ROOT CAUSE: Direct Incomes extra = {used_di - TALLY['dir_inc']:+,.2f}")

# ── OVERHEAD ───────────────────────────────────────────────
print("\n" + "="*70)
print("5. OVERHEAD (Indirect Expenses)")
print("="*70)
oh_included = 0
oh_excluded = 0
print(f"\n   {'Status':10s} | {'Tally Group':25s} | {'MIS Group':30s} | {'Value':>15s}")
print("   " + "-"*85)
for r in rows:
    tg = str(r['tally_group']).lower()
    mg = str(r['mis_group']).lower()
    val = abs(r['net_sum'] or 0)
    if tg in ('indirect expenses', 'salaries and bonus', 'salary accounts'):
        _COGS = {'direct expenses','opening stock','purchase accounts','direct incomes','cost of sales :'}
        if mg in _COGS:
            oh_excluded += val
            status = "❌ EXCLUDED"
        else:
            oh_included += val
            status = "✅ INCLUDED"
        print(f"   {status:10s} | {r['tally_group']:25s} | {r['mis_group']:30s} | {val:>15,.2f}")

print(f"\n   Portal Overhead (included) = {oh_included:>15,.2f}")
print(f"   Portal Overhead (excluded) = {oh_excluded:>15,.2f}  ← These are MISSING")
print(f"   Tally  Overhead            = {TALLY['ind_exp']:>15,.2f}")
print(f"   MISSING from Portal        = {TALLY['ind_exp'] - oh_included:>+15,.2f}")
print(f"\n   REASON: 'Indirect Expenses|Direct Expenses' = {oh_excluded:,.2f}")
print(f"   = Salaries & Wages wrongly tagged as 'Direct Expenses' MIS group")
print(f"   = Fix: Re-sync after Masters.xlsx update")

# ── NET PROFIT ─────────────────────────────────────────────
print("\n" + "="*70)
print("6. NET PROFIT SUMMARY")
print("="*70)
ind_inc_total = sum(abs(r['net_sum'] or 0) for r in rows
                    if str(r['tally_group']).lower() == 'indirect incomes')
portal_np = portal_gp + ind_inc_total - oh_included
print(f"   Portal NP = GP({portal_gp/1e7:.2f}) + IndInc({ind_inc_total/1e7:.2f}) - OH({oh_included/1e7:.2f})")
print(f"             = {portal_np:>15,.2f}")
print(f"   Tally  NP = {TALLY['np']:>15,.2f}")
print(f"   DIFF      = {portal_np - TALLY['np']:>+15,.2f}")
