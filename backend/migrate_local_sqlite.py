import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "lhcrm.db")
if os.path.exists(db_path):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    
    # Check leads columns
    cols = [r[1] for r in cur.execute("PRAGMA table_info(leads)").fetchall()]
    print(f"[*] Leads columns count: {len(cols)}")
    
    if "source_type" not in cols:
        cur.execute("ALTER TABLE leads ADD COLUMN source_type VARCHAR(50) DEFAULT 'kommo'")
        print("[+] Added column source_type to leads table")
    
    if "loss_reason" not in cols:
        cur.execute("ALTER TABLE leads ADD COLUMN loss_reason VARCHAR(255)")
        print("[+] Added column loss_reason to leads table")

    if "unidade" not in cols:
        cur.execute("ALTER TABLE leads ADD COLUMN unidade VARCHAR(100)")
        print("[+] Added column unidade to leads table")

    if "procedimento" not in cols:
        cur.execute("ALTER TABLE leads ADD COLUMN procedimento VARCHAR(100)")
        print("[+] Added column procedimento to leads table")

    if "origem" not in cols:
        cur.execute("ALTER TABLE leads ADD COLUMN origem VARCHAR(100)")
        print("[+] Added column origem to leads table")

    if "suborigem" not in cols:
        cur.execute("ALTER TABLE leads ADD COLUMN suborigem VARCHAR(100)")
        print("[+] Added column suborigem to leads table")

    con.commit()
    con.close()
    print("[OK] Local SQLite Schema updated successfully.")
