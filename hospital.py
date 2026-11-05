import sqlite3

def connect():
    conn = sqlite3.connect("hospital.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_tables():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        phone TEXT,
        address TEXT
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialization TEXT,
        fee REAL
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        date TEXT,
        status TEXT DEFAULT 'Booked',
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id INTEGER,
        amount REAL,
        paid_status TEXT DEFAULT 'Pending',
        FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
    )""")

    conn.commit()
    conn.close()

# ---------- Patients ----------
def add_patient():
    name = input("Patient name: ").strip()
    age = int(input("Age: "))
    gender = input("Gender (M/F/O): ").strip().upper()
    phone = input("Phone: ").strip()
    address = input("Address: ").strip()

    if not name or not phone.isdigit() or len(phone) != 10:
        print("Invalid name or phone number!")
        return

    conn = connect()
    conn.execute(
        "INSERT INTO patients (name, age, gender, phone, address) VALUES (?, ?, ?, ?, ?)",
        (name, age, gender, phone, address))
    conn.commit()
    conn.close()
    print("Patient added successfully!")

def view_patients():
    conn = connect()
    rows = conn.execute("SELECT * FROM patients").fetchall()
    conn.close()
    if not rows:
        print("No patients found.")
        return
    for r in rows:
        print(r)

# ---------- Doctors ----------
def add_doctor():
    name = input("Doctor name: ").strip()
    specialization = input("Specialization (Eg: Cardiologist): ").strip()
    fee = float(input("Consultation fee: "))

    if not name or not specialization:
        print("Name and specialization cannot be empty!")
        return

    conn = connect()
    conn.execute(
        "INSERT INTO doctors (name, specialization, fee) VALUES (?, ?, ?)",
        (name, specialization, fee))
    conn.commit()
    conn.close()
    print("Doctor added successfully!")

def view_doctors():
    conn = connect()
    rows = conn.execute("SELECT * FROM doctors").fetchall()
    conn.close()
    if not rows:
        print("No doctors found.")
        return
    for r in rows:
        print(r)

# ---------- Appointments ----------
def book_appointment():
    print("\n--- Patients ---")
    view_patients()
    print("\n--- Doctors ---")
    view_doctors()

    patient_id = int(input("\nEnter Patient ID: "))
    doctor_id = int(input("Enter Doctor ID: "))
    date = input("Enter date (YYYY-MM-DD): ").strip()

    conn = connect()

    patient = conn.execute(
        "SELECT * FROM patients WHERE patient_id = ?", (patient_id,)).fetchone()
    if not patient:
        print("Patient ID not found!")
        conn.close()
        return

    doctor = conn.execute(
        "SELECT * FROM doctors WHERE doctor_id = ?", (doctor_id,)).fetchone()
    if not doctor:
        print("Doctor ID not found!")
        conn.close()
        return

    conn.execute(
        "INSERT INTO appointments (patient_id, doctor_id, date) VALUES (?, ?, ?)",
        (patient_id, doctor_id, date))
    conn.commit()
    conn.close()
    print("Appointment booked successfully!")

def view_appointments():
    conn = connect()
    rows = conn.execute("""
        SELECT a.appointment_id, p.name, d.name, d.specialization, a.date, a.status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
    """).fetchall()
    conn.close()

    if not rows:
        print("No appointments found.")
        return

    print("\nID | Patient | Doctor | Specialization | Date | Status")
    for r in rows:
        print(r)
# ---------- Billing ----------
def create_bill():
    view_appointments()
    appointment_id = int(input("\nEnter Appointment ID: "))

    conn = connect()

    # Appointment irukkaanu check + doctor fee edukkrom (JOIN)
    row = conn.execute("""
        SELECT d.fee
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.appointment_id = ?
    """, (appointment_id,)).fetchone()

    if not row:
        print("Appointment ID not found!")
        conn.close()
        return

    # Already bill irukkaanu check
    existing = conn.execute(
        "SELECT * FROM bills WHERE appointment_id = ?", (appointment_id,)).fetchone()
    if existing:
        print("Bill already created for this appointment!")
        conn.close()
        return

    consultation_fee = row[0]
    medicine = float(input("Medicine charges (0 if none): "))
    total = consultation_fee + medicine

    conn.execute(
        "INSERT INTO bills (appointment_id, amount) VALUES (?, ?)",
        (appointment_id, total))
    conn.commit()
    conn.close()
    print(f"Bill created! Consultation: {consultation_fee}, Medicine: {medicine}, Total: {total}")


def view_bills():
    conn = connect()
    rows = conn.execute("""
        SELECT b.bill_id, p.name, d.name, b.amount, b.paid_status
        FROM bills b
        JOIN appointments a ON b.appointment_id = a.appointment_id
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
    """).fetchall()
    conn.close()

    if not rows:
        print("No bills found.")
        return

    print("\nBill ID | Patient | Doctor | Amount | Status")
    for r in rows:
        print(r)


def pay_bill():
    view_bills()
    bill_id = int(input("\nEnter Bill ID to mark as paid: "))

    conn = connect()
    bill = conn.execute(
        "SELECT paid_status FROM bills WHERE bill_id = ?", (bill_id,)).fetchone()

    if not bill:
        print("Bill ID not found!")
        conn.close()
        return

    if bill[0] == "Paid":
        print("This bill is already paid!")
        conn.close()
        return

    conn.execute(
        "UPDATE bills SET paid_status = 'Paid' WHERE bill_id = ?", (bill_id,))
    conn.commit()
    conn.close()
    print("Payment recorded. Bill marked as Paid!")
    # ---------- Reports ----------
def report_doctor_appointments():
    conn = connect()
    rows = conn.execute("""
        SELECT d.name, d.specialization, COUNT(a.appointment_id) AS total
        FROM doctors d
        LEFT JOIN appointments a ON d.doctor_id = a.doctor_id
        GROUP BY d.doctor_id
        ORDER BY total DESC
    """).fetchall()
    conn.close()

    if not rows:
        print("No doctors found.")
        return

    print("\n--- Doctor-wise Appointments ---")
    print("Doctor | Specialization | Total Appointments")
    for r in rows:
        print(r)


def report_daily_appointments():
    conn = connect()
    rows = conn.execute("""
        SELECT date, COUNT(*) AS total
        FROM appointments
        GROUP BY date
        ORDER BY date
    """).fetchall()
    conn.close()

    if not rows:
        print("No appointments found.")
        return

    print("\n--- Daily Appointments ---")
    print("Date | Total Appointments")
    for r in rows:
        print(r)


def report_revenue():
    conn = connect()
    rows = conn.execute("""
        SELECT paid_status, COUNT(*) AS bills, SUM(amount) AS total_amount
        FROM bills
        GROUP BY paid_status
    """).fetchall()
    conn.close()

    if not rows:
        print("No bills found.")
        return

    print("\n--- Revenue Report ---")
    print("Status | Number of Bills | Total Amount")
    for r in rows:
        print(r)
# ---------- Main menu ----------
def main():
    create_tables()
    while True:
        print("\n--- Hospital Management System ---")
        print("1. Add Patient")
        print("2. View Patients")
        print("3. Add Doctor")
        print("4. View Doctors")
        print("5. Book Appointment")
        print("6. View Appointments")
        print("7. Create Bill")
        print("8. View Bills")
        print("9. Pay Bill")
        print("10. Report: Doctor-wise Appointments")
        print("11. Report: Daily Appointments")
        print("12. Report: Revenue")
        print("0. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            add_patient()
        elif choice == "2":
            view_patients()
        elif choice == "3":
            add_doctor()
        elif choice == "4":
            view_doctors()
        elif choice == "5":
            book_appointment()
        elif choice == "6":
            view_appointments()
        elif choice == "7":
            create_bill()
        elif choice == "8":
            view_bills()
        elif choice == "9":
            pay_bill()
        elif choice == "10":
            report_doctor_appointments()
        elif choice == "11":
            report_daily_appointments()
        elif choice == "12":
            report_revenue()
        elif choice == "0":
            break
        else:
            print("Invalid choice!")

main()