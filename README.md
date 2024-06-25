# S.I.M.P Chat Application

A comprehensive chat application built using Python, SQLite, and Tkinter for the GUI. This application supports user login, signup, and real-time messaging with other connected users. It also integrates with a generative AI model for chatbot responses.

## Features

- User login and signup
- Real-time messaging between users
- Integration with generative AI for chatbot responses
- Graphical User Interface (GUI) using customtkinter
- SQLite database for user management
- Error handling for robust network communication

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Required Python libraries: `socket`, `threading`, `sqlite3`, `requests`, `time`, `re`, `os`, `customtkinter`, `logging`, `tkinter`

### Installation

1. Install the required libraries:


pip install requests customtkinter google-generativeai


4. Set up the database:

In server.py replace the database path in the 'create_database' function and the server instance init

This will create the necessary database and tables.

### Running the Application

#### Server

1. Open a terminal and navigate to the project directory.
2. Run the server script:

python server.py

The server will start listening for incoming connections.

#### Client

1. Open a terminal and navigate to the project directory.
2. Run the client script:

python client.py

The client application will start, and the login window will be displayed.

## Detailed Explanation

### Server Code

#### Socket Setup and Server Initialization

The server initializes a socket, binds it to a specified host and port, and listens for incoming connections. Logging is configured for debugging and monitoring purposes.

#### Handling Clients

The server accepts client connections, processes incoming messages, and broadcasts messages to all connected clients. It handles different message types such as login, signup, and chatbot communication.

#### Broadcasting Messages

The server iterates over all connected clients and sends messages to each one. Errors encountered during message sending are logged.

#### Handling Login and Signup

The server processes login and signup messages by interacting with the SQLite database. It validates user credentials and manages user sessions.

#### Chatbot Communication

The server integrates with a generative AI model to provide chatbot responses. It sends user messages to the chatbot and returns the cleaned response.

### Client Code

#### Socket Setup and Client Initialization

The client initializes a socket and sets up the GUI using customtkinter. It manages the connection to the server and handles user interactions.

#### Handling Login and Signup

The client provides a login window for users to enter their credentials. It sends login and signup messages to the server and processes the responses.

#### Sending and Receiving Messages

The client sends messages to the server and receives messages from the server. It updates the GUI with incoming messages and handles errors during communication.

#### Reconnecting to the Server

The client attempts to reconnect to the server if the connection is lost. It tries multiple times and notifies the user if reconnection fails.

## Error Handling

The application includes extensive error handling to manage network communication issues, database errors, and unexpected exceptions. Errors are logged for debugging, and users are notified of connection issues.

## GUI Explanation

The GUI is built using customtkinter and includes various widgets such as frames, labels, entries, buttons, and checkboxes. The layout is designed for ease of use and functionality. Detailed explanations of each widget and their placement are provided in the code comments.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.