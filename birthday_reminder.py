import datetime
import sqlite3

from tabulate import tabulate

# DATABASE INITIALIZATION & CONNECTION ||

connection = sqlite3.connect("birthdays.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS birthdays
    (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        month INTEGER CHECK ( month >= 1 AND month <= 12 ),
        day INTEGER CHECK ( day >= 1 AND day <= 31 ),
        number TEXT CHECK ( number LIKE '+%' ),
        notes TEXT,
        guidelines TEXT,
        reminders TEXT,
        last_manual_send_year INTEGER,
        last_reminded_date TEXT,
        created_at TEXT DEFAULT (DATETIME('now')),
        UNIQUE (name, month, day)
    )
""")

print("\nDatabase and table created successfully!")


# CRUD FUNCTIONS ||

# --- Input Retrieval + LOOP for Invalid Choices ---


def get_choice(prompt, choices):

    while True:
        user_input = input(prompt)

        cleaned_input = user_input.strip().lower()

        if cleaned_input in choices:
            return cleaned_input

        else:
            print("Invalid choice! Try again...")

            continue


# --- Input Collection Functions ---


def get_name():

    while True:
        name = input("Enter the name:\n> ").strip().title()

        if name != "":
            print("Success!")
            break
        else:
            print("The contact must have a name.")

    return name


def get_month():

    while True:
        try:
            month = int(input("Enter the birth month (1 - 12):\n> ").strip())

            if month < 1 or month > 12:
                print("The month number must be from 1 to 12. \nNo 0s necessary.")
            else:
                print("Success!")
                break

        except ValueError:
            print("Please enter a valid number for the month (1 - 12).")

    return month


def get_day(month):

    while True:
        try:
            day = int(input("Enter the birth day (1 - 31):\n> ").strip())

            if day < 1 or day > 31:
                print("The day number must be from 1 to 31. \nNo 0s necessary.")
            elif month in {4, 6, 9, 11} and day > 30:
                print(f"The month {month} only has 30 days.")
            elif month == 2 and day > 28:
                print(f"The month {month} does not have {day} days.")
            else:
                print("Success!")
                break

        except ValueError:
            print("Please enter a valid number for the day (1 - 31).")

    return day


def get_number():

    while True:
        number = input(
            "Enter the number of the contact (Ex: +5554900008888):\n> "
        ).strip()

        if number == "":
            number = "None"
            print("No number added (optional).")
            break

        elif not number.startswith("+"):
            print(
                "The number must start with '+' followed by the Country Code (CC | Brazil's CC: +55)."
            )
            continue

        elif not number[1:].isdigit():
            print(
                "The number only accepts digits following the '+'. No spaces in between the digits either."
            )
            continue

        elif len(number) < 10:
            print("The number is too short. Please, check and correct the number.")
            continue

        elif len(number) > 15:
            print("The number is too long. Please, check and correct the number.")
            continue

        print("Success!")
        break

    return number


def get_notes():

    print("Provide any notes you would like to attach to this contact:\n")

    notes = input("> ").strip()

    if notes == "":
        notes = "None"

    return notes


def get_guidelines():

    print("Provide the automated message's specifications for this contact:\n")

    guidelines = input("> ").strip()

    if guidelines == "":
        guidelines = "None"

    return guidelines


def get_reminders():

    print(
        "Specify the days you would like to receive reminders before the event arrives.\n IMPORTANT: Use a comma (,) to separate the days: 7,3,1\n"
    )

    reminders = input("> ").strip()

    if reminders == "":
        reminders = "7,3,1"
        print("Reminders set to default values: 7, 3 and 1 day(s).")

    return reminders


# --- Calling all the functions + Inserting Data into Database ---


def list_single_row(rowid):

    try:
        sql = "SELECT * FROM birthdays WHERE ID = ?"

        if rowid == cursor.lastrowid:
            row_id = rowid

        elif rowid == id:
            row_id = rowid

        cursor.execute(sql, (row_id,))

        new_row = cursor.fetchone()

        if new_row:
            headers = [
                "ID",
                "Name",
                "Month",
                "Day",
                "Number",
                "Notes",
                "Guidelines",
                "Reminders",
                "Last Manual Send",
                "Last Reminded Date",
                "Creation Date",
            ]

            print(
                tabulate(
                    [new_row],
                    headers=headers,
                    tablefmt="fancy_grid",
                    maxcolwidths=[
                        None,
                        None,
                        None,
                        None,
                        None,
                        50,
                        80,
                        None,
                        None,
                        None,
                        None,
                    ],
                )
            )

        if new_row is None:
            print("\nRow not found after insertion into database; Weird!\n")

            pass

    except sqlite3.Error as e:
        print(f"\nAn error occurred while displaying the new inserted row: \n'{e}'\n")


def add_birthday():

    print(
        "Hi! (•◡•) / \nPlease, provide the information necessary for the new contact.\n"
    )

    # --- CALLING the functions & CREATING the values variables ---
    name = get_name()
    month = get_month()
    day = get_day(month)
    number = get_number()
    notes = get_notes()
    guidelines = get_guidelines()
    reminders = get_reminders()

    # --- Display SUCCESS message and report NEXT STEPS ---
    print(
        f"Success! Attempting the insertion of the information provided into the database with the following paramenters: \n\nName: {name}; \nMonth: {month}; \nDay: {day}; \nnumber: {number}; \nNotes: {notes}; \nguidelines: {guidelines}; \nReminders: {reminders}.\n"
    )

    # --- Create INSERT & DATA variables ---
    sql = "INSERT INTO birthdays (name, month, day, number, notes, guidelines, reminders) VALUES (?, ?, ?, ?, ?, ?, ?)"

    # WHILE LOOP: First TRY/EXCEPT (Duplicates + ANY Error handling)

    while True:
        values = (name, month, day, number, notes, guidelines, reminders)

        # 1st TRY (ORIGINAL VALUES)
        try:
            cursor.execute(sql, values)
            connection.commit()

            print(
                f"Successfully added {name}'s birthday to the database! ID: {cursor.lastrowid}"
            )

            list_single_row(cursor.lastrowid)

            break

        # 1st ERROR (DUPLICATES)
        except sqlite3.IntegrityError as e:
            connection.rollback()

            print(
                f"Sorry! The database already has a contact with the same name, month and day of birth. \nMore about the error: \n\n'{e}'\n"
            )

            print(
                "Would you like to change the name, month and day of this contact? ( y / n ) \n"
            )

            user_choice = get_choice("> ", ["y", "n"])

            if user_choice == "y":
                name = get_name()
                month = get_month()
                day = get_day(month)

                print("Attempting insertion...")

                continue

            elif user_choice == "n":
                print("Fair enough! Exiting...")

                break

        # 2nd ERROR (GENERAL)
        except sqlite3.Error as e:
            connection.rollback()

            print(
                f"Sorry! A database error occured and the insertion was not possible. \nMore about the error: \n\n'{e}'\n\n"
            )

            print(
                "Would you like to RETRY the insertion or REDO the formulary in its entirety? ( RETRY / REDO / QUIT ) \n"
            )

            user_choice = get_choice("> ", ["retry", "redo", "quit"])

            if user_choice == "retry":
                print("Attempting insertion once again...")

                continue

            elif user_choice == "redo":
                name = get_name()
                month = get_month()
                day = get_day(month)
                number = get_number()
                notes = get_notes()
                guidelines = get_guidelines()
                reminders = get_reminders()

                continue

            elif user_choice == "quit":
                print("Fair enough! Exiting...")

                break


# --- Current Database Display ---


def list_database(order_by):

    order = "DESC" if order_by.strip().upper() == "DESC" else "ASC"

    print("\n\nCurrent birthday's database:\n")

    query = f"SELECT * FROM birthdays ORDER BY created_at {order}"

    cursor.execute(query)

    headers = [
        "ID",
        "Name",
        "Month",
        "Day",
        "Number",
        "Notes",
        "Guidelines",
        "Reminders",
        "Last Manual Send",
        "Last Reminded Date",
        "Creation Date",
    ]

    rows = cursor.fetchall()

    print(
        tabulate(
            rows,
            headers=headers,
            tablefmt="fancy_grid",
            showindex=True,
            maxcolwidths=[None, None, None, None, None, 50, 80, None, None, None, None],
        )
    )


# --- Check ID function to only accept valid IDs when searching for a row in the DB ---


def check_id():

    while True:
        print("\nPlease, provide the contact's ID. (ex: 120) \n")

        user_input = input("> ")

        if not user_input:
            print("\nNo ID provided. Trying again...\n")

            continue

        cleaned_input = user_input.strip()

        try:
            converted_input = int(cleaned_input)

            id = converted_input

        except ValueError as e:
            print(
                f"\nInvalid input! You must provide a valid integer as the ID. \nMore about the error: \n'{e}'\n Trying again...\n"
            )

            continue

        try:
            cursor.execute("SELECT * FROM birthdays WHERE ID = ?", (id,))

            row = cursor.fetchone()

            if row:
                print("\nContact found:\n\n", row)

                contact_id = row[0]

                return contact_id

            else:
                print("\nNo ID found...\n")

                continue

        except sqlite3.Error:
            print(
                "\nAn error occurred. More about the error: \n'{e}'\n Try again or quit? ( retry / quit ) \n"
            ).strip().lower()

            choice = get_choice("> ", ["retry", "quit"])

            if choice == "retry":
                continue

            elif choice == "quit":
                print("\nCanceling edit...\n")

                return


# BIRTHDAY LOGIC (upcoming birthdays, sending reminders, days until, etc.) ||


def upcoming_birthdays(day_range=30):

    today = datetime.date.today()
    cursor.execute("SELECT ID, name, month, day, reminders FROM birthdays")
    rows = cursor.fetchall()

    for row in rows:
        print(f"{type(row)}, {row}")
        contact_id, name, month, day, reminders = row

        reminders_list = []
        for num in reminders.split(","):
            reminders_list.append(int(num))

        try:
            profile = datetime.date(today.year, int(month), int(day))
        except ValueError:
            profile = datetime.date(today.year, 3, 1)

        if profile <= today:
            try:
                profile = profile.replace(year=today.year + 1)
            except ValueError:
                profile = profile.replace((today.year, 3, 1) + 1)
        else:
            days_left = (profile - today).days

            if days_left <= day_range:
                print(
                    f"Found [ID:{contact_id}] {name}, ({month}/{day}) with {days_left} days left. \n"
                )
                return (contact_id, name, days_left, reminders_list)


contact_id = upcoming_birthdays()
name = upcoming_birthdays()
days_left = upcoming_birthdays()
reminders_list = upcoming_birthdays()


def reminder_filter():

    for x in reminders_list:
        if x > days_left:
            reminders_list.delete(x)
        else:
            pass
    return reminders_list


active_reminders = reminder_filter()


# USER INTERACTION (CLI Menu) ||

# --- Menu Build ---


while True:
    print("""
    What would you like to do?

        Display Database (1)
        Display Upcoming Birthdays (2)
        Insert NEW Contact (3)
        Edit Contact (4)
        Delete Contact (5)
        QUIT (6)
    """)

    choice = get_choice("> ", ["1", "2", "3", "4", "5", "6"])

    if choice == "1":
        list_database("ASC")

        continue

    elif choice == "2":
        upcoming_birthdays()

    elif choice == "3":
        print("Are you sure? ( y / n )\n")

        confirmation = get_choice("> ", ["y", "n"])

        if confirmation == "y":
            add_birthday()

        elif confirmation == "n":
            continue

    elif choice == "4":
        while True:
            print("\nID of the contact you would like to edit.\n")

            id = check_id()

            print(
                "What would you like to change about this contact? \n\nChoose: \nname \nmonth \nday \nnumber \nnotes \nguidelines \nreminders \n"
            )

            modification = get_choice(
                "> ",
                ["name", "month", "day", "number", "notes", "guidelines", "reminders"],
            )

            if modification == "name":
                name = get_name()

                column = "name"

                change = name

            elif modification == "month":
                month = get_month()

                column = "month"

                change = month

            elif modification == "day":
                day = get_day(month)

                column = "day"

                change = day

            elif modification == "number":
                number = get_number()

                column = "number"

                change = number

            elif modification == "notes":
                notes = get_notes()

                column = "notes"

                change = notes

            elif modification == "guidelines":
                guidelines = get_guidelines()

                column = "guidelines"

                change = guidelines

            elif modification == "reminders":
                reminders = get_reminders()

                column = "reminders"

                change = reminders

            sql = f"UPDATE birthdays SET {column} = ? WHERE ID = ?"

            # As ID becomes a TUPLE (as the entire row from the ID is linked (as a tuple) to this variable), we use [0] to get only the ID part of the tuple
            values = (change, id)

            try:
                cursor.execute(sql, values)
                connection.commit()
                row = cursor.fetchall()

                list_single_row(id)

                print(
                    "\nEditing successfully completed! Would you like to make any more edits? ( y / n )\n"
                )

                choice = get_choice("> ", ["y", "n"])

                if choice == "y":
                    continue

                elif choice == "n":
                    print("Exiting...")

                    break

            except sqlite3.IntegrityError as e:
                connection.rollback()

                print(
                    f"Sorry! The database already has a contact with the same name, month and day of birth. \nMore about the error: \n\n'{e}'\n\n"
                )

                continue

            except sqlite3.Error as e:
                connection.rollback()

                print(
                    f"Sorry! A database error occured and the insertion was not possible. \nMore about the error: \n\n'{e}'"
                )

                continue

    elif choice == "5":
        print("\n\nID of the contact you would like to delete.")

        id = check_id()

        print("\nAre you sure you would like to delete this contact? [YES/NO]\n")

        choice = get_choice("> ", ["yes", "no"])

        if choice == "yes":
            cursor.execute("DELETE FROM birthdays WHERE ID = ?", (id,))
            connection.commit()

            print(f"\nRow from ID {id} deleted. Displaying the updated database:")

            try:
                list_database("ASC")

            except Exception:
                print(
                    "\nNot able to display the current database. Sending you back to the menu..."
                )

                continue

        elif choice == "no":
            print("Returning to menu...")

            continue

    elif choice == "6":
        print("Are you sure? ( y / n )\n")

        confirmation = get_choice("> ", ["y", "n"])

        if confirmation == "y":
            print("Exiting...")

            break

        elif confirmation == "n":
            continue


# MAIN / SCHEDULER ENTRYPOINT ||
