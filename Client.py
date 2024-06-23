import socket  # For creating and managing network connections
import threading  # For running tasks concurrently
import tkinter as tk  # For the graphical user interface
from tkinter import messagebox
from customtkinter import *  # For a customized and modern look to the tkinter GUI
import logging
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ChatClient:
    def __init__(self, host, port):
        self.host = host  # Server hostname or IP address
        self.port = port  # Server port number
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creating a TCP socket
        self.gui_done = False  # Flag to check if the GUI is fully set up
        self.running = True  # Flag to keep the client running
        self.client_username = None  # Store the username after login
        self.connection_time = None
        self.online_duration_thread = None


        self.login_window()  # Start the GUI with the login window

    def login_window(self):
        self.root = CTk()  # Creating the main application window
        self.root.geometry("400x400")  # Setting the window size
        self.root.title("S.I.M.P Login")  # Setting the window title

        self.frame = CTkFrame(self.root)  # Frame to contain all widgets in the login window
        self.frame.pack(pady=20, padx=60, fill="both", expand=True)

        self.label = CTkLabel(self.frame, text="Login")  # Label for the login title
        self.label.pack(pady=12, padx=10)

        self.entry_username = CTkEntry(self.frame, placeholder_text="Username")  # Entry field for the username
        self.entry_username.pack(pady=12, padx=10)

        self.entry_password = CTkEntry(self.frame, placeholder_text="Password", show="*")  # Entry field for the password
        self.entry_password.pack(pady=12, padx=10)

        self.show_password_var = CTkCheckBox(self.frame, text="Show Password", command=self.toggle_password)  # Checkbox to toggle password visibility
        self.show_password_var.pack(pady=12, padx=10)

        self.button_login = CTkButton(self.frame, text="Login", command=self.login)  # Button to login
        self.button_login.pack(pady=12, padx=10)

        self.button_signup = CTkButton(self.frame, text="Sign Up", command=self.signup_window)  # Button to switch to the signup window
        self.button_signup.pack(pady=12, padx=10)

        self.message_label = CTkLabel(self.frame, text="", font=("Arial", 14))  # Label to show login status messages
        self.message_label.pack(pady=12, padx=10)

        self.root.mainloop()  # Start the main event loop

    def signup_window(self):
        self.frame.destroy()  # Destroy the current frame (login frame)
        self.frame = CTkFrame(self.root)  # Create a new frame for the signup window
        self.frame.pack(pady=20, padx=60, fill="both", expand=True)

        self.label = CTkLabel(self.frame, text="Sign Up")  # Label for the signup title
        self.label.pack(pady=12, padx=10)

        self.entry_username = CTkEntry(self.frame, placeholder_text="Username")  # Entry field for the username
        self.entry_username.pack(pady=12, padx=10)

        self.entry_password = CTkEntry(self.frame, placeholder_text="Password", show="*")  # Entry field for the password
        self.entry_password.pack(pady=12, padx=10)

        self.show_password_var = CTkCheckBox(self.frame, text="Show Password", command=self.toggle_password)  # Checkbox to toggle password visibility
        self.show_password_var.pack(pady=12, padx=10)

        self.button_signup = CTkButton(self.frame, text="Sign Up", command=self.signup)  # Button to sign up
        self.button_signup.pack(pady=12, padx=10)

        self.button_back = CTkButton(self.frame, text="Back to Login", command=self.back_to_login)  # Button to go back to the login window
        self.button_back.pack(pady=12, padx=10)

        self.message_label = CTkLabel(self.frame, text="", font=("Arial", 14))  # Label to show signup status messages
        self.message_label.pack(pady=12, padx=10)

    def back_to_login(self):
        self.frame.destroy()  # Destroy the current frame (signup frame)
        self.login_window()  # Recreate the login window

    def toggle_password(self):
        if self.entry_password.cget("show") == "*":
            self.entry_password.configure(show="")
        else:
            self.entry_password.configure(show="*")

    def login(self):
        username = self.entry_username.get().lower().strip()
        password = self.entry_password.get().strip()
        if username and password:
            try:
                self.client_socket.connect((self.host, self.port))
                self.client_socket.send(f"LOGIN {username} {password}".encode())
                response = self.client_socket.recv(1024).decode()
                if response == "SUCCESS":
                    self.client_username = username
                    self.connection_time = time.time()  # Set connection time
                    self.open_chat_room()
                elif response == "FAIL":
                    self.message_label.configure(text="Password incorrect")
                    self._reset_socket()
                elif response == "USER_NOT_FOUND":
                    self.message_label.configure(text="Account Not found")
                    self._reset_socket()
            except Exception as e:
                self.message_label.configure(text="Connection error: Unable to communicate with server")
                self._reset_socket()
                logging.error(f'Connection Failed: {e}')
        else:
            self.message_label.configure(text="Please enter both username and password.")

    def signup(self):
        username = self.entry_username.get().lower().strip()
        password = self.entry_password.get().strip()
        if username and password:
            try:
                self.client_socket.connect((self.host, self.port))
                self.client_socket.send(f"SIGNUP {username} {password}".encode())
                response = self.client_socket.recv(1024).decode()
                if response == "SUCCESS":
                    self.message_label.configure(text="Account created successfully. Please log in.")
                    self.connection_time = time.time()  # Set connection time
                    self._reset_socket()
                    self.back_to_login()
                elif response == "USERNAME_EXISTS":
                    self.message_label.configure(text="Username already exists")
                    self._reset_socket()
            except Exception as e:
                self.message_label.configure(text="Connection error: Unable to communicate with server")
                self._reset_socket()
                logging.error(f'Connection Failed: {e}')
        else:
            self.message_label.configure(text="Please enter both username and password.")

    def open_chat_room(self):
        self.gui_done = True  # Set the GUI done flag
        self.root.destroy()  # Close the login window

        self.chat_window = CTk()  # Create the main chat window
        self.chat_window.geometry("800x600")  # Set the window size
        self.chat_window.title("S.I.M.P Chat Room")  # Set the window title

        self.tabview = CTkTabview(self.chat_window)  # Create a tabbed interface with "Chat" and "Settings" tabs
        self.tabview.pack(pady=20, padx=20, fill="both", expand=True)

        self.tab_chat = self.tabview.add("Chat")  # Add the "Chat" tab
        self.tab_settings = self.tabview.add("Settings")  # Add the "Settings" tab

        self.chat_frame = CTkScrollableFrame(self.tab_chat)  # Create a scrollable frame within the "Chat" tab
        self.chat_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        self.entry_message = CTkEntry(self.tab_chat, placeholder_text=r"Type your message here... '\SERVER' to communicate with the server ")
        self.entry_message.pack(pady=12, padx=10, side="left", fill="x", expand=True)

        self.button_send = CTkButton(self.tab_chat, text="Send", command=self.send_message)
        self.button_send.pack(pady=12, padx=10, side="right")

        self.info_frame = CTkFrame(self.tab_settings)  # Create a frame for the information bar
        self.info_frame.pack(pady=12, padx=10, fill="x")

        # Server address and port
        self.server_info_label = CTkLabel(self.info_frame, text=f"Connected to: {self.host}:{self.port}")
        self.server_info_label.pack(anchor="w")

        # Number of connected users
        self.user_count_label = CTkLabel(self.info_frame, text="Connected users: N/A")
        self.user_count_label.pack(anchor="w")

        # Connection time
        self.connection_time_label = CTkLabel(self.info_frame, text="Connection time: N/A")
        self.connection_time_label.pack(anchor="w")

        # Online duration
        self.online_duration_label = CTkLabel(self.info_frame, text="Online duration: N/A")
        self.online_duration_label.pack(anchor="w")

        # Active status
        self.active_status_label = CTkLabel(self.info_frame, text="Active status: Disconnected")
        self.active_status_label.pack(anchor="w")

        # Settings tab widgets
        self.appearance_mode_optionmenu = CTkOptionMenu(self.tab_settings, values=["Dark", "Light", "System"], command=self.change_appearance_mode)
        self.appearance_mode_optionmenu.pack(pady=12, padx=10)

        self.scaling_optionmenu = CTkOptionMenu(self.tab_settings, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling)
        self.scaling_optionmenu.pack(pady=12, padx=10)

        self.theme_optionmenu = CTkOptionMenu(self.tab_settings, values=["blue", "green", "dark-blue"], command=self.change_theme)
        self.theme_optionmenu.pack(pady=12, padx=10)

        self.enter_key_behavior = tk.StringVar(value="Normal")
        self.enter_key_optionmenu = CTkOptionMenu(self.tab_settings, values=["Normal", "Send Message"], command=self.change_enter_key_behavior)
        self.enter_key_optionmenu.pack(pady=12, padx=10)

        self.entry_message.bind('<Return>', self.on_enter_key)  # Bind the Enter key to a function
        self.entry_message.bind('<Shift-Return>', self.on_shift_enter_key)  # Bind Shift+Enter key to a function

        threading.Thread(target=self.receive_messages, daemon=True).start()  # Start a thread to receive messages

        self.chat_window.mainloop()  # Start the main event loop for the chat window

    def change_enter_key_behavior(self, choice):
        self.enter_key_behavior.set(choice)  # Set the behavior for the Enter key

    def on_enter_key(self, event):
        if self.enter_key_behavior.get() == "Send Message":
            self.send_message()  # Send the message if Enter key behavior is set to "Send Message"
            return "break"  # Prevent the default behavior (moving to the next line)

    def on_shift_enter_key(self, event):
        self.entry_message.insert(tk.INSERT, '\n')
        return "break"  # Prevent the default behavior

    def change_theme(self, theme):
        set_default_color_theme(theme)  # Change the theme of the application

    def change_appearance_mode(self, mode):
        set_appearance_mode(mode)  # Change the appearance mode (dark, light, system)

    def change_scaling(self, scaling):
        set_widget_scaling(int(scaling.replace("%", "")) / 100)  # Change the scaling of the widgets

    def create_chat_bubble(self, message, sender_type):
        message_with_sender = message.strip()

        if sender_type == "self":
            bg_color = "#0078D7"  # Blue for sent messages
            brd_color = bg_color
            text_color = "#FFFFFF"  # White text for better readability
            sticky_side = 'e'  # Right side
        elif sender_type == "server":
            bg_color = "#FFFFFF"  # White for received messages
            brd_color = "#F2F2F2"  # Grey for received messages
            text_color = "#000000"  # Black text for better readability
            sticky_side = 'w'  # Left side
        else:
            bg_color = "#F2F2F2"  # Grey for received messages
            brd_color = bg_color  # Grey for received messages
            text_color = "#000000"  # Black text for better readability
            sticky_side = 'w'  # Left side

        bubble_frame = CTkFrame(self.chat_frame, corner_radius=15, fg_color=brd_color, width=600)
        bubble_frame.grid(sticky=sticky_side, padx=5, pady=5)

        bubble = CTkLabel(
            bubble_frame,
            text=message_with_sender.strip('"'),
            justify="left",
            fg_color=bg_color,
            text_color=text_color,
            wraplength=500,  # Set the wrap length for the message text

        )
        bubble.pack(fill='both', padx=10, pady=10)

    def send_message(self):
        message = self.entry_message.get().strip()  # Get the message from the entry field
        if message:  # Check if there is a message to send
            try:
                if message.startswith(r"\SERVER") or message.startswith(r"\server"):
                    self.client_socket.send(message.encode())  # Send server commands directly
                    self.create_chat_bubble(message.strip(), "self")  # Display the sent message
                else:
                    full_message = f'{self.client_username}: \n"{message}"'  # Format the message
                    self.client_socket.send(full_message.encode())  # Send the message to the server
                    self.create_chat_bubble(message.strip('"'), "self")  # Display the sent message
                self.entry_message.delete(0, tk.END)  # Clear the entry field
            except Exception as e:
                logging.error(f"Send message error: {e}")
        else:
            messagebox.showwarning("Warning", "You cannot send an empty message!")

    def receive_messages(self):
        while self.running:  # Keep running while the client is active
            try:
                message = self.client_socket.recv(1024).decode()  # Receive messages from the server
                if not message.startswith(f'{self.client_username}: '):  # Ignore self messages
                    if message.startswith('server: ') :
                        self.create_chat_bubble(message.replace('server: ', ''), "server")  # Display server messages
                    else:
                        self.create_chat_bubble(message, "other")  # Display messages from other users
            except ConnectionAbortedError:
                break
            except Exception as e:
                logging.error(f"Receive error: {e}")
                break

    def _reset_socket(self):
        self.client_socket.close()  # Close the socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Recreate the socket

if __name__ == "__main__":
    client = ChatClient(host='192.168.43.250', port=5555)  # Create an instance of ChatClient with server details
