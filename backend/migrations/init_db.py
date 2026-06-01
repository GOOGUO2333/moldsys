#!/usr/bin/env python3
"""Database initialization - Multi-table with foreign keys."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymysql
from werkzeug.security import generate_password_hash
from config import Config

def get_root_conn():
    """Connect as root (for creating database)"""
    return pymysql.connect(host=Config.DB_HOST, port=Config.DB_PORT,
        user='root', password=Config.DB_PASSWORD, charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)

def get_conn():
    """Connect as app user (for tables)"""
    return pymysql.connect(host=Config.DB_HOST, port=Config.DB_PORT,
        user=Config.DB_USER, password=Config.DB_PASSWORD,
        database=Config.DB_NAME, charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)

def init():
    print("[*] Starting database initialization...")
    print(f"    Host: {Config.DB_HOST}:{Config.DB_PORT}")
    print(f"    Database: {Config.DB_NAME}")
    print(f"    User: {Config.DB_USER}")

    # Step 1: Connect as root to create database
    print("[1/3] Creating database (as root)...")
    try:
        conn = get_root_conn()
        with conn.cursor() as c:
            c.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            # Grant privileges to app user
            c.execute(f"GRANT ALL PRIVILEGES ON {Config.DB_NAME}.* TO '{Config.DB_USER}'@'%'")
            c.execute("FLUSH PRIVILEGES")
        conn.commit()
        print("      OK")
    except Exception as e:
        print(f"      Warning: {e}")
    finally:
        try: conn.close()
        except: pass

    # Step 2: Connect as app user to create tables
    print("[2/3] Creating tables...")
    conn = get_conn()
    try:
        c = conn.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(20) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")

        c.execute("""CREATE TABLE IF NOT EXISTS molds (
            id INT AUTO_INCREMENT PRIMARY KEY, mold_no VARCHAR(20) UNIQUE NOT NULL,
            mold_name VARCHAR(50) NOT NULL, maintain_interval BIGINT NOT NULL,
            is_focused TINYINT DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")

        c.execute("""CREATE TABLE IF NOT EXISTS mold_status (
            id INT AUTO_INCREMENT PRIMARY KEY, mold_id INT NOT NULL,
            current_count BIGINT DEFAULT 0, last_maintain_count BIGINT DEFAULT 0,
            last_maintain_date DATE, total_production BIGINT DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (mold_id) REFERENCES molds(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")

        c.execute("""CREATE TABLE IF NOT EXISTS counter_reset_logs (
            id INT AUTO_INCREMENT PRIMARY KEY, mold_id INT NOT NULL,
            reset_count BIGINT NOT NULL, previous_total BIGINT NOT NULL,
            new_total BIGINT NOT NULL, reset_date DATE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (mold_id) REFERENCES molds(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")

        c.execute("""CREATE TABLE IF NOT EXISTS maintenance_logs (
            id INT AUTO_INCREMENT PRIMARY KEY, mold_id INT NOT NULL,
            previous_maintain_count BIGINT NOT NULL, new_maintain_count BIGINT NOT NULL,
            maintain_date DATE NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (mold_id) REFERENCES molds(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")

        print("      OK")

        # Step 3: Insert default data
        print("[3/3] Inserting default data...")

        hashed_pw = generate_password_hash('admin')
        c.execute("INSERT IGNORE INTO users (username, password) VALUES ('admin', %s)", (hashed_pw,))

        molds_data = [
            ('M001', '前盖模具A', 5000, 1),
            ('M002', '后盖模具B', 8000, 1),
            ('M003', '底座模具C', 3000, 0),
            ('M004', '侧板模具D', 10000, 0),
        ]
        for mold_no, name, interval, focused in molds_data:
            c.execute("INSERT IGNORE INTO molds (mold_no, mold_name, maintain_interval, is_focused) VALUES (%s, %s, %s, %s)", (mold_no, name, interval, focused))

        status_data = [
            (1, 52000, 45000, '2024-12-15', 50000),
            (2, 37400, 30000, '2024-10-20', 30000),
            (3, 18000, 12000, '2025-01-08', 0),
            (4, 85000, 80000, '2024-08-30', 0),
        ]
        for mold_id, cur, last, date, total in status_data:
            c.execute("""INSERT IGNORE INTO mold_status (mold_id, current_count, last_maintain_count, last_maintain_date, total_production)
                VALUES (%s, %s, %s, %s, %s)""", (mold_id, cur, last, date, total))

        c.execute("""INSERT IGNORE INTO counter_reset_logs (mold_id, reset_count, previous_total, new_total, reset_date)
            VALUES (1, 45000, 0, 45000, '2023-06-01'), (1, 5000, 45000, 50000, '2024-06-01')""")
        c.execute("""INSERT IGNORE INTO counter_reset_logs (mold_id, reset_count, previous_total, new_total, reset_date)
            VALUES (2, 30000, 0, 30000, '2023-08-01')""")

        conn.commit()
        print("      OK")
        print("[+] Database initialization completed!")

    except Exception as e:
        conn.rollback()
        print(f"[-] Error: {e}")
        raise
    finally: conn.close()

if __name__ == '__main__':
    init()
