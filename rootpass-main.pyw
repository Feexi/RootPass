# The imports
import pyperclip
from tkinter import *
import tkinter.messagebox
import customtkinter
import random
import string
import json
import os
import subprocess

# Set the appdata_dir to the actual appdata folder.
APPDATA_DIR = os.path.join(os.getenv("APPDATA"), "RootPass")
# Ensure the directory exists in the appdata, if no create one.
os.makedirs(APPDATA_DIR, exist_ok=True)

# Path to the password file.
PASSWORDS_FILE = os.path.join(APPDATA_DIR, "passwords.json")

# Here we set passwords as our directory.
passwords = {}

def copy_to_clipboard():
    copypassword = entrypassword.get() # Grabs the entered password, sets it to be the same as copypassword which pyperclip uses next.
    pyperclip.copy(copypassword) # Copies the password to the clipboard.

def generate_password():
    length = 16  # Length of the password that's gonna be generated
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    entrypassword.delete(0, END)  # Clear the password entrybox before inserting the randomly generated one.
    entrypassword.insert(0, password)
    entrypassword.configure(state=DISABLED)

def clear_passwords():
    # Clears the passwords from app memory.
    passwords.clear()
    # Delete the JSON file.
    try:
        os.remove(PASSWORDS_FILE)
    except FileNotFoundError:
        pass  # Pass if file not found.

def open_passwords_window():
    passwords_window = customtkinter.CTkToplevel(master=root)
    passwords_window.title("Saved Passwords") # Sets the window title to "Saved Passwords"
    passwords_window.geometry("300x300") # Sets the dimensions for the new window
    passwords_window.attributes('-topmost', True)  # Always on top
    pwbutton = customtkinter.CTkButton(master=passwords_window, text="Clear Passwords", command=clear_passwords)
    pwbutton.place(relx=0.5, rely=0.94, anchor=CENTER)
    
    # Saved passwords go here.
    for app, password in passwords.items():
        label = customtkinter.CTkLabel(master=passwords_window, text=f"{app}: {password}")
        label.pack()

def save_password():
    app_name = entryapp.get()
    password = entrypassword.get()
    passwords[app_name] = password
    save_passwords_to_file()

def switch_theme(root, new_appearance_mode):
    # Switch between light
    if new_appearance_mode == "light":
        customtkinter.set_appearance_mode("light")
    elif new_appearance_mode == "dark":
        customtkinter.set_appearance_mode("dark")

def a_switch_theme():
    switch_theme(root, "dark" if themeswitch.get() else "light")  # Toggle theme based on switch state

def save_passwords_to_file():
    try:
        # Get rid of the hidden atribute temporarily, otherwise program can't write to it.
        subprocess.run(["attrib", "-H", PASSWORDS_FILE], check=True)
        with open(PASSWORDS_FILE, "w") as f:
            json.dump(passwords, f)
        # Put the hidden atribute back on after writing to the file.
    finally:
        subprocess.run(["attrib", "+H", PASSWORDS_FILE], check=True)

def unlock_entry():
    # Unlocks the entry box.
    entrypassword.configure(state=NORMAL)

def save_and_unlock():
    # Saves password using the save_password()
    save_password()
    # Unlocks the entrybox after doing save_password()
    unlock_entry()

def load_passwords_from_file():
    try:
        with open(PASSWORDS_FILE, "r") as f:
            # Updates the password list from the contents of the json file.
            passwords.update(json.load(f))
    except FileNotFoundError:
        tkinter.messagebox.showinfo("File Not Found", "File containing passwords wasn't found. The password database is empty.")

# Set the default theme.
customtkinter.set_appearance_mode("light")
# Set the default color scheme.
customtkinter.set_default_color_theme("green")

# Creating the CTK window
root = customtkinter.CTk()
# Setting the title for our window
root.title("RootPass")
# Setting window width & height
root.geometry("400x500")

# Setting up the icon
root.iconbitmap('rootpass.ico')

# Buttons, switches and entryboxes go here.
copyrightlabel = customtkinter.CTkLabel(master=root, text="RootPass™ 2024")
themeswitch = customtkinter.CTkSwitch(master=root, text="Theme", command=a_switch_theme)
entryapp = customtkinter.CTkEntry(master=root, width=280, placeholder_text="Enter App:")
entrypassword = customtkinter.CTkEntry(master=root, width=280, placeholder_text="Enter Password:")
buttonsave = customtkinter.CTkButton(master=root, width=180, text="Save Password", command=save_and_unlock)
buttongenerate = customtkinter.CTkButton(master=root, width=180, text="Generate Password", command=generate_password)
buttoncopy = customtkinter.CTkButton(master=root, width=160, text="Copy Password", command=copy_to_clipboard)
buttonshowpasswords = customtkinter.CTkButton(master=root, width=160, text="Show Passwords", command=open_passwords_window)

# Placing the actual buttons, switches and entryboxes with all sorts of coordinates.
copyrightlabel.place(relx=0.85, rely=0.98, anchor=S)
themeswitch.place(relx=0.15, rely=0.98, anchor=S)
entryapp.place(relx=0.5, rely=0.09, anchor=S)
entrypassword.place(relx=0.5, rely=0.16, anchor=S)
buttongenerate.place(relx=0.5, rely=0.18, anchor=N)
buttoncopy.place(relx=0.5, rely=0.85, anchor=N)
buttonshowpasswords.place(relx=0.5, rely=0.92, anchor=N)
buttonsave.place(relx=0.5, rely=0.25, anchor=N)

# Load passwords from file when the application starts
load_passwords_from_file()

# Running the app 
root.mainloop()
