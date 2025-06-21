import psycopg2
import datetime

class Solution_Bank:
    def _init_(self):
        self.user = 'Employee@Bank'            
        self.password = 'employee'

    # Establishes connection to PostgreSQL database
    def connect_db(self):
        return psycopg2.connect(
            dbname="Solution_Bank",
            user="postgres",
            password="root",
            host="localhost",
            port=5432
        )

    # Function to deposit money into user's account
    def deposit_amount(self, conn, cursor, table_name, result):
        # Re-fetch latest balance
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM {} 
            WHERE AADHAR_NO = {}
            ORDER BY ctid DESC LIMIT 1
        """.format(table_name, result[0]))
    
        result = cursor.fetchone()  #  latest record

        # Proceed with fresh balance
        new_deposit = int(input("Enter Deposit Amount: "))
        new_balance = result[5] + new_deposit  #  correct balance

        cursor.execute("""
            INSERT INTO {} (
                AADHAR_NO, FULL_NAME, ADDRESS, PHONE_NO,
                NOMINEE_AADHAR, BALANCE, WITHDRAW, DEPOSIT
            ) VALUES ({}, '{}', '{}', {}, {}, {}, {}, {})
        """.format(table_name, result[0], result[1], result[2], result[3],
                result[4], new_balance, 0, new_deposit))

        conn.commit()
        cursor.close()

        print("\nTransaction:")
        print("Aadhar:", result[0])
        print("Name:", result[1])
        print("Deposited Amount:", new_deposit)
        print("New Balance:", new_balance)
        print("Transaction successful Deposited.")


    # Function to withdraw money from user's account
    def withdraw_amount(self, conn, cursor, table_name, result):
    # Always re-fetch latest transaction
        conn = self.connect_db()        
        cursor = conn.cursor()  
        cursor.execute("""  
            SELECT * FROM {} 
            WHERE AADHAR_NO = {}
            ORDER BY ctid DESC LIMIT 1
        """.format(table_name, result[0]))
    
        result = cursor.fetchone()  #  Fetch the latest balance

        print("\nUser found. Last transaction:")
        print("Aadhar:", result[0])
        print("Name:", result[1])
        print("Balance:", result[5])

        withdraw_amount = int(input("Enter Withdraw Amount: "))

        # Check for sufficient balance
        if withdraw_amount > result[5]:
            print("Insufficient balance.")
            return
        if withdraw_amount < 0 or withdraw_amount > 100000:
            print("Withdraw amount must not exceed 100000.")
            return

        new_balance = result[5] - withdraw_amount
        print("New Balance after withdrawal:", new_balance)

        # Insert withdrawal transaction
        cursor.execute("""
            INSERT INTO {} (
                AADHAR_NO, FULL_NAME, ADDRESS, PHONE_NO,
                NOMINEE_AADHAR, BALANCE, WITHDRAW, DEPOSIT
            ) VALUES ({}, '{}', '{}', {}, {}, {}, {}, {})
        """.format(table_name, result[0], result[1], result[2], result[3],
                result[4], new_balance, withdraw_amount, 0))

        conn.commit()
        cursor.close()
        print("Transaction successful Withdrawn.")


    def mini_statement(self,conn,cursor,table_name,result):
        print("----SOLUTION_BANK----")
        print("Aadhar : ",result[0])
        print("Name :",result[1])
        print("phone_no :",result[3])
        print("Time :",datetime.datetime.now())
        print("Current Balance :",result[5])

        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM {} WHERE AADHAR_NO = {}
        """.format(table_name, result[0]))
        transactions = cursor.fetchall()
        print("\n------------TRANSACTION HISTORY----------------")
        print("Withdraw Amount | Deposit Amount | Balance")
        print("-------------------------------------------------")
        for transaction in transactions: 
            if transaction[6] != 0:
                withdraw = transaction[6]
            else:
                withdraw = 0 
            if transaction[7] != 0:
                deposit = transaction[7]
            else:
                deposit = 0 
            if transaction[5] != 0:
                balance = transaction[5]
            else:
                balance = 0
            print("{:<15}|{:>16}|{:>10}".format(withdraw, deposit, balance))
        cursor.close()
    def balance_enquiry(self,conn,cursor,table_name,result):
        conn = self.connect_db()    
        cursor = conn.cursor()  
        cursor.execute("""  
            SELECT * FROM {} 
            WHERE AADHAR_NO = {}
            ORDER BY ctid DESC LIMIT 1
        """.format(table_name, result[0]))
        result = cursor.fetchone()  
        cursor.close()
        print("\n----BALANCE ENQUIRY----")
        print("Time:", datetime.datetime.now())
        print("Name:", result[1])
        print("Current Balance:", result[5])


    # Create a new user record if not found in DB
    def create_user(self, conn, cursor, table_name, aadhar_no):
        # Collect all user details from input
        full_name = input("Enter Full Name: ")
        address = input("Enter Address: ")
        phone_no = int(input("Enter Phone Number: "))
        nominee_aadhar = int(input("Enter Nominee Aadhar Number: "))
        balance = int(input("Enter Initial Balance: "))
        deposit = int(input("Enter Deposit Amount: "))

        # Insert new user record into the table
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO {} (
                AADHAR_NO, FULL_NAME, ADDRESS, PHONE_NO,
                NOMINEE_AADHAR, BALANCE, WITHDRAW, DEPOSIT
            ) VALUES ({}, '{}', '{}', {}, {}, {}, {}, {})
        """.format(table_name, aadhar_no, full_name, address, phone_no,
                   nominee_aadhar, balance, 0, deposit))
        conn.commit()
        print("New account created.")

    # Login and main program logic
    def login(self):
        # Check for correct username
        entered_user = input("Please enter the username: ")
        if entered_user == self.user:
            # Check for correct password
            entered_password = input("Please enter the password: ")
            if entered_password == self.password:
                print("Login successful!")

                try:
                    # Connect to database and get cursor
                    conn = self.connect_db()
                    print("Database connected")
                    cursor = conn.cursor()

                    # Ask for table name
                    table_name = input("Enter Account Holder Name: ").strip()

                    # Try creating the table (fails if it already exists)
                    try:
                        cursor.execute("""
                            CREATE TABLE {} (
                                AADHAR_NO BIGINT,
                                FULL_NAME VARCHAR(50),
                                ADDRESS VARCHAR(50),
                                PHONE_NO BIGINT,
                                NOMINEE_AADHAR BIGINT,
                                BALANCE BIGINT,
                                WITHDRAW INT,
                                DEPOSIT BIGINT
                            );
                        """.format(table_name))
                        conn.commit()
                        print("Acccount '{}' created.".format(table_name))
                    except psycopg2.errors.DuplicateTable:
                        # If account exists, rollback the failed transaction
                        conn.rollback()
                        print("Account '{}' already exists.".format(table_name))

                    # Ask for Aadhar number and check if user exists
                    aadhar_no = int(input("Enter Aadhar Number: "))
                    cursor.execute("""
                        SELECT * FROM {} 
                        WHERE AADHAR_NO = {}
                        ORDER BY ctid DESC LIMIT 1  
                    """.format(table_name, aadhar_no))
                    result = cursor.fetchone()
                    # ctid is a hidden system column in PostgreSQL that refers to the physical location of a row. 
                    # It can be used to retrieve the most recent record for a given Aadhar number.
                    # But ctid is not meant for application logic, and it's not very beginner-friendly.
                    # It's recommended to use a more explicit identifier for application logic.
                    # If user exists, offer deposit or withdrawal
                    if result:  # if result is not None  
                        while True:
                            print("\nUser already exists.")
                            print("1. Deposit                   2. Withdraw")
                            print("3. Mini_statement            4. Balance Enquiry")
                            print("5. Cancel")
                            choice = input("Choose option (1/2/3/4/5): ")

                            if choice == '1':
                                self.deposit_amount(conn, cursor, table_name, result)
                            elif choice == '2':
                                self.withdraw_amount(conn, cursor, table_name, result)
                            elif choice == '3':
                                self.mini_statement(conn,cursor,table_name,result)
                            elif choice == '4':
                                self.balance_enquiry(conn,cursor,table_name,result)
                            elif choice == '5':
                                print("         Transaction declined.")
                                print("\n----------------------------------------------")
                                print("     Thank you for using our Bank!")
                                print("             Visit again!")
                                return False
                            else:
                                print("Invalid choice.")
                    else:
                        # If user not found, create new user
                        self.create_user(conn, cursor, table_name, aadhar_no)

                except Exception as e:
                    print("ERROR:", e)

            else:
                print("Incorrect password.")
        else:
            print("Incorrect username.")
Solution_Bank().login()