import socket
import threading
import time
import base64
import os
import tkinter as tk
from tkinter import scrolledtext, simpledialog

clients = {}
usernames = {}

class ServerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Chat Server GUI")

        self.dark_bg = "#06021E"
        self.dark_fg = "lime"
        self.dark_highlight_bg = "#06021E"
        self.dark_highlight_fg = "black"

        self.master.config(bg=self.dark_bg)

        self.server_message_entry = tk.Entry(master, bg=self.dark_highlight_bg, fg=self.dark_fg)
        self.server_message_entry.pack(pady=10)

        self.send_server_message_button = tk.Button(master, text="Send Server Message", command=self.send_server_message, bg=self.dark_highlight_bg, fg=self.dark_fg)
        self.send_server_message_button.pack(pady=10)

        self.start_button = tk.Button(master, text="Start Server", command=self.start_server, bg=self.dark_highlight_bg, fg=self.dark_fg)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(master, text="Private Mode", command=self.stop_server, state=tk.DISABLED, bg=self.dark_highlight_bg, fg=self.dark_fg)
        self.stop_button.pack(pady=10)

        self.kick_button = tk.Button(master, text="Kick Out Person", command=self.kick_out_person, state=tk.DISABLED, bg=self.dark_highlight_bg, fg=self.dark_fg)
        self.kick_button.pack(pady=10)

        self.close_button = tk.Button(master, text="Close Server", command=self.close_server, state=tk.DISABLED, bg=self.dark_highlight_bg, fg=self.dark_fg)
        self.close_button.pack(pady=10)

        self.log_text = scrolledtext.ScrolledText(master, width=40, height=15, bg=self.dark_bg, fg=self.dark_fg)
        self.log_text.pack(pady=10)

        self.server = None

    def send_server_message(self):
        message = self.server_message_entry.get()
        if message:
            self.broadcast(f"Server: {message}")
            self.log(f"Server: {message}")
            self.server_message_entry.delete(0, tk.END)
        else:
            self.log("Cannot send an empty message.")

    def start_server(self):
        self.server_running = True  
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('192.168.1.12', 12345))
        self.server.listen(5)
        self.log("Server listening on port 12345...")

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.kick_button.config(state=tk.NORMAL)
        self.close_button.config(state=tk.NORMAL)

        threading.Thread(target=self.accept_clients).start()

    def accept_clients(self):
        while True:
            client_socket, addr = self.server.accept()
            self.log(f"Accepted connection from {addr}")

            username = client_socket.recv(1024).decode('utf-8')
            if username in usernames.values():
                self.send_error_message(client_socket, "Username is already taken. Please choose another.")
                client_socket.close()
                continue

            clients[username] = client_socket
            usernames[client_socket] = username
            client_socket.send(f"Welcome to the chat, {username}!".encode('utf-8'))

            self.broadcast(f"{username} has joined the chat.")

            threading.Thread(target=self.handle_client, args=(client_socket, username)).start()

    def handle_client(self, client_socket, username):
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break

                if message.lower() == 'exit':
                    break

                if message.startswith('/private'):
                    parts = message.split(' ', 2)
                    if len(parts) == 3:
                        recipient = parts[1]
                        private_message = f"{username} (private): {parts[2]}"
                        self.send_private_message(username, recipient, private_message)
                    else:
                        self.send_error_message(client_socket, "Invalid private message format.")
                elif message.startswith('image'):
                    parts = message.split(' ', 2)
                    if len(parts) == 3:
                        image_filename = parts[1]
                        image_data = parts[2]
                        self.save_and_broadcast_image(username, image_filename, image_data)
                    else:
                        self.send_error_message(client_socket, "Invalid image message format.")
                else:
                    self.log(f"{username}: {message}")
                    self.broadcast(f"{username}: {message}")

            except ConnectionResetError:
                break

        self.log(f"{username} has left the chat.")

        client_socket.close()
        del clients[username]
        del usernames[client_socket]

        if self.server_running:
            self.log(f"{username} can now continue chatting.")
            threading.Thread(target=self.handle_client, args=(client_socket, username)).start()

    def send_private_message(self, sender, recipient, message):
        if recipient in clients and recipient in usernames:
            recipient_socket = clients[recipient]
            timestamped_message = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}"
            recipient_socket.send(timestamped_message.encode('utf-8'))
        else:
            self.send_error_message(clients[sender], f"{recipient} is not online or doesn't exist.")

    def send_error_message(self, client_socket, message):
        error_message = f"Server: Error - {message}"
        client_socket.send(error_message.encode('utf-8'))

    def save_and_broadcast_image(self, sender, image_filename, image_data):
        try:
            image_data_bytes = base64.b64decode(image_data)
        except Exception as e:
            self.log(f"Error decoding image data: {e}")
            return

        images_folder = "images"
        os.makedirs(images_folder, exist_ok=True)

        image_path = os.path.join(images_folder, image_filename)

        try:
            with open(image_path, "wb") as image_file:
                image_file.write(image_data_bytes)
        except Exception as e:
            self.log(f"Error saving image: {e}")
            return

        for client in clients.values():
            try:
                client.send(f"image {image_filename}".encode('utf-8'))
                client.send(image_data_bytes)
            except Exception as e:
                self.log(f"Error sending image to client: {e}")

    def kick_out_person(self):
        person_to_kick = simpledialog.askstring("Kick Out Person", "Enter the username to kick out:")
        if person_to_kick in clients:
            client_socket = clients[person_to_kick]
            self.send_error_message(client_socket, "You have been kicked out by the server admin.")
            client_socket.close()
            del clients[person_to_kick]
            del usernames[client_socket]
            self.log(f"{person_to_kick} has been kicked out by the server admin.")
            self.broadcast(f"{person_to_kick} has been kicked out by the server admin.")
        else:
                       self.log(f"{person_to_kick} is not online or doesn't exist.")

    def stop_server(self):
        if self.server_running:
            stop_message = "Private mode ON. No other user will be able to join."
            for client_socket in clients.values():
                try:
                    client_socket.send(f"Server: {stop_message}".encode('utf-8'))
                except Exception as e:
                    self.log(f"Error sending stop message to client: {e}")

            self.server.close()
            self.log("Private Mode ON")

            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.kick_button.config(state=tk.DISABLED)
            self.close_button.config(state=tk.NORMAL)

            self.server_running = False

    def close_server(self):
        self.stop_server()
        self.master.destroy()

    def log(self, message):
        timestamped_message = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}"
        self.log_text.insert(tk.END, timestamped_message + '\n')
        self.log_text.see(tk.END)

    def broadcast(self, message):
        timestamped_message = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}"
        for client_socket in clients.values():
            try:
                client_socket.send(timestamped_message.encode('utf-8'))
            except Exception as e:
                self.log(f"Error sending message to client: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    gui = ServerGUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.close_server)
    root.mainloop()
