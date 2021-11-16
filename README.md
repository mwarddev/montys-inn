# Monty's Inn
## Room Booking System

Monty's Inn Room Booking System is a Command Line Interface (CLI) application for users to book a stay in the fictional beachfront Inn with a Monty Python theme. Users can check availabilty for any of the 10 rooms Monty's Inn has to offer. Rooms also have a different number of beds, different facilities and different views. Users will be able to book a room and cancel the reservation at a later date if required. All room prices include the cost of breakfasts which consist of spam, eggs and ham.

## User stories

* User Goals
    * The user wants to be able to check availabilty for the room they require to book.
    * The user wishes to choose a room depending on number of beds required, type of facilities (WC or full En Suite), and type of view.
    * The user wants to be able to book the room and recieve a calculated cost for the stay.
    * The user wants to be able to return to the application and cancel a booking.

* Owner's Goals
    * The owner wants to validate the user input to ensure the application runs without issue.
    * The owner wants to take user information to assign bookings to the user.
    * The owner wants to use the user information to reference the users booking in the event the user wishes to cancel the booking.

## Structure

The flowchart created with [lucid.app](https://lucid.app) shows the flow of the app's logic.

![flowchart](read_me_images/flowchart.png)

### Welcome Screen

![welcome_page](read_me_images/welcome_page.png)
The user starts off at the welcome screen. This screen tells the user the app is a bed and breakfast room booking app. The app asks the user for their first name, last name and email address. The app validates the name fields are not empty and validates the email address matches a Regular Expression pattern before advancing. If incorrect details are input, the user is asked to re-enter the details.

### Main Menu

![main_menu](read_me_images/main_menu.png)
The main menu greets the user by their first name and offers a choice on 3 options. 1. Check for availability and book a room. 2. View bookings. 3. Cancel bookings.
This menu is also validated, anything other than 1, 2 or three will raise an error and the user is asked to re-enter the option.

### Booking Option

![past_date_error](read_me_images/past_date_error.png)
The booking option takes a date in the format dd/mm/yyyy and validates it for correct format against a Regular Expression pattern. Then the date is check to see if it's in range of the bookings worksheet which holds all the room, date and pricing data. Finally the date is checked against today's date, using the datetime library, to make sure the selected date hasn't already passed. Once the date is validated, the user is then asked for the number of night's they wish to stay. This input is validated to make sure an integer is entered.

#### Bookings Worksheet

![bookings_worksheet](read_me_images/bookings_worksheet.png)

### Available Rooms

![available_rooms](read_me_images/available_rooms.png)
Using the date and duration the user entered, the app searches this range of data in the bookings worksheet and checks to see if any of the price cells in the range contain the string "booked". If they do, the room isn't added to the available rooms list. If they are available, the app displays information for each room in a list and calculates the cost for the stay. Once the dynamic list is compiled the user has the option of selecting a room to book, selecting a different date or returning to the main menu. The input is validated to make sure it's an integer and in the list of choices.

### Booking Confirmation

![room_book_menu](read_me_images/room_book_menu.png)
When a room is selected, the prices in that date range for that room are changed to the string "booked" and the user's booking details are stored in the user booking info worksheet (this gives the booking an id for use in cancellation). The room details are printed to the screen again with a confirmation message and the user is taken back to the main menu.
![booked_room_confirm](read_me_images/booked_room_confirm.png)

#### User Booking Info Worksheet

![booking_info_worksheet](read_me_images/booking_info_worksheet.png)


### View Bookings

![view_bookings](read_me_images/view_bookings.png)
The view bookings option uses the email address the user entered at the start screen and checks the user booking info worksheet for a match. If there is a match, a list of rooms booked by the user is compiled. If the email address doesn't match, the user is redirected back to the start screen to re-enter their details and try again.

### Cancel Bookings

![cancel_booking](read_me_images/cancel_booking.png)
The cancel booking option uses the "view bookings" function to compile a list of the user's bookings to cancel. Each booking is given a number which the user enter's to confirm they want to cancel that room. The entry is validated to make sure it's an integer and in the list. Then, using a default prices worksheet (a duplicate of the bookings worksheet without any bookings), the app extracts the original prices for the requested cancellation and replaces the "booked" strings in the bookings worksheet before deleting the relevant user data in the user bookings info worksheet. A confimation message is displayed and the user is returned to the main menu.
![cancel_confirm](read_me_images/cancel_confirm.png) 

## Technologies Used

### Python

The whole project is written in Python with the use of libraries and APIs to interact with user input and [Google Sheets](https://www.google.co.uk/sheets/about/).
To make the code a little easier to read, all validator functions were added to a separate file (validate) and imported into the main file (run).

### Regular Expressions (re)

The Regular expressions (re) library was imported to the validator file for use in validator functions to match user inputs against re patterns.

### Datetime (Date)

Date (date) from the datetime library was imported to the validator file to match today's date against user input, and ensure past dates are not entered.

### GSpread (gspread)

GSpread was installed and imported to enable Python to communicate with [Google Sheets](https://www.google.co.uk/sheets/about/).

### Google Oauth2

Credentials was imported from the installed Goole Outh2 to allow Python to access [Google Sheets](https://www.google.co.uk/sheets/about/). 
