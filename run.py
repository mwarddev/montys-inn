import validate
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
        if validate.validate_email(email):
            print("\nThank you. Your email address is valid.\n")
            break

    return fname, lname, email


def menu(creds):
    """
    This function takes a number as input to select a menu item
    and directs the user to the desired function.
    """
    print(f"\nWelcome {creds[0]}. Please select from the following options:\n")
    menu_options = """
    Enter 1 to check for availabilty and book a room.
    Enter 2 to view your booking/s.
    Enter 3 to cancel a booking.
    """
    print(menu_options)
    # Takes user input and checks choice against avilable options
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
    # Takes user input and validates for format, date in available
    # dates and date hasn't already passed.
    while True:
        print("Please enter the date using the following format: dd/mm/yyyy\n")
        start_date = input("Start date: ")
        if validate.validate_date(start_date):
            if validate.validate_future_date(start_date):
                print("\nThank You. This date is valid.")
                break
    return start_date


def get_duration_info():
    """
    Take and validate user duration input.
    """
    # Takes user input and validates that it's an integer.
    while True:
        print("\nHow many nights would you like to stay?")
        print("Maximum 14 nights\n")
        nights = input("Number of nights: \n")
        if validate.validate_duration(nights):
            print("Thank you.\n")
            duration = int(nights)
            break
        else:
            print("Value must be a number")
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
        # Checks if requested date range contains a booking.
        if "booked" in room_range:
            continue
        else:
            # Prints available room info.
            float_room_range = [float(price) for price in room_range]
            room_cost = round(sum(float_room_range), 2)
            rooms_dict.update({room_name: room_cost})
            print(f"\n{room_name} available\n")
            print(f"{room_name} sleeps {room_sleeps} with {room_beds}")
            print(f"{room_name} has {room_facilities} and {room_view}")
            print(f"Room cost: £{room_cost}")
            print(f"Duration: {duration} nights from {date_info}")
            print("=" * 79)
            rooms.append(room_name)
    return rooms, rooms_dict, start_date_index


def book_room(room_data, date_info, duration_info, user_creds):
    """
    Take user input to select required room and write
    booking data to spreadsheet
    """
    # Creates a dynamic options list of available rooms and
    # stores the data in a dictionary.
    booking_dict = {}
    print("\nPlease select one of the following options:\n")
    for ind, room in enumerate(room_data[0]):
        booking_dict.update({ind + 1: room})
        print(f"Enter {ind + 1} to book {room}.")
    # Prints other options
    print("Enter 0 to select a different date.")
    print("Enter 101 to exit to main menu.\n")

    update_worksheet = SHEET.worksheet("user_booking_info")
    # Checks user input for other options selected first.
    while True:
        booking_choice = input("Enter option: \n")
        if validate.validate_booking(booking_choice):
            booking_option = int(booking_choice)
            if booking_option == 0:
                main_booking()
            elif booking_option == 101:
                main_menu()
            # Validates if number is in options list.
            elif booking_option not in booking_dict.keys():
                print("\nThe option you entered is invalid.")
                print("Please try again.")
                book_room(room_data, date_info, duration_info, user_creds)
            else:
                print("\nProcessing your booking. Please wait...\n")
            # If room booking selected, validate input.
            # write to user_booking_info worksheet.

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
                                booked.update_cell(booked_row,
                                                   room_col, "booked")
                                row_count += 1
                    print(f"Thank you {user_creds[0]}")
                    print(f"You have booked {data[5]}")
                    print(f"From {date_info} for {duration_info} night/s")
                    print(f"Total cost: £{price}\n")
                    print("Booking complete.\n")
                    main_menu()


def get_booking_info(user_creds):
    """
    Retrieves user's booking info from worksheet
    """
    # Checks if bookings have been made against user's
    # email address and outputs booking info if available
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
            print(f"Duration: {user_bookings[4]} night/s")
            print(f"Cost: £{user_bookings[6]}")
            print("=" * 79)
            option += 1
    # Runs if no bookings found.
    if user_creds[2] not in email_col:
        print("\nSorry. We couldn't find your booking/s.")
        print("Please re-enter your details to try again.")
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
    cancel_string = input("Booking number: \n")

    try:
        if cancel_string != "":
            cancel_option = int(cancel_string)
            for ind, _ in enumerate(bookings):
                # Matches option selected with the index in the bookings list
                if cancel_option - 1 == ind:
                    # Gets the date of the selected booking
                    # to be used to get the row index in the bookings worksheet
                    selected_date = bookings[cancel_option - 1][3]
                    # Gets index of selected date
                    for date_ind, val in enumerate(booked_sheet.col_values(1)):
                        if selected_date == val:
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
                    # Get values from default prices worksheet and add
                    # them to the same cells in the bookings worksheet
                    while row_count <= int(bookings[cancel_option - 1][4]) - 1:
                        price = price_list.cell(booked_row + row_count,
                                                room_col).value
                        booked_sheet.update_cell(booked_row + row_count,
                                                 room_col, price)
                        row_count += 1
                    # Delete user booking info from user_booking_info worksheet
                    for row_ind, id_num in enumerate(info_sheet.col_values(8)):
                        if id_num == bookings[cancel_option - 1][7]:
                            info_sheet.delete_rows(row_ind + 1)
                    # Print success and return to main menu
                    print("\nYour room has been cancelled")
                    main_menu()
        else:
            raise ValueError()
    # Validates selected option.
    except ValueError:
        print("The option you entred is invalid.\nPlease enter a valid option")
        cancel(bookings)
    # Validates option is available.
    cancel_index_list = []
    for ind, _ in enumerate(bookings):
        cancel_index_list.append(ind)
    if cancel_option - 1 not in cancel_index_list:
        print("The option you entred is invalid.\nPlease try again.")
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


# Welcome message.
welcome = """
\nWelcome to Monty's Inn\n
Monty's Inn is a fictitious beachfront bed and breakfast.
Using this app you can check availability, book, and cancel rooms.
All prices include breakfast which consists of spam eggs and ham
(vegan option available).
"""
print(welcome)

start()
