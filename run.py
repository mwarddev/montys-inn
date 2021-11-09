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
        print(f"Unfortunately the email address you provided {email_error}.\n")
        print("Please provide a valid email address.\n")
        return False


def main_menu(creds):
    """
    This function takes a number as input to select a menu item 
    and directs the user to the desired function.
    """
    print(f"Welcome {creds[0]}. Please select one of the following options:\n")
    print("Enter 1 to check for availabilty and book a room.")
    print("Enter 2 cancel a booking.")

    menu_option = input("\nPlease enter an option number: ")

    if menu_option == "1":
        main_booking()
    elif menu_option == "2":
        cancel_booking()
    else:
        print("\nYour option is invalid. Please enter 1 or 2.\n")
        main_menu(creds)

def get_date_info():
    """
    Take and validate user date input.
    """
    print("From which date would you like to start your stay?")

    while True:
        print("Please enter the date using the following format: dd/mm/yyyy\n")
        start_date = input("Start date: ")
        if validate_date(start_date):
            print("\nThank You. This date is valid")
            break
    return start_date


def get_duration_info():
    """
    Take and validate user duration input.
    """
    while True:
        print("\nHow many nights would you like to stay?\n")
        duration = int(float(input("Number of nights: ")))
        if validate_duration(duration):
            print("Thank you.\n")
            break
    return duration


def get_available_room_data(date, duration):
    """
    Check date data against bookings worksheet
    and get list of available rooms.
    """
    print("\n Checking for available rooms...\n")
    
    # Gets the index value of the start date requested by the user
    bookings = SHEET.worksheet("bookings")
    date_column = bookings.col_values(1)
    for date_index, item in enumerate(date_column):
        if item == date:
            start_date_index = date_index

    # Gets a list of lists of prices of rooms for the requested duration
    # Converts retrieved prices to floats
    rooms = []
    rooms_dict = {}
    for values in range(2, 12):
        room_values = bookings.col_values(values)
        room_range = room_values[start_date_index:start_date_index + duration]
        room_name = room_values[0]
        room_sleeps = room_values[1]
        room_beds = room_values[2]
        room_facilities = room_values[3]
        room_view = room_values[4]
        
        if "booked" in room_range:
            continue
        else:
            float_room_range = [float(price) for price in room_range]
            room_cost = sum(float_room_range)
            rooms_dict.update({room_name: room_cost})
            print(f"\n{room_name} available.\n")
            print(f"{room_name} sleeps {room_sleeps} with {room_beds}.")
            print(f"{room_name} has {room_facilities} and {room_view}.")
            print(f"Room cost = £{room_cost} for {duration} nights from {date}.")
            print("=" * 80)
            rooms.append(room_name)
    return rooms, rooms_dict


def book_room(room_data, date_info, duration_info, user_creds):
    """
    Take user input to select required room and write
    booking data to spreadsheet
    """
    print(room_data)
    print(duration_info)
    booking_dict = {}
    print("\nPlease select one of the following options:")
    for ind, room in enumerate(room_data[0]):
        booking_dict.update({ind + 1: room})
        print(f"Enter {ind + 1} to book {room}.")

    print("Enter 0 to select a different date.")
    print("Enter 'exit' to exit to main menu.\n")
    booking_option = input("Enter option: ")
    update_worksheet = SHEET.worksheet("user_booking_info")

    for key, value in booking_dict.items():
        if int(booking_option) == key:
            if value in room_data[1]:
                price = room_data[1][value]
                data = (user_creds[2], user_creds[0], user_creds[1], date_info, duration_info, value, price) 
                update_worksheet.append_row(data)


def validate_date(date):
    """
    Validates format of user input date and checks that date
    is in range of the worksheet
    """
    try:
        date_in_range = SHEET.worksheet("bookings").col_values(1)
        date_pattern = r"([\d{2}\/][\d{2}\/][\d{4}])"
        date_match = re.search(date_pattern, date)
        if date_match:
            if date in date_in_range:
                return True
            else:
                print(f"Sorry. The date you have entered ({date}) is out of range.")
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
    Converts user input to int & float then validates 
    if input is a string or number.
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


def main():
    """
    Call all functions
    """
    main.user_creds = get_user_creds()
    main_menu(main.user_creds)


def main_booking():
    """
    Call booking functions
    """
    date_info = get_date_info()
    duration_info = get_duration_info()
    room_data = get_available_room_data(date_info, duration_info)
    book_room(room_data, date_info, duration_info, main.user_creds)

print("\nWelcome to Monty's Inn")
print("Monty's Inn is a ficticious beachfront bed and breakfast.")
print("Using this app you can check availability, book, and cancel rooms.")
print("All prices include breakfast which consists of spam eggs and ham")
print("(vegan option available).")

main()
