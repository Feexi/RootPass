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
from cryptography.fernet import Fernet

# Set the appdata_dir to the actual appdata folder.
APPDATA_DIR = os.path.join(os.getenv("APPDATA"), "RootPass")
# Ensure the directory exists in the appdata, if no create one.
os.makedirs(APPDATA_DIR, exist_ok=True)

# Path to the password file.
PASSWORDS_FILE = os.path.join(APPDATA_DIR, "passwords.json")

# Here we set passwords as our directory.
passwords = {}

# Generate a secret key for encryption
def generate_key():
    return Fernet.generate_key()

# Encrypt a password
def encrypt_password(password, key):
    cipher_suite = Fernet(key)
    return cipher_suite.encrypt(password.encode()).decode()

# Decrypt a password
def decrypt_password(encrypted_password, key):
    cipher_suite = Fernet(key)
    return cipher_suite.decrypt(encrypted_password.encode()).decode()

# Update save_passwords_to_file function to encrypt passwords before saving
def save_passwords_to_file():
    try:
        key = generate_key()  # Generate a new key each time you save passwords
        subprocess.run(["attrib", "-H", PASSWORDS_FILE], check=True)  # Temporarily remove the hidden attribute
        with open(PASSWORDS_FILE, "wb") as f:  # Open in binary mode
            encrypted_passwords = {app: encrypt_password(password, key) for app, password in passwords.items()}
            f.write(key + b'\n')  # Write the key directly and add a newline for separation
            f.write(json.dumps(encrypted_passwords).encode())  # Encode the JSON string to bytes
    finally:
        subprocess.run(["attrib", "+H", PASSWORDS_FILE], check=True)  # Restore the hidden attribute

# Update load_passwords_from_file function to decrypt passwords after loading
def load_passwords_from_file():
    try:
        with open(PASSWORDS_FILE, "rb") as f:  # Open in binary mode
            key = f.readline().rstrip(b'\r\n')  # Read the key and strip newline characters
            if key:
                encrypted_data = f.read()  # Read the rest of the file
                encrypted_passwords = json.loads(encrypted_data.decode())  # Decode and load the JSON
                passwords.update({app: decrypt_password(encrypted_password, key) for app, encrypted_password in encrypted_passwords.items()})
            else:
                tkinter.messagebox.showinfo("Key Not Found", "Secret key for decryption not found.")
    except FileNotFoundError:
        tkinter.messagebox.showinfo("File Not Found", "File containing passwords wasn't found. The password database is empty.")

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
    passwords_window.iconbitmap("rootpass.ico")
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
        with open(PASSWORDS_FILE, "rb") as f:  # Open in binary mode
            key = f.readline().rstrip(b'\r\n')  # Read the key and strip newline characters
            if key:
                encrypted_data = f.read()  # Read the rest of the file
                encrypted_passwords_start = encrypted_data.find(b'\n') + 1  # Find the start of encrypted passwords
                encrypted_passwords = encrypted_data[encrypted_passwords_start:]  # Extract encrypted passwords
                encrypted_passwords = json.loads(encrypted_passwords.decode())  # Decode and load the JSON
                passwords.update({app: decrypt_password(encrypted_password, key) for app, encrypted_password in encrypted_passwords.items()})
            else:
                tkinter.messagebox.showinfo("Key Not Found", "Secret key for decryption not found.")
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
