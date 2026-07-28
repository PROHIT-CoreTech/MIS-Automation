import sqlite3

conn = sqlite3.connect('data/mis_portal.db')
conn.row_factory = sqlite3.Row

# Apni company ka id yahan daal (2 = Unique Steel Products, apne hisaab se badal)
rows = conn.execute("""
    SELECT tally_group, SUM(net) as total
    FROM pl_data
    WHERE company_id=2 AND year=2025
    GROUP BY tally_group
    ORDER BY tally_group
""").fetchall()

for r in rows:
    print(f"{r['tally_group']:30s} {r['total']:>18,.2f}")

conn.close()