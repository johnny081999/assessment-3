'''Hospital Appointment Booking System

This program allows the patients to manage their appointments
with a menu-driven interface. The user can create a new appointment,
cancel an existing appointment, view appointments and reschedule
appointments.
'''

import json
import os
from datetime import datetime

APPOINTMENTS_FILE = "appointments.json"

# List of doctors. Each doctor is a dictionary that contains a
# dictionary of available times, keyed by date.
doctors = [
    {
        "name": "Dr. Smith",
        "specialty": "Cardiology",
        "available_times": {
            "2026-09-22": ["09:00", "09:30", "10:00"],
            "2026-09-23": ["11:00", "11:30"]
        }
    },
    {
        "name": "Dr. Lee",
        "specialty": "Dermatology",
        "available_times": {
            "2026-09-22": ["14:00", "14:30"],
            "2026-09-24": ["09:00", "09:30", "10:00"]
        }
    },
    {
        "name": "Dr. Patel",
        "specialty": "General Practice",
        "available_times": {
            "2026-09-22": ["08:00", "08:30", "09:00"],
            "2026-09-23": ["13:00", "13:30"]
        }
    }
]

appointments = []  # loaded from / saved to APPOINTMENTS_FILE
next_id = 1 #To use for appointment ID

main_menu_display = """
Choose an option:
    1.Book Appointment
    2.Cancel Appointment
    3.View Appointment
    4.Reschedule Appointment
    5.Exit
"""


# ---------- File handling ----------

def load_appointments():
    global appointments, next_id
    #Error handling if the file does not exist
    if not os.path.exists(APPOINTMENTS_FILE):
        print("No appointments file found yet.")
        return

    try:
        #Read the appointment file
        with open(APPOINTMENTS_FILE, "r") as file:
            appointments = json.load(file)
        if appointments:
            #Get new appointment ID
            next_id = max(a["id"] for a in appointments) + 1
    except (IOError, json.JSONDecodeError):
        #The file is not available to read
        print("Could not read the appointments file.")


def save_appointments():
    #Write all appointments back to the JSON file.
    with open(APPOINTMENTS_FILE, "w") as file:
        json.dump(appointments, file, indent=2)


# ---------- Helper functions ----------

#Get the doctor name
def find_doctor(name):
    for doctor in doctors:
        if doctor["name"].lower() == name.lower():
            return doctor
    return None

#Get appointment by ID
def get_appointment_by_id(appointment_id):
    for a in appointments:
        if a["id"] == appointment_id:
            return a
    return None


def build_all_slots():
    """
    Build one flat, numbered list combining every doctor with every one
    of their free date/time slots.
    This lets the patient pick a single number instead of typing a
    doctor name, a date and a time separately.
    """
    slots = []
    for doctor in doctors:
        for date, times in doctor["available_times"].items():
            for time in times:
                slots.append({"doctor": doctor, "date": date, "time": time})
    return slots


def show_all_slots(slots):
    print("\nAvailable appointment slots:")
    for i, slot in enumerate(slots, start=1):
        doctor = slot["doctor"]
        print(f'{i}. {doctor["name"]} ({doctor["specialty"]}) - {slot["date"]} {slot["time"]}')


def build_doctor_slots(doctor):
    #Same idea as build_all_slots(), but only for one doctor.
    slots = []
    for date, times in doctor["available_times"].items():
        for time in times:
            slots.append({"date": date, "time": time})
    return slots


def show_doctor_slots(slots):
    print("\nAvailable times:")
    for i, slot in enumerate(slots, start=1):
        print(f'{i}. {slot["date"]} {slot["time"]}')


def block_time(doctor, date, time):
    #Remove a time from the doctor's available times (mark as booked).
    doctor["available_times"][date].remove(time)


def unblock_time(doctor, date, time):
    #Add a time back to the doctor's available times (mark as free).
    doctor["available_times"].setdefault(date, [])
    doctor["available_times"][date].append(time)


# ---------- Core features ----------

def book_appointment():
    global next_id
    print("\n-- Book appointment --")

    slots = build_all_slots()
    if not slots:
        print("There are no available slots right now.")
        return

    show_all_slots(slots)

    try:
        choice = int(input("\nChoose a slot (number): "))
        if choice < 1 or choice > len(slots):
            raise ValueError("There is no slot with that number.")

        chosen = slots[choice - 1]
        doctor = chosen["doctor"]
        date = chosen["date"]
        time = chosen["time"]

        patient_name = input("Patient name: ").strip()
        if patient_name == "":
            raise ValueError("Patient name cannot be empty.")

        # Block the time slot so it cannot be double booked
        block_time(doctor, date, time)

        appointment = {
            "id": next_id,
            "patient": patient_name,
            "doctor": doctor["name"],
            "date": date,
            "time": time,
            "status": "booked",
            "created_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        appointments.append(appointment)
        save_appointments()
        print(f"Appointment #{next_id} booked.")
        next_id += 1

    except ValueError as e:
        print(f"Could not book appointment: {e}")


def cancel_appointment():
    print("\n-- Cancel appointment --")
    try:
        appointment_id = int(input("Enter appointment id: "))
        appointment = get_appointment_by_id(appointment_id)

        if appointment is None or appointment["status"] != "booked":
            raise ValueError("No active appointment found with that id.")

        appointment["status"] = "cancelled"

        # Unblock the time slot so someone else can book it
        doctor = find_doctor(appointment["doctor"])
        if doctor is not None:
            unblock_time(doctor, appointment["date"], appointment["time"])

        save_appointments()
        print("Appointment cancelled.")

    except ValueError as e:
        print(f"Could not cancel appointment: {e}")


def view_appointment():
    """
    Shows every appointment stored in appointments.json, including
    cancelled ones, ordered as they were created. Since everything is
    kept in the same file.
    """
    print("\n-- All appointments --")
    if not appointments:
        print("No appointments yet.")
        return

    for a in appointments:
        print(f'#{a["id"]} | {a["patient"]} | {a["doctor"]} | {a["date"]} {a["time"]} | {a["status"]} | Created on: {a["created_on"]}')


def reschedule_appointment():
    print("\n-- Reschedule appointment --")
    try:
        appointment_id = int(input("Enter appointment id: "))
        appointment = get_appointment_by_id(appointment_id)

        if appointment is None or appointment["status"] != "booked":
            raise ValueError("No active appointment found with that id.")

        doctor = find_doctor(appointment["doctor"])
        if doctor is None:
            raise ValueError("Doctor for this appointment no longer exists.")

        slots = build_doctor_slots(doctor)
        if not slots:
            raise ValueError("This doctor has no available slots to reschedule into.")

        show_doctor_slots(slots)
        choice = int(input("\nChoose a new slot (number): "))
        if choice < 1 or choice > len(slots):
            raise ValueError("There is no slot with that number.")

        chosen = slots[choice - 1]
        new_date = chosen["date"]
        new_time = chosen["time"]

        old_date, old_time = appointment["date"], appointment["time"]

        # Unblock the old slot, block the new one
        unblock_time(doctor, old_date, old_time)
        block_time(doctor, new_date, new_time)

        appointment["date"] = new_date
        appointment["time"] = new_time

        save_appointments()
        print("Appointment rescheduled.")

    except ValueError as e:
        print(f"Could not reschedule appointment: {e}")


# main menu
def main():
    load_appointments()

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

#The JSON file is removed to avoid duplicated appointments
if os.path.exists(APPOINTMENTS_FILE):
    os.remove("appointments.json")
# execute main menu
main()
