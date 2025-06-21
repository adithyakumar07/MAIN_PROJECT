import psycopg2
import datetime
class AKs_BANK:
    def __init__(self):
        self.user = "A"
        self.password = '7'

    # Establishes connection to PostgreSQL database
    def connect_db(self):
        return psycopg2.connect(
            dbname="AK's_BANK",
            user="postgres",
            password="root",
            host="localhost",
            port=5432
        )

    # Function to deposit money into user's account
    def deposit_amount(self, conn, cursor, table_name, result):
        new_deposit = int(input("Enter Deposit Amount: "))
        new_balance = result[5] + new_deposit

        query = f"""
            INSERT INTO {table_name} (
                AADHAR_NO, FULL_NAME, PHONE_NO,
                NOMINEE_AADHAR, BALANCE, WITHDRAW, DEPOSIT
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            result[0], result[1], result[2], result[3],
            result[4], new_balance, 0, new_deposit
        ))

        conn.commit()
        print("\nTransaction:")
        print("Aadhar:", result[0])
        print("Name:", result[1])
        print("Deposited Amount:", new_deposit)
        print("New Balance:", new_balance)

    # Function to withdraw money from user's account
    def withdraw_amount(self, conn, cursor, table_name, result):
        print("\nUser found. Last transaction:")
        print("Aadhar:", result[0])
        print("Name:", result[1])
        print("Balance:", result[5])

        withdraw_amount = int(input("Enter Withdraw Amount: "))
        if withdraw_amount > result[5]:
            print("Insufficient balance.")
            return

        new_balance = result[5] - withdraw_amount

        query = f"""
            INSERT INTO {table_name} (
                AADHAR_NO, FULL_NAME, ADDRESS, PHONE_NO,
                NOMINEE_AADHAR, BALANCE, WITHDRAW, DEPOSIT
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            result[0], result[1], result[2], result[3],
            result[4], new_balance, withdraw_amount, 0
        ))

        conn.commit()
        print("Withdrawal successful. New Balance:", new_balance)

    # Function to show mini-statement
    def mini_statement(self, conn, cursor, table_name, result):
        print("\n---- AK's BANK MINI STATEMENT ----")
        print("Aadhar:", result[0])
        print("Name:", result[1])
        print("Phone No:", result[3])
        print("Time:", datetime.datetime.now())
        print("Current Balance:", result[5])

        cursor.execute(f"""
            SELECT BALANCE, WITHDRAW, DEPOSIT FROM {table_name}
            WHERE AADHAR_NO = %s
        """, (result[0],))
        transactions = cursor.fetchall()

        print("\n---- TRANSACTION HISTORY ----")
        print("Withdraw Amount | Deposit Amount | Balance")
        for t in transactions:
            print(f" {t[1]:<15} | {t[2]:<15} | {t[0]}")

    # Create a new user record
    def create_user(self, conn, cursor, table_name, aadhar_no):
        full_name = input("Enter Full Name: ")
        address = input("Enter Address: ")
        phone_no = input("Enter Phone Number: ")
        nominee_aadhar = input("Enter Nominee Aadhar Number: ")
        balance = int(input("Enter Initial Balance: "))
        withdraw = int(input("Enter Withdraw Amount (0 if none): "))
        deposit = int(input("Enter Deposit Amount (0 if none): "))

        query = f"""
            INSERT INTO {table_name} (
                AADHAR_NO, FULL_NAME, ADDRESS, PHONE_NO,
                NOMINEE_AADHAR, BALANCE, WITHDRAW, DEPOSIT
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            aadhar_no, full_name, address, phone_no,
            nominee_aadhar, balance, withdraw, deposit
        ))

        conn.commit()
        print("New user created successfully.")

    # Login and main program logic
    def login(self):
        entered_user = input("Please enter the username: ")
        if entered_user != self.user:
            print("Incorrect username.")
            return

        entered_password = input("Please enter the password: ")
        if entered_password != self.password:
            print("Incorrect password.")
            return

        print("Login successful!")

        try:
            conn = self.connect_db()
            cursor = conn.cursor()

            table_name = input("Enter Account Holder Name: ").strip().replace(" ", "_")

            try:
                cursor.execute(f"""
                    CREATE TABLE {table_name} (
                        AADHAR_NO BIGINT,
                        FULL_NAME VARCHAR(50),
                        ADDRESS TEXT,
                        PHONE_NO VARCHAR(15),
                        NOMINEE_AADHAR BIGINT,
                        BALANCE BIGINT,
                        WITHDRAW BIGINT,
                        DEPOSIT BIGINT
                    )
                """)
                conn.commit()
                print(f"Account '{table_name}' created.")
            except psycopg2.errors.DuplicateTable:
                conn.rollback()
                print(f"Account '{table_name}' already exists.")

            aadhar_no = int(input("Enter Aadhar Number: "))
            cursor.execute(f"""
                SELECT * FROM {table_name}
                WHERE AADHAR_NO = %s
                ORDER BY BALANCE DESC LIMIT 1
            """, (aadhar_no,))
            result = cursor.fetchone()

            if result:
                while True:
                    print("\n1. Deposit")
                    print("2. Withdraw")
                    print("3. Mini Statement")
                    print("4. Exit")
                    choice = input("Choose option (1/2/3/4): ")

                    if choice == '1':
                        self.deposit_amount(conn, cursor, table_name, result)
                    elif choice == '2':
                        self.withdraw_amount(conn, cursor, table_name, result)
                    elif choice == '3':
                        self.mini_statement(conn, cursor, table_name, result)
                    elif choice == '4':
                        print("Thank you for using AK's BANK!")
                        break
                    else:
                        print("Invalid choice.")
            else:
                print("User not found. Creating new user.")
                self.create_user(conn, cursor, table_name, aadhar_no)

        except Exception as e:
            print("ERROR:", e)

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

# Run the program
AKs_BANK().login()
