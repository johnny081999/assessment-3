"""Hospital Appointment Booking System"""

import datetime

main_menu_display = """
Choose an option:
    1.Book Appointment
    2.Cancel Appointment
    3.View Appointment
    4.Reschedule Appointment
    5.Exit
"""

def book_appointment():
    ...

def cancel_appointment():
    ...

def view_appointment():
    ...

def reschedule_appointment():
    ...


# main menu
def main():
    tickets = []

    # print Main Menu
    print(main_menu_display)
    # dont cast to int(), as non integer input will cause exception
    choice = input("Your choice: ")  # choice that user entered

    # loop until 5.Exit is chosen by user
    while choice != "5":
        # 1.Book Appointment
        if choice == "1":
           book_appointment()
        # 2.Cancel Appointment
        elif choice == "2":
            cancel_appointment()
        # 3.View Appointment
        elif choice == "3":
            view_appointment()
        # 4.Reschedule Appointment
        elif choice == "4":
            reschedule_appointment()
        else:
            print("Invalid choice:" + choice + ". Please enter a number from 1 to 5")

        # print Main Menu
        print(main_menu_display)

        choice = input("Your choice: ")

# execute main manu
main()