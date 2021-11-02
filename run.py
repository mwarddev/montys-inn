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
        pattern = r"([\w.-]+)@([\w.-]+)(\.[\w.]+)"
        match = re.search(pattern, email)
        if match:
            return True
        else:
            raise ValueError(f"{email} is not valid")
    except ValueError as e:
        print(f"Unfortunately the email address you provided {e}. \nPlease provide a valid email address.\n")
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
    print("Check availability")


def cancel_booking():
    print("Cancel Booking")



print("\nWelcome to Monty's Inn")
print("Monty's Inn is a ficticious beachfront bed and breakfast.")
print("Using this app you can check availability, book, and cancel rooms.")
print("All prices include the cost of breakfast which consists of spam eggs and ham")
print("(vegan option available).")

user_creds = get_user_creds()
menu = main_menu(user_creds)