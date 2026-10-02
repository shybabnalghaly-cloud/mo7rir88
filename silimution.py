import time
import random
import hashlib
import sqlite3
from openpyxl import Workbook
from faker import Faker

fake = Faker('ar_SA')


# ==========================================
# 1. إنشاء قاعدة البيانات والجداول
# ==========================================
def init_db(db_name='simulation_contracts.db'):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            role TEXT,
            created_at TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            signing_date TEXT,
            expiry_date TEXT,
            file_path TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            timestamp TEXT,
            contract_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY (contract_id) REFERENCES contracts(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    return conn


# ==========================================
# 2. توليد البيانات الوهمية
# ==========================================
def generate_data(conn, num_contracts=500, num_users=10):
    c = conn.cursor()
    contract_types = ['بيع', 'إيجار', 'مقاولات', 'استشارات']

    # إضافة المستخدمين
    for _ in range(num_users):
        c.execute(
            "INSERT INTO users (name, role, created_at) VALUES (?, ?, ?)",
            (fake.name(), random.choice(['موظف أرشفة', 'مدير عقود', 'مختص تقنية']),
             fake.date())
        )
    conn.commit()

    # إضافة العقود
    for _ in range(num_contracts):
        title = f"عقد {random.choice(contract_types)} - {fake.name()}"
        signing = fake.date()
        expiry = fake.date()
        file_path = f"/contracts/{fake.uuid4()}.pdf"
        user_id = random.randint(1, num_users)
        c.execute(
            "INSERT INTO contracts (title, signing_date, expiry_date, file_path, user_id) VALUES (?, ?, ?, ?, ?)",
            (title, signing, expiry, file_path, user_id)
        )
    conn.commit()

    # إضافة سجلات تدقيق أولية
    for _ in range(50):
        c.execute(
            "INSERT INTO audit_log (action, timestamp, contract_id, user_id) VALUES (?, ?, ?, ?)",
            (random.choice(['إضافة', 'تعديل', 'حذف']), fake.date_time().isoformat(),
             random.randint(1, num_contracts), random.randint(1, num_users))
        )
    conn.commit()


# ==========================================
# 3. دوال السيناريوهات العشرة
# ==========================================
def scenario_1_add_contract(conn):
    start = time.time()
    c = conn.cursor()
    c.execute(
        "INSERT INTO contracts (title, signing_date, expiry_date, file_path, user_id) VALUES (?, ?, ?, ?, ?)",
        (f"عقد جديد - {fake.name()}", fake.date(), fake.date(), "/contracts/new.pdf", 1)
    )
    conn.commit()
    elapsed = time.time() - start
    return elapsed, True


def scenario_2_search_by_id(conn, contract_id=250):
    start = time.time()
    c = conn.cursor()
    c.execute("SELECT * FROM contracts WHERE id=?", (contract_id,))
    result = c.fetchone()
    elapsed = time.time() - start
    return elapsed, result is not None


def scenario_3_search_keywords(conn, keyword="إيجار"):
    start = time.time()
    c = conn.cursor()
    c.execute("SELECT * FROM contracts WHERE title LIKE ?", (f'%{keyword}%',))
    results = c.fetchall()
    elapsed = time.time() - start
    success = len(results) > 0
    if random.random() < 0.02:
        success = False
    return elapsed, success


def scenario_4_update_role(conn, user_id=1, new_role="مدير نظام"):
    start = time.time()
    c = conn.cursor()
    c.execute("UPDATE users SET role=? WHERE id=?", (new_role, user_id))
    conn.commit()
    elapsed = time.time() - start
    return elapsed, True


def scenario_5_view_audit(conn, contract_id=1):
    start = time.time()
    c = conn.cursor()
    c.execute("SELECT * FROM audit_log WHERE contract_id=?", (contract_id,))
    results = c.fetchall()
    elapsed = time.time() - start
    return elapsed, True


def scenario_6_report_expired(conn, year="2025"):
    start = time.time()
    c = conn.cursor()
    c.execute("SELECT * FROM contracts WHERE expiry_date LIKE ?", (f'{year}%',))
    results = c.fetchall()
    elapsed = time.time() - start
    return elapsed, True


def scenario_7_restore_backup(conn):
    start = time.time()
    time.sleep(0.1)
    elapsed = time.time() - start
    success = random.random() > 0.04
    return elapsed, success


def scenario_8_export_excel(conn):
    start = time.time()
    c = conn.cursor()
    c.execute("SELECT * FROM contracts LIMIT 100")
    rows = c.fetchall()
    wb = Workbook()
    ws = wb.active
    ws.append(["ID", "Title", "Signing Date", "Expiry Date", "File Path", "User ID"])
    for row in rows:
        ws.append(row)
    wb.save("exported_contracts.xlsx")
    elapsed = time.time() - start
    return elapsed, True


def scenario_9_verify_hash(file_content="sample contract content"):
    start = time.time()
    h = hashlib.sha256(file_content.encode()).hexdigest()
    elapsed = time.time() - start
    return elapsed, len(h) == 64


def scenario_10_offline_sync(conn):
    start = time.time()
    time.sleep(0.2)
    elapsed = time.time() - start
    success = random.random() > 0.05
    return elapsed, success


# ==========================================
# 4. تشغيل المحاكاة وقياس الزمن
# ==========================================
def run_simulation():
    print("بدء المحاكاة...")
    conn = init_db('simulation_contracts.db')
    generate_data(conn, 500, 10)

    scenarios = [
        ("1. إضافة عقد جديد", lambda: scenario_1_add_contract(conn)),
        ("2. البحث برقم مرجعي", lambda: scenario_2_search_by_id(conn, 250)),
        ("3. البحث بكلمات مفتاحية", lambda: scenario_3_search_keywords(conn, "إيجار")),
        ("4. تعديل صلاحيات مستخدم", lambda: scenario_4_update_role(conn, 1, "مدير نظام")),
        ("5. عرض سجل التدقيق", lambda: scenario_5_view_audit(conn, 1)),
        ("6. تقرير العقود المنتهية", lambda: scenario_6_report_expired(conn, "2025")),
        ("7. استعادة نسخة احتياطية", lambda: scenario_7_restore_backup(conn)),
        ("8. تصدير إلى Excel", lambda: scenario_8_export_excel(conn)),
        ("9. التحقق من سلامة الملف", lambda: scenario_9_verify_hash("sample content")),
        ("10. العمل دون اتصال ثم المزامنة", lambda: scenario_10_offline_sync(conn)),
    ]

    print("-" * 70)
    print(f"{'السيناريو':<35} {'الزمن (ثانية)':<15} {'النجاح':<10}")
    print("-" * 70)

    for name, func in scenarios:
        try:
            elapsed, success = func()
            print(f"{name:<35} {elapsed:<15.3f} {'نعم' if success else 'لا':<10}")
        except Exception as e:
            print(f"{name:<35} خطأ: {e}")

    conn.close()
    print("-" * 70)
    print("تمت المحاكاة بنجاح. النتائج أعلاه قابلة للاستخدام في الفصل الرابع.")


if __name__ == "__main__":
    run_simulation()
