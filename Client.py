import socket
import threading
import tkinter as tk
from tkinter import messagebox
from customtkinter import *
import logging
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gui_done = False
        self.running = True
        self.client_username = None
        self.connection_time = None
        self.online_duration_thread = None

        self.root = CTk()
        self.active_status = tk.StringVar(value="Connected")

        self.login_window()

    def login_window(self):
        self.root.geometry("400x400")
        self.root.title("S.I.M.P Login")

        self.frame = CTkFrame(self.root)
        self.frame.pack(pady=20, padx=60, fill="both", expand=True)

        self.label = CTkLabel(self.frame, text="Login")
        self.label.pack(pady=12, padx=10)

        self.entry_username = CTkEntry(self.frame, placeholder_text="Username")
        self.entry_username.pack(pady=12, padx=10)

        self.entry_password = CTkEntry(self.frame, placeholder_text="Password", show="*")
        self.entry_password.pack(pady=12, padx=10)

        self.show_password_var = CTkCheckBox(self.frame, text="Show Password", command=self.toggle_password)
        self.show_password_var.pack(pady=12, padx=10)

        self.button_login = CTkButton(self.frame, text="Login", command=self.login)
        self.button_login.pack(pady=12, padx=10)

        self.button_signup = CTkButton(self.frame, text="Sign Up", command=self.signup_window)
        self.button_signup.pack(pady=12, padx=10)

        self.message_label = CTkLabel(self.frame, text="", font=("Arial", 14))
        self.message_label.pack(pady=12, padx=10)

        self.root.mainloop()

    def signup_window(self):
        self.frame.destroy()
        self.frame = CTkFrame(self.root)
        self.frame.pack(pady=20, padx=60, fill="both", expand=True)

        self.label = CTkLabel(self.frame, text="Sign Up")
        self.label.pack(pady=12, padx=10)

        self.entry_username = CTkEntry(self.frame, placeholder_text="Username")
        self.entry_username.pack(pady=12, padx=10)

        self.entry_password = CTkEntry(self.frame, placeholder_text="Password", show="*")
        self.entry_password.pack(pady=12, padx=10)

        self.show_password_var = CTkCheckBox(self.frame, text="Show Password", command=self.toggle_password)
        self.show_password_var.pack(pady=12, padx=10)

        self.button_signup = CTkButton(self.frame, text="Sign Up", command=self.signup)
        self.button_signup.pack(pady=12, padx=10)

        self.button_back = CTkButton(self.frame, text="Back to Login", command=self.back_to_login)
        self.button_back.pack(pady=12, padx=10)

        self.message_label = CTkLabel(self.frame, text="", font=("Arial", 14))
        self.message_label.pack(pady=12, padx=10)

    def back_to_login(self):
        self.frame.destroy()
        self.login_window()

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
                    self.connection_time = time.time()
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
                    self.connection_time = time.time()
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
        self.gui_done = True
        self.root.destroy()

        self.chat_window = CTk()
        self.chat_window.geometry("800x600")
        self.chat_window.title("S.I.M.P Chat Room")

        self.tabview = CTkTabview(self.chat_window)
        self.tabview.pack(pady=20, padx=20, fill="both", expand=True)

        self.tab_chat = self.tabview.add("Chat")
        self.tab_settings = self.tabview.add("Settings")

        self.chat_frame = CTkScrollableFrame(self.tab_chat)
        self.chat_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        self.entry_message = CTkEntry(self.tab_chat, placeholder_text=r"Type your message here... '\SERVER' to communicate with the server ")
        self.entry_message.pack(pady=12, padx=10, side="left", fill="x", expand=True)

        self.button_send = CTkButton(self.tab_chat, text="Send", command=self.send_message)
        self.button_send.pack(pady=12, padx=10, side="right")

        self.settings_frame = CTkScrollableFrame(self.tab_settings)
        self.settings_frame.pack(pady=12, padx=10, fill="both", expand=True)
        self.settings_frame.grid_columnconfigure(0, weight=1)

        self.server_info_label = CTkLabel(self.settings_frame, text=f"Connected to: {self.host}     :{self.port}")
        self.server_info_label.pack(anchor="w")

        self.user_count_label = CTkLabel(self.settings_frame, text="Connected users: N/A")
        self.user_count_label.pack(anchor="w")

        # Active status
        self.active_status_label = CTkLabel(self.settings_frame, text= f"Active status: {self.active_status.get()}")
        self.active_status_label.pack(anchor="w")

        self.online_duration_label = CTkLabel(self.settings_frame, text="Online duration: N/A")
        self.online_duration_label.pack(anchor="w")

        self.reconnect_button = CTkButton(self.settings_frame, text="Reconnect", command=self.reconnect)
        self.reconnect_button.pack(pady=12, padx=10)

        self.appearance_mode_label = CTkLabel(self.settings_frame, text="Appearance Mode")
        self.appearance_mode_label.pack(pady=12, padx=10)

        self.appearance_mode_optionmenu = CTkOptionMenu(self.settings_frame, values=["Dark", "Light", "System"], command=self.change_appearance_mode)
        self.appearance_mode_optionmenu.pack(pady=12, padx=10)

        self.scaling_label = CTkLabel(self.settings_frame, text="Scaling")
        self.scaling_label.pack(pady=12, padx=10)

        self.scaling_optionmenu = CTkOptionMenu(self.settings_frame, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling)
        self.scaling_optionmenu.pack(pady=12, padx=10)

        self.theme_label = CTkLabel(self.settings_frame, text="Theme")
        self.theme_label.pack(pady=12, padx=10)

        self.theme_optionmenu = CTkOptionMenu(self.settings_frame, values=["blue", "green", "dark-blue"], command=self.change_theme)
        self.theme_optionmenu.pack(pady=12, padx=10)

        self.enter_key_behavior_label = CTkLabel(self.settings_frame, text="Enter Key Behavior")
        self.enter_key_behavior_label.pack(pady=12, padx=10)

        self.enter_key_behavior = tk.StringVar(value="Normal")
        self.enter_key_optionmenu = CTkOptionMenu(self.settings_frame, values=["Normal", "Send Message"], command=self.change_enter_key_behavior)
        self.enter_key_optionmenu.pack(pady=12, padx=10)

        self.entry_message.bind('<Return>', self.on_enter_key)

        self.online_duration_thread = threading.Thread(target=self.update_info_bar, daemon=True)
        self.online_duration_thread.start()

        threading.Thread(target=self.receive_messages, daemon=True).start()

        self.chat_window.mainloop()

    def change_enter_key_behavior(self, choice):
        self.enter_key_behavior.set(choice)

    def on_enter_key(self, event):
        if self.enter_key_behavior.get() == "Send Message":
            self.send_message()
            return "break"

    def change_theme(self, theme):
        set_default_color_theme(theme)

    def change_appearance_mode(self, mode):
        set_appearance_mode(mode)

    def change_scaling(self, scaling):
        set_widget_scaling(int(scaling.replace("%", "")) / 100)

    def create_chat_bubble(self, message, sender_type):
        message_with_sender = message.strip()

        if sender_type == "self":
            bg_color = "#0078D7"
            brd_color = bg_color
            text_color = "#FFFFFF"
            sticky_side = 'e'
        elif sender_type == "server":
            bg_color = "#FFFFFF"
            brd_color = "#F2F2F2"
            text_color = "#000000"
            sticky_side = 'w'
        else:
            bg_color = "#F2F2F2"
            brd_color = bg_color
            text_color = "#000000"
            sticky_side = 'w'

        bubble_frame = CTkFrame(self.chat_frame, corner_radius=15, fg_color=brd_color, width=600)
        bubble_frame.grid(sticky=sticky_side, padx=5, pady=5)

        bubble = CTkLabel(
            bubble_frame,
            text=message_with_sender.strip('"'),
            justify="left",
            fg_color=bg_color,
            text_color=text_color,
            wraplength=500,
        )
        bubble.pack(fill='both', padx=10, pady=10)

    def send_message(self):
        message = self.entry_message.get().strip()
        if message:
            try:
                if message.startswith(r"\SERVER") or message.startswith(r"\server"):
                    self.client_socket.send(message.encode())
                    self.create_chat_bubble(message.strip(), "self")
                else:
                    full_message = f'USER_MESSAGE {self.client_username}: \n{message}'
                    self.client_socket.send(full_message.encode())
                    self.create_chat_bubble(message.strip(), "self")
                self.entry_message.delete(0, tk.END)
            except Exception as e:
                logging.error(f"Send message error: {e}")
                if self.active_status.get() == "Disconnected":
                    messagebox.showerror("Error", "You are disconnected from the server.")
        else:
            messagebox.showwarning("Warning", "You cannot send an empty message!")

    def receive_messages(self):
        while self.running:
            try:
                message = self.client_socket.recv(1024).decode()
                if message.startswith("USER_COUNT"):
                    user_count = message.split()[1]
                    self.user_count_label.configure(text=f"Connected users: {user_count}")
                elif message.startswith('SERVER: '):
                        self.create_chat_bubble(message, "server")
                elif message.startswith('USER_MESSAGE'):
                    message = message.replace('USER_MESSAGE', '').strip()
                    if not message.startswith(self.client_username):
                        self.create_chat_bubble(message, "other")
                else:
                    self.create_chat_bubble(message, "other")
            except ConnectionAbortedError:
                break
            except Exception as e:
                logging.error(f"Receive error: {e}")
                self.active_status.set("Disconnected")
                break

    def update_info_bar(self):
        while self.running:
            if self.connection_time:
                elapsed_time = int(time.time() - self.connection_time)
                hours, minutes = divmod(elapsed_time // 60, 60)
                seconds = elapsed_time % 60
                self.online_duration_label.configure(text=f"Online duration: {hours}h {minutes}m {seconds}s")
                self.active_status_label.configure(text=f"Active status: {self.active_status.get()}")
            else:
                self.active_status_label.configure(text="Active status: Disconnected")
            time.sleep(1)

    def reconnect(self):
        attempts = 5
        for attempt in range(attempts):
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.host, self.port))
                self.connection_time = time.time()
                self.active_status.set("Connected")
                messagebox.showinfo("Success", "Reconnected to the server.")
                
                # Start listening for messages again after reconnecting
                threading.Thread(target=self.receive_messages, daemon=True).start()
                return
            except Exception as e:
                logging.error(f"Reconnect attempt {attempt + 1} failed: {e}")
                time.sleep(1)
        messagebox.showerror("Error", "Failed to reconnect to the server.")
        self._reset_socket()

    def _reset_socket(self):
        self.client_socket.close()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if __name__ == "__main__":
    client = ChatClient(host='192.168.43.250', port=5555)
