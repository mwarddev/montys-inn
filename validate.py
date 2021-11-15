from datetime import date
import re
import gspread
from google.oauth2.service_account import Credentials


SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("monty's_inn")

def validate_email(email):
    """
    Try block checks email address validation using regex and raises a
    ValueError if email address doesn't meet requirements.
    """
    try:
        pattern = r"^[\w\.-]+@[\w\.-]+\.[\w\.]+$"
        email_match = re.search(pattern, email)
        if email_match:
            return True
        else:
            raise ValueError(f"{email} is not valid")
    except ValueError as email_error:
        print(f"Unfortunately the email address you provided {email_error}.\n")
        print("Please provide a valid email address.\n")
        return False


def validate_date(user_date):
    """
    Validates format of user input date and checks that date
    is in range of the worksheet
    """
    try:
        date_in_range = SHEET.worksheet("bookings").col_values(1)
        date_pattern = r"^[\d]{2}\/[\d]{2}\/[\d]{4}$"
        date_match = re.search(date_pattern, user_date)
        if date_match:
            if user_date in date_in_range:
                return True
            else:
                print(f"\nSorry. The date you have entered ({user_date})")
                print("is not available. \nPlease enter another date.\n")
                return False
        else:
            raise ValueError(f"{user_date} is not valid")
    except ValueError as date_error:
        print(f"\nUnfortunately the date you provided {date_error}.")
        print("Please provide a valid date in the format dd/mm/yyyy.\n")
        return False


def validate_future_date(user_date):
    """
    Checks user entered date against datetime object to ensure
    past date is not entered.
    """
    date_column = SHEET.worksheet("bookings").col_values(1)
    today_date = date.today()
    format_date = today_date.strftime("%d/%m/%Y")
    for date_ind, date_val in enumerate(date_column):
        if format_date == date_val:
            today_ind = date_ind
    for date_ind, date_val in enumerate(date_column):        
        if user_date == date_val:
            user_ind = date_ind
            if int(user_ind) >= int(today_ind):
                return True
            else:
                print("\nSorry. This date has already passed.")
                print("please enter a valid date.\n")
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