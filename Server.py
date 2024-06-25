import logging
import socket
import threading
import sqlite3 
import requests
import time
import re
import os
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Database setup function
def create_database():
    database_path = r"C:\Users\tjbat\Documents\python projects\S.I.M.P\S.I.M.P (Beta)\main\S.I.M.P-Chat\S.I.M.P.db"
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, password)
            VALUES (0, 'admin', 'password'), 
                   (1, 'user1', 'password'), 
                   (2, 'user2', 'password1')
        ''')

        conn.commit()
        logging.info("Database created and initial data inserted.")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"Failed to create a database: {e}")
    finally:
        if conn:
            conn.close()

create_database()

class ChatServer:
    def __init__(self, host, port, db_path):
        self.host = host
        self.port = port
        self.db_path = db_path
        self.clients = {}

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            logging.info(f"Server started, Address: {self.host}, Port: {self.port}")
        except socket.error as e:
            logging.error(f"Socket error: {e}")
            self.server.close()

    def broadcast(self, message):
        for client_socket in self.clients.values():
            try:
                client_socket.send(message.encode())
            except Exception as e:
                logging.error(f"Failed to send message: {e}")

    def handle_client(self, client_socket, client_address):
        logging.info(f"New connection from {client_address}")
        try:
            while True:
                if message := client_socket.recv(1024).decode():
                    logging.debug(f"Received message: {message}")

                    if re.match(r"^LOGIN\s", message):
                        self.handle_login(client_socket, message)
                    elif re.match(r"^SIGNUP\s", message):
                        self.handle_signup(client_socket, message)
                    elif re.match(r"^\\SERVER\s|\\server\s", message):
                        user_message = re.sub(r"^\\SERVER\s|\\server\s", '', message).strip()
                        try:
                            chatbot_response = self.get_chatbot_response(user_message)
                            client_socket.send(f'SERVER: \n{chatbot_response}'.encode())
                        except requests.RequestException as e:
                            logging.error(f"Chatbot request error: {e}")
                            client_socket.send("SERVER: \nChatbot service unavailable.".encode())
                    else:
                        self.broadcast(message)
                else:
                    self.remove_client(client_socket)
                    break
        except socket.error as e:
            logging.error(f"Connection error: {e}")
            self.remove_client(client_socket)
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            self.remove_client(client_socket)

    def get_chatbot_response(self, message):
        try:
            # Set the environment variable for the API key
            os.environ["GEMINI_API_KEY"] = "AIzaSyBFUyEqWF4MCCToqZpQcWP4XT77Mo6LkHI"

            genai.configure(api_key=os.environ["GEMINI_API_KEY"])

            generation_config = {
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 500,
                "response_mime_type": "text/plain",
            }

            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
            )

            chat_session = model.start_chat(
                history=[
                    # Include any previous messages here if maintaining context
                ]
            )

            response = chat_session.send_message(message)
            cleaned_response = self.clean_response(response.text)  # Clean the response here
            return cleaned_response
        except Exception as e:
            logging.error(f"Chatbot error: {e}")
            return "Failed to retrieve data from the chatbot."

    def clean_response(self, response):
        return re.sub(r'\*', '', response)

    def broadcast_user_count(self):
        while True:
            user_count = len(self.clients)
            message = f"USER_COUNT {user_count}"
            for client_socket in self.clients.values():
                try:
                    client_socket.send(message.encode())
                except Exception as e:
                    logging.error(f"Failed to send user count: {e}")
            time.sleep(5)  # Send user count every 5 seconds


    def handle_login(self, client_socket, message):
        try:
            _, username, password = message.split()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username, password FROM users WHERE username=?", (username,))
                if record := cursor.fetchone():
                    db_username, db_password = record
                    if db_password == password:
                        client_socket.send("SUCCESS".encode())
                        self.clients[username] = client_socket
                        logging.info(f"{username} logged in successfully.")
                        self.broadcast(f"SERVER: \n{username} has joined the server.")
                    else:
                        client_socket.send("FAIL".encode())
                else:
                    client_socket.send("USER_NOT_FOUND".encode())
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            client_socket.send("ERROR".encode())
        except Exception as e:
            logging.error(f"Login error: {e}")
            client_socket.send("ERROR".encode())

    def handle_signup(self, client_socket, message):
        try:
            _, username, password = message.split()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username FROM users WHERE username=?", (username,))
                if cursor.fetchone():
                    client_socket.send("USERNAME_EXISTS".encode())
                else:
                    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                    conn.commit()
                    client_socket.send("SUCCESS".encode())
                    logging.info(f"{username} signed up successfully.")
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            client_socket.send("ERROR".encode())
        except Exception as e:
            logging.error(f"Signup error: {e}")
            client_socket.send("ERROR".encode())

    def remove_client(self, client_socket):
        for username, socket in self.clients.items():
            if socket == client_socket:
                del self.clients[username]
                logging.info(f"{username} has left the server.")
                self.broadcast(f"SERVER: \n{username} has left the server.")
                break
        client_socket.close()

    def start(self):
        threading.Thread(target=self.broadcast_user_count, daemon=True).start()
        while True:
            try:
                client_socket, client_address = self.server.accept()
                client_handler = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_handler.start()
            except Exception as e:
                logging.error(f"Failed to accept connection: {e}")

if __name__ == "__main__":
    try:
        server = ChatServer(host='192.168.43.250', port=5555, db_path=r"C:\Users\tjbat\Documents\python projects\S.I.M.P\S.I.M.P (Beta)\main\S.I.M.P-Chat\S.I.M.P.db")
        server.start()
    except Exception as e:
        logging.critical(f"Server startup failed: {e}")
