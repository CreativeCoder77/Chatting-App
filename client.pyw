import socket
import threading
import datetime
import tkinter as tk
from tkinter import scrolledtext, simpledialog, Text

current_time = datetime.datetime.now()
current_hour = current_time.hour
current_minute = current_time.minute
# Global variables
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.1.12', 12345))

send_on_enter = True

dark_bg = "#06021E"
dark_fg = "lime"
dark_highlight_bg = "#06021E"
dark_highlight_fg = "black"
current_mode = "dark"
light_bg = "white"
light_fg = "black"
light_highlight_bg = "#06021E"

def toggle_mode():
    global current_mode
    if current_mode == "dark":
        apply_light_mode()
        current_mode = "light"
    else:
        apply_dark_mode()
        current_mode = "dark"

def apply_dark_mode():
    window.config(bg=dark_bg)
    canvas.itemconfig(rectangle_chat_area, fill=dark_bg)
    chat_area.config(bg=dark_bg, fg=dark_fg)
    message_entry.config(bg=dark_highlight_bg, fg=dark_fg)
    find_button.config(bg=dark_bg, fg=dark_fg)
    toggle_button.config(text="Light Mode", bg=dark_highlight_bg, fg=dark_fg)

def apply_light_mode():
    window.config(bg=light_bg)
    canvas.itemconfig(rectangle_chat_area, fill=light_bg)
    chat_area.config(bg=light_bg, fg=light_fg)
    message_entry.config(bg=light_bg, fg=light_fg)
    find_button.config(bg=light_highlight_bg, fg=light_fg)
    toggle_button.config(text="Dark Mode", bg=light_highlight_bg, fg=light_fg)

def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            chat_area.configure(state=tk.NORMAL)
            chat_area.insert(tk.END, f"{message}\n")
            chat_area.configure(state=tk.DISABLED)
            chat_area.see(tk.END)
            
            # Save the received message to a text file
            with open(f"{current_hour, current_minute} (username={username}) chat_history.txt", "a") as file:
                file.write(f"{message}\n")
        except ConnectionResetError:
            print("Connection to the server has been lost.")
            break

def send_message():
    message = message_entry.get("1.0", tk.END).strip()
    if message:
        client_socket.send(message.encode('utf-8'))
        message_entry.delete("1.0", tk.END)
        
        # Save the sent message to the chat history file
        with open(f"{current_hour, current_minute} (username={username}) chat_history.txt", "a") as file:
            file.write(f"{message}\n")

def toggle_send_behavior():
    global send_on_enter
    send_on_enter = not send_on_enter

def get_username():
    global username
    username = simpledialog.askstring("Username", "Enter your username:")
    client_socket.send(username.encode('utf-8'))

def on_enter_press(event):
    if send_on_enter:
        send_message()
    else:
        message_entry.insert(tk.END, "\n")

def find_text():
    search_text = simpledialog.askstring("Find", "Enter text to find:")
    if search_text:
        start_index = '1.0'
        while True:
            start_index = chat_area.search(search_text, start_index, stopindex=tk.END)
            if not start_index:
                break
            end_index = f'{start_index}+{len(search_text)}c'
            chat_area.tag_add('find', start_index, end_index)
            chat_area.tag_configure('find', background='yellow', foreground='black')
            start_index = end_index
        window.after(5000, remove_find_highlight)

def remove_find_highlight():
    chat_area.tag_remove('find', '1.0', tk.END)

def delete_selected_messages():
    if chat_area.tag_ranges(tk.SEL):
        start, end = chat_area.tag_ranges(tk.SEL)
        deleted_text = chat_area.get(start, end)
        chat_area.tag_add("deleted", start, end)
        chat_area.tag_config("deleted", overstrike=True, foreground="gray")
        
        # Remove the deleted text from the chat history
        chat_area.delete(tk.SEL_FIRST, tk.SEL_LAST)

# Create GUI
window = tk.Tk()
window.geometry("653x476")
window.title("Chat App")

canvas = tk.Canvas(window, bg=dark_bg, height=476, width=653, bd=0, highlightthickness=0, relief="ridge")
canvas.place(x=0, y=0)

text_widget_id = canvas.create_text(220.0, 12.0, anchor="nw", text="Chatting App", fill="white", font=("Inter Bold", 32 * -1))
rectangle_chat_area = canvas.create_rectangle(9.0, 71.0, 639.0, 318.0, fill=dark_bg, outline="green")
chat_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=65, height=11, state=tk.DISABLED, bg=dark_bg, fg=dark_fg, font=("Arial", 12))
chat_area.place(x=20, y=90)
message_entry = Text(window, wrap=tk.WORD, width=70, height=4, bg=dark_highlight_bg, fg=dark_fg, font=("Arial", 12))
message_entry.place(x=9, y=325)
find_button = tk.Button(window, text="Find", command=find_text, bg=dark_bg, fg=dark_fg, width=10, height=2)
find_button.place(x=540, y=380)
toggle_button = tk.Button(window, text="Toggle Mode", command=toggle_mode, width=10, height=2, bg=dark_highlight_bg, fg=dark_fg)
toggle_button.place(x=540, y=430)
delete_selected_button = tk.Button(window, text="Delete Selected", command=delete_selected_messages, width=15, height=2, bg=dark_highlight_bg, fg=dark_fg)
delete_selected_button.place(x=320, y=430)

receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

get_username()
window.bind("<Return>", on_enter_press)
window.mainloop()
