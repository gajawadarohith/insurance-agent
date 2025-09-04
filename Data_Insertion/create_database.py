import sqlite3
import os

def create_database():
    """Create SQLite database with insurance customer data"""
    
    # Create data_insertion directory if it doesn't exist
    os.makedirs('data_insertion', exist_ok=True)
    
    # Connect to SQLite database (will create if doesn't exist)
    conn = sqlite3.connect('insurance_db.sqlite')
    cursor = conn.cursor()
    
    # Create policy_info table with exact structure
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS policy_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_holder_name TEXT NOT NULL,
            policy_number TEXT UNIQUE NOT NULL,
            product_name TEXT NOT NULL,
            policy_start_date TEXT NOT NULL,
            premium_due_date TEXT NOT NULL,
            outstanding_amount REAL NOT NULL,
            total_premium_paid REAL NOT NULL,
            sum_assured REAL NOT NULL,
            fund_value REAL NOT NULL,
            status TEXT NOT NULL,
            loyalty_benefits REAL NOT NULL,
            phone_number TEXT NOT NULL
        )
    ''')
    
    # Sample data with 20 customers
    sample_data = [
        ('Pratik Jadhav', 'PN1000', 'Smart Growth', '2019-08-04', '2024-11-25', 10895.00, 51582.00, 1000000.00, 462010.00, 'Active', 28544.00, '+919849475949'),
        ('Priya Sharma', 'PN1001', 'Health Shield Pro', '2020-03-15', '2024-10-15', 15800.00, 42000.00, 800000.00, 380000.00, 'Active', 22000.00, '+919849475949'),
        ('Rajesh Kumar', 'PN1002', 'Motor Insurance', '2018-12-10', '2024-09-20', 12500.00, 35000.00, 600000.00, 320000.00, 'Active', 18000.00, '+919849475949'),
        ('Anita Patel', 'PN1003', 'Home Protection', '2021-06-22', '2024-12-05', 8900.00, 28000.00, 500000.00, 250000.00, 'Active', 15000.00, '+919849475949'),
        ('Suresh Reddy', 'PN1004', 'Term Life Plan', '2017-11-08', '2024-08-30', 21000.00, 75000.00, 1500000.00, 850000.00, 'Active', 45000.00, '+919849475949'),
        ('Meera Singh', 'PN1005', 'Child Education Plan', '2022-01-14', '2024-11-15', 9800.00, 32000.00, 400000.00, 180000.00, 'Active', 12000.00, '+919849475949'),
        ('Vikram Malhotra', 'PN1006', 'Retirement Plus', '2016-09-30', '2024-07-25', 18500.00, 95000.00, 1200000.00, 680000.00, 'Active', 38000.00, '+919849475949'),
        ('Sunita Verma', 'PN1007', 'Critical Illness', '2020-07-18', '2024-12-01', 11200.00, 45000.00, 700000.00, 420000.00, 'Active', 25000.00, '+919849475949'),
        ('Arun Desai', 'PN1008', 'Personal Accident', '2021-04-12', '2024-09-12', 4500.00, 18000.00, 300000.00, 120000.00, 'Active', 8000.00, '+919849475949'),
        ('Kavita Joshi', 'PN1009', 'Wealth Builder', '2015-12-05', '2024-06-18', 32000.00, 120000.00, 2000000.00, 1500000.00, 'Active', 65000.00, '+919849475949'),
        ('Rahul Gupta', 'PN1010', 'Smart Growth', '2018-05-20', '2024-10-30', 14200.00, 58000.00, 900000.00, 520000.00, 'Active', 32000.00, '+919849475949'),
        ('Neha Kapoor', 'PN1011', 'Health Shield Pro', '2019-11-03', '2024-11-10', 16800.00, 48000.00, 850000.00, 450000.00, 'Active', 28000.00, '+919849475949'),
        ('Amit Shah', 'PN1012', 'Motor Insurance', '2017-08-15', '2024-09-05', 13800.00, 38000.00, 650000.00, 350000.00, 'Active', 20000.00, '+919849475949'),
        ('Pooja Mehta', 'PN1013', 'Home Protection', '2020-02-28', '2024-12-20', 7200.00, 25000.00, 450000.00, 220000.00, 'Active', 13000.00, '+919849475949'),
        ('Deepak Verma', 'PN1014', 'Term Life Plan', '2016-06-12', '2024-08-15', 22500.00, 82000.00, 1300000.00, 750000.00, 'Active', 42000.00, '+919849475949'),
        ('Ritu Sharma', 'PN1015', 'Child Education Plan', '2021-09-08', '2024-11-25', 10500.00, 35000.00, 450000.00, 200000.00, 'Active', 14000.00, '+919849475949'),
        ('Mohan Singh', 'PN1016', 'Retirement Plus', '2015-03-25', '2024-07-10', 19500.00, 105000.00, 1400000.00, 780000.00, 'Active', 48000.00, '+919849475949'),
        ('Sangeeta Patel', 'PN1017', 'Critical Illness', '2019-04-17', '2024-12-15', 11800.00, 52000.00, 750000.00, 480000.00, 'Active', 30000.00, '+919849475949'),
        ('Vishal Kumar', 'PN1018', 'Personal Accident', '2020-10-30', '2024-09-25', 5200.00, 20000.00, 350000.00, 140000.00, 'Active', 9000.00, '+919849475949'),
        ('Anjali Reddy', 'PN1019', 'Wealth Builder', '2014-07-22', '2024-06-30', 35000.00, 135000.00, 2200000.00, 1650000.00, 'Active', 72000.00, '+919849475949')
    ]
    
    # Insert sample data
    cursor.executemany('''
        INSERT OR REPLACE INTO policy_info 
        (policy_holder_name, policy_number, product_name, policy_start_date, 
         premium_due_date, outstanding_amount, total_premium_paid, 
         sum_assured, fund_value, status, loyalty_benefits, phone_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_data)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("✅ Database created successfully!")
    print("📊 Sample data inserted with 20 customers")
    print("📱 All customers have phone number: +919849475949")
    print("💾 Database file: insurance_db.sqlite")
    print("📋 Table structure matches your requirements exactly")

if __name__ == "__main__":
    create_database() 