# Hospital_Management_system
Console-based Hospital Management System using Python and SQLite
# Hospital Management System

A console-based Hospital Management System built using **Python** and **SQLite**.
It manages patients, doctors, appointments and billing, and generates reports.

## Features
- Patient registration and viewing
- Doctor management (name, specialization, fee)
- Appointment booking with patient and doctor ID validation
- Billing with automatic doctor fee calculation and payment tracking
- Reports: doctor-wise appointments, daily appointments, revenue

## Technologies Used
- Python (functions, loops, input validation)
- SQLite (relational database)
- SQL: CREATE, INSERT, SELECT, UPDATE, JOIN, LEFT JOIN, GROUP BY, Foreign Keys

## Database Tables
- patients (patient_id, name, age, gender, phone, address)
- doctors (doctor_id, name, specialization, fee)
- appointments (appointment_id, patient_id, doctor_id, date, status)
- bills (bill_id, appointment_id, amount, paid_status)

## How to Run
1. Install Python 3
2. Download hospital.py
3. Run in terminal: python hospital.py
4. The database (hospital.db) is created automatically on first run.

## Author
Sivasakthimurugan M