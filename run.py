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


def get_user_creds():
    """
    Get and store user name and email address for use in booking
    and cancellation process
    """
    # Get first name
    while True:
        print("\nPlease enter your first name.\n")
        fname = input("First Name: \n")
        if fname == "":
            print("First Name can not be blank.")
        else:
            print("\nThank you.")
            break

    # Get last name
    while True:
        print("Please enter your last name.\n")
        lname = input("Last Name: \n")
        if lname == "":
            print("Last Name can not be blank.")
        else:
            print("\nThank you.")
            break

    # Get and validate email
    while True:
        print("Please enter your email address.\n")
        email = input("Email: \n")

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


def menu(creds):
    """
    This function takes a number as input to select a menu item
    and directs the user to the desired function.
    """
    print(f"\nWelcome {creds[0]}. Please select one of the following options:\n")
    print("Enter 1 to check for availabilty and book a room.")
    print("Enter 2 to view your booking/s.")
    print("Enter 3 cancel a booking.")

    menu_option = input("\nPlease enter an option number: \n")

    if menu_option == "1":
        main_booking()
    elif menu_option == "2":
        booking_info()
    elif menu_option == "3":
        cancel_booking()
    else:
        print("\nYour option is invalid. Please enter 1, 2 or 3.\n")
        menu(creds)


def get_date_info():
    """
    Take and validate user date input.
    """
    print("\nFrom which date would you like to start your stay?")

    while True:
        print("Please enter the date using the following format: dd/mm/yyyy\n")
        start_date = input("Start date: ")
        if validate_date(start_date):
            if validate_future_date(start_date):
                print("\nThank You. This date is valid.")
                break
            else:
                print("\nSorry. This date has already passed.")
                print("please enter a valid date.\n")
    return start_date


def get_duration_info():
    """
    Take and validate user duration input.
    """
    while True:
        print("\nHow many nights would you like to stay?\n")
        duration = int(float(input("Number of nights: \n")))
        if validate_duration(duration):
            print("Thank you.\n")
            break
    return duration


def get_available_room_data(date_info, duration):
    """
    Check date data against bookings worksheet
    and get list of available rooms.
    """
    print("\n Checking for available rooms...\n")

    # Gets the index value of the start date requested by the user
    bookings = SHEET.worksheet("bookings")
    date_column = bookings.col_values(1)
    for date_index, item in enumerate(date_column):
        if item == date_info:
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
            room_cost = round(sum(float_room_range), 2)
            rooms_dict.update({room_name: room_cost})
            print(f"\n{room_name} available\n")
            print(f"{room_name} sleeps {room_sleeps} with {room_beds}")
            print(f"{room_name} has {room_facilities} and {room_view}")
            print(f"Room cost: £{room_cost} for {duration} nights from {date_info}")
            print("=" * 80)
            rooms.append(room_name)
    return rooms, rooms_dict, start_date_index


def book_room(room_data, date_info, duration_info, user_creds):
    """
    Take user input to select required room and write
    booking data to spreadsheet
    """
    booking_dict = {}
    print("\nPlease select one of the following options:\n")
    for ind, room in enumerate(room_data[0]):
        booking_dict.update({ind + 1: room})
        print(f"Enter {ind + 1} to book {room}.")

    print("Enter 0 to select a different date.")
    print("Enter 101 to exit to main menu.\n")
    booking_option = int(input("Enter option: \n"))

    update_worksheet = SHEET.worksheet("user_booking_info")
    try:
        if booking_option == 0:
            main_booking()
        elif booking_option == 101:
            main_menu()
        else:
            print("\nProcessing your booking. Please wait...\n")

            # write to user_booking_info worksheet
            for key, value in booking_dict.items():
                if booking_option == key:
                    id_row = update_worksheet.col_values(8)
                    if id_row[-1] == "booking id":
                        new_id = 1
                    else:
                        new_id = int(id_row[-1]) + 1
                    if value in room_data[1]:
                        price = room_data[1][value]
                        data = (user_creds[2],
                                user_creds[0],
                                user_creds[1],
                                date_info,
                                duration_info,
                                value,
                                price,
                                new_id)
                        update_worksheet.append_row(data)

                    # Write to bookings worksheet
                    booked = SHEET.worksheet("bookings")
                    booked_row = booked.row_values(1)
                    for ind, val in enumerate(booked_row):
                        if val == data[5]:
                            room_col = ind + 1
                            row_count = 1
                            while row_count <= duration_info:
                                booked_row = room_data[2] + row_count
                                booked.update_cell(booked_row, room_col, "booked")
                                row_count += 1
                    print(f"Thank you {user_creds[0]}. You have booked {data[5]}")
                    print(f"from {date_info} for {duration_info} nights.")
                    print(f"Total cost: £{price}.\n")
                    print("Booking complete.\n")
                    main_menu()

    except ValueError:
        print("\nThe option you entered is invalid.")
        print("Please try again.")
        book_room(room_data, date_info, duration_info, user_creds)

    #for key, value in booking_dict.items():
        #if booking_option != key:
    if booking_option not in booking_dict.keys():
        print("\nThe option you entered is invalid.")
        print("Please try again.")
        book_room(room_data, date_info, duration_info, user_creds)


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
            if user_date == date_val:
                user_ind = date_ind
                if today_ind <= user_ind:
                    return True
                else:
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


def get_booking_info(user_creds):
    """
    Retrieves user's booking info from worksheet
    """
    print("\nSearching for your bookings...\n")
    view_bookings = SHEET.worksheet("user_booking_info")
    email_col = view_bookings.col_values(1)
    user_booking_list = []
    option = 1
    for ind, value in enumerate(email_col):
        if value == user_creds[2]:
            row_ind = ind
            user_bookings = view_bookings.row_values(row_ind + 1)
            user_booking_list.append(user_bookings)
            print(f"\nBooking number: {option}\n")
            print(f"Room: {user_bookings[5]}")
            print(f"Start date: {user_bookings[3]}")
            print(f"Duration: {user_bookings[4]} nights")
            print(f"Cost: £{user_bookings[6]}")
            print("=" * 80)
            option += 1

    if user_creds[2] not in email_col:
        print("\nSorry. We couldn't find your booking/s.")
        print("Please re-enter your name and email address to try again.")
        start()
    return user_booking_list


def cancel(bookings):
    """
    Get user data from get_booking_info function
    update bookings worksheet and delete required row from
    user_bookings_info worksheet
    """
    print("\nPlease select which booking you wish to cancel\n")
    booked_sheet = SHEET.worksheet("bookings")
    price_list = SHEET.worksheet("default_prices")
    info_sheet = SHEET.worksheet("user_booking_info")
    cancel_option = int(input("Booking number: \n"))

    try:
        for ind, _ in enumerate(bookings):
            # Matches option selected with the index in the bookings list
            if cancel_option - 1 == ind:
                # Gets the date of the selected booking
                # to be used to get the row index in the bookings worksheet
                selected_date = bookings[cancel_option - 1][3]
                # Gets index of selected date
                for date_ind, value in enumerate(booked_sheet.col_values(1)):
                    if selected_date == value:
                        selected_date_index = date_ind
                print("\nCancelling your booking...")
                # Gets the room row of the bookings worksheet to get
                # column index
                room_row = booked_sheet.row_values(1)
                for cell_ind, val in enumerate(room_row):
                    if val == bookings[cancel_option - 1][5]:
                        room_col = cell_ind + 1
                booked_row = selected_date_index + 1
                row_count = 0
                # Get values from default prices worksheet and add them to the
                # same cells in the bookings worksheet
                while row_count <= int(bookings[cancel_option - 1][4])- 1:
                    price = price_list.cell(booked_row + row_count, room_col).value
                    booked_sheet.update_cell(booked_row + row_count, room_col, price)
                    row_count += 1
                # Delete user booking info from user_booking_info worksheet
                for row_ind, booking_id in enumerate(info_sheet.col_values(8)):
                    if booking_id == bookings[cancel_option - 1][7]:
                        info_sheet.delete_rows(row_ind + 1)

                print("\nYour room has been cancelled")
                main_menu()
    except ValueError:
        print("The option you entred is invalid.")
        print("Please enter a valid option")
        cancel(bookings)

    cancel_index_list = []
    for ind, _ in enumerate(bookings):
        cancel_index_list.append(ind)
    if cancel_option - 1 not in cancel_index_list:
        print("The option you entred is invalid.")
        print("Please try again.")
        cancel(bookings)


def start():
    """
    Call all functions
    """
    start.user_creds = get_user_creds()
    main_menu()


def main_menu():
    """
    Call main menu function
    """
    menu(start.user_creds)


def main_booking():
    """
    Call booking functions
    """
    date_info = get_date_info()
    duration_info = get_duration_info()
    room_data = get_available_room_data(date_info, duration_info)
    book_room(room_data, date_info, duration_info, start.user_creds)
    main_menu()

def cancel_booking():
    """
    Call cancellation functions
    """
    booked_info = get_booking_info(start.user_creds)
    cancel(booked_info)
    main_menu()

def booking_info():
    """
    Calls the get_booking_info function
    """
    get_booking_info(start.user_creds)
    main_menu()


print("\nWelcome to Monty's Inn\n")
print("Monty's Inn is a ficticious beachfront bed and breakfast.")
print("Using this app you can check availability, book, and cancel rooms.")
print("All prices include breakfast which consists of spam eggs and ham")
print("(vegan option available).")

start()
