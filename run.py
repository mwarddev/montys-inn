import gspread
from google.oauth2.service_account import Credentials
import re

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("monty's_inn")

def get_user_creds():
    """
    Get and store user name and email address for use in booking
     and cancellation process
    """

    print("\nPlease enter your first name.\n")
    fname = input("First Name: ")
    print("\nThank you.")
    print("Please enter your last name.\n")
    lname = input("Last Name: ")
    print("\nThank you.")

    while True:
        print("Please enter your email address.\n")
        email = input("Email: ")

        if validate_email(email):
            print("\nThank you. Your email address is valid.\n")
            break

    return fname, lname, email


def validate_email(email):
    """
    Try block checks email address validation using regex and raises a 
    ValueError if email address doesn't meet requirements.
    """

    try:
        pattern = r"[\w\.-]+@[\w\.-]+\.[\w\.]+"
        email_match = re.search(pattern, email)
        if email_match:
            return True
        else:
            raise ValueError(f"{email} is not valid")
    except ValueError as email_error:
        print(f"Unfortunately the email address you provided {email_error}.\nPlease provide a valid email address.\n")
        return False


def main_menu(fname):
    """
    This function takes a number as input to select a menu item 
    and directs the user to the desired function.
    """
    print(f"Welcome {fname[0]}. Please select one of the following options:\n")
    print("Enter 1 to check for availabilty and book a room.")
    print("Enter 2 cancel a booking.")

    menu_option = input("\nPlease enter an option number: ")

    if menu_option == "1":
        check_availability()
    elif menu_option == "2":
        cancel_booking()
    else:
        print("\nYour option is invalid. Please enter 1 or 2.\n")
        main_menu(fname)


def check_availability():
    """
    Take and validate user input and check the data against the booking spreadsheet for availability.
    """
    print("From which date would you like to start your stay?")

    while True:
        print("Please enter the date using the following format: dd/mm/yyyy\n")
        start_date = input("Start date: ")

        if validate_date(start_date):
            print("\nThank You. This date is valid")
            break
        return start_date

    while True:
        print("\nHow many nights would you like to stay?\n")
        duration = int(float(input("Number of nights: ")))

        if validate_duration(duration):
            print("Thank you.")
            break
        return duration

    print("\n Checking for available dates...")

    # Gets the index value of the start date requested by the user
    bookings = SHEET.worksheet("bookings")
    date_column = bookings.col_values(1)
    for date_index, item in enumerate(date_column):
        if item == start_date:
            start_date_index = date_index

    # Gets a list of lists of prices of rooms for the duration the user requested
    # Converts retrieved prices to floats
    available_rooms = []
    for values in range(2, 12):
        room_values = bookings.col_values(values)
        room_range = room_values[start_date_index:start_date_index + duration]
        room_name = room_values[0]
        room_sleeps = room_values[1]
        room_beds = room_values[2]
        room_facilities = room_values[3]
        room_view = room_values[4]
        room_cost = sum(room_range)
        if "booked" in room_range:
            continue
        else:
            print(f"{room_name} available.\n")
            print(f"{room_name} sleeps {room_sleeps} people in {room_beds}.\n")
            print(f"{room_name} has a {room_facilities} and has {room_view}.\n")
            print("=" * 80 "\n")
        float_room_range = [float(price) for price in room_range]
        available_rooms.append(float_room_range)
    print(available_rooms)


def validate_date(date):
    """
    Validates format of user input date and checks that date is in range of the worksheet
    """
    try:
        date_in_range = SHEET.worksheet("bookings").col_values(1)

        date_pattern = r"([\d{2}\/][\d{2}\/][\d{4}])"
        date_match = re.search(date_pattern, date)

        if date_match:
            if date in date_in_range:
                return True
            else:
                print(f"Sorry. The date you have entered({date}) is out of range.")
                print("Please select another date.")
                return False
            return True
        else:
            raise ValueError(f"{date} is not valid")
    except ValueError as date_error:
        print(f"Unfortunately the date you provided {date_error}.")
        print("Please provide a valid date in the format dd/mm/yyyy.\n")
        return False


def validate_duration(duration):
    """
    Converts user input to int & float then validates if input is a string or number.  
    """

    try:
        if isinstance(duration, int):
            return True
        else:
            raise ValueError(f"({duration}) is invalid")
    except ValueError as un_numable:
        print(f"The number you entered {un_numable}")
        print("Please enter a valid number. For example: 7")
        return False


def cancel_booking():
    print("Cancel Booking")



print("\nWelcome to Monty's Inn")
print("Monty's Inn is a ficticious beachfront bed and breakfast.")
print("Using this app you can check availability, book, and cancel rooms.")
print("All prices include the cost of breakfast which consists of spam eggs and ham")
print("(vegan option available).")

user_creds = get_user_creds()
menu = main_menu(user_creds)