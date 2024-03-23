# Chatting-App
## Description
This is a simple chat application implemented using Python's socket programming for networking and Tkinter for the GUI. The application allows multiple clients to connect to a central server and communicate with each other through text messages. It also supports private messaging and sending images.
## Features
Server: The server is responsible for accepting connections from clients, handling incoming messages, broadcasting messages to all clients, and managing private messaging.

Client:The client connects to the server, sends messages, receives messages, and displays them in the GUI. It also supports sending private messages, searching for text in the chat history, toggling between dark and light modes, and deleting selected messages.

GUI: The GUI is implemented using Tkinter, providing a user-friendly interface for sending and receiving messages.

## Installation

Clone the repository:

```
git clone https://github.com/DhairyaAgarwa/Chatting-App.git
```
Run the server:

```bash
python server.pyw
```
Run the client:
```bash
python client.pyw
```
## Usage
- Start the server first, then run the client application.

- Enter your desired username when prompted.

- Type your message in the input field and press Enter to send.

- Use the "Toggle Mode" button to switch between dark and light modes.

- Use the "Find" button to search for text in the chat history.

- To delete selected messages, select the text and click on the "Delete Selected" button.

## Steps
#### 1.Clone the Repository:
>>>Clone the repository from GitHub using the provided URL.

#### Navigate to the Project Directory:
>>>Open your terminal or command prompt and navigate to the directory where the project was cloned.

#### Run the Server:
>>>Execute the server.pyw script to start the server.

#### Run the Client:
>>>Execute the client.pyw script to start the client application.

#### Enter Username:
>>>When prompted, enter your desired username to join the chat.

#### Start Chatting:
>>>Start sending and receiving messages with other users in the chat.


## License

  - [MIT](https://choosealicense.com/licenses/mit/)


## Acknowledgements

 - [Python Documentation](https://docs.python.org/3/library/socket.html)
 - [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)

