
import socket
import ssl
import threading
import re

host = '0.0.0.0'
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")

server_ssl = context.wrap_socket(server, server_side=True)

clients = {}
user_chatrooms = {}  
active_chatrooms = {}  

available_chatrooms = ["General", "Tech", "Music", "Movies", "Sports"]

admin_password = "adminpass"

def read_chat_history():
    try:
        with open("history.txt", "r") as file:
            return file.read()
    except FileNotFoundError:
        return "No chat history available."

# Function to write message to chat history file
def write_to_history(message):
    with open("history.txt", "a") as file:
        file.write(message + "\n")

def broadcast(message, sender_chatroom):
    for client_socket, chatroom in user_chatrooms.items():
        if chatroom == sender_chatroom:
            client_socket.send(message.encode('utf-8'))

def handle_client(client_socket, address):
    is_admin = False  # Flag to track if the client is an admin
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            
            if message.startswith('/join'):
                chatroom = message.split(' ')[1]
                join_chatroom(client_socket, chatroom)
            elif message.startswith('/leave'):
                leave_chatroom(client_socket)
            elif message.startswith('/list_rooms'):
                send_available_chatrooms(client_socket)
            elif message.startswith('/kick') or message.startswith('/ban'):
                if is_admin:
                    handle_admin_actions(client_socket, message)
                else:
                    client_socket.send("Only admin can perform kick/ban actions.".encode('utf-8'))
            elif message.startswith('/request_history'):
                history = read_chat_history()
                client_socket.send(f'/history: {history}'.encode('utf-8'))
            elif message.startswith('/admin_login'):
                if is_admin:
                    client_socket.send("You are already logged in as admin.".encode('utf-8'))
                else:
                    password = message.split(' ')[1]
                    if password == admin_password:
                        is_admin = True
                        client_socket.send("Admin login successful.".encode('utf-8'))
                    else:
                        client_socket.send("Incorrect password.".encode('utf-8'))
            else:
                handle_message(client_socket, message)
        except OSError as e:
            print(f"An error occurred in handle_client: {e}")
            break
        except Exception as e:
            print("An unexpected error occurred in handle_client:", e)
            break

    # Client has disconnected
    if client_socket in clients.values():
        nickname = [nick for nick, sock in clients.items() if sock == client_socket][0]
        del clients[nickname]
        if client_socket in user_chatrooms:
            del user_chatrooms[client_socket]
        broadcast(f'{nickname} left the chat', None)
    client_socket.close()

def handle_message(client_socket, message):
    if client_socket in user_chatrooms:
        chatroom = user_chatrooms[client_socket]
        if message.startswith('/'):
            client_socket.send('Invalid command'.encode('utf-8'))
        else:
            broadcast(f'{message}', chatroom)
            write_to_history(f'{chatroom}: {message}')

def join_chatroom(client_socket, chatroom):
    # Add client to the specified chatroom if it exists
    if chatroom in available_chatrooms:
        if chatroom not in active_chatrooms:
            active_chatrooms[chatroom] = []
        active_chatrooms[chatroom].append(client_socket)
        user_chatrooms[client_socket] = chatroom
        client_socket.send(f'You joined chatroom {chatroom}'.encode('utf-8'))
    else:
        client_socket.send(f'Chatroom {chatroom} does not exist'.encode('utf-8'))


def leave_chatroom(client_socket):
    # Remove client from their current chatroom
    if client_socket in user_chatrooms:
        chatroom = user_chatrooms[client_socket]
        if chatroom in active_chatrooms:
            active_chatrooms[chatroom].remove(client_socket)
            del user_chatrooms[client_socket]
            client_socket.send('You left the chatroom'.encode('utf-8'))
    else:
        client_socket.send('You are not in any chatroom'.encode('utf-8'))

def handle_admin_actions(client_socket, message):
    action, target = re.match(r'^/(\w+)\s+(\w+)$', message).groups()
    if action == 'kick':
        kick_user(client_socket, target)
    elif action == 'ban':
        ban_user(client_socket, target)

def kick_user(admin_socket, target):
    for nickname, sock in clients.items():
        if nickname == target:
            sock.send("You have been kicked by the admin.".encode('utf-8'))
            leave_chatroom(sock)
            return
        

def ban_user(admin_socket, target):
    for nickname, sock in clients.items():
        if nickname == target:
            sock.send("You have been banned by the admin.".encode('utf-8'))
            leave_chatroom(sock)
            # Optionally, add the banned user to a banned list for future checks
            return


def send_available_chatrooms(client_socket):
    # Send the list of available chatrooms to the client
    client_socket.send('/list_rooms: '.encode('utf-8') + ', '.join(available_chatrooms).encode('utf-8'))

def accept_clients():
    while True:
        client_socket, address = server_ssl.accept()
        print(f'Connected with {str(address)}')

        client_socket.send('HARINI'.encode('utf-8'))
        nickname = client_socket.recv(1024).decode('utf-8')

        clients[nickname] = client_socket
        print(f'Nickname of client is {nickname}')
        broadcast(f'{nickname} joined the chat', None)

        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
        client_thread.start()

print("Server is listening")
accept_clients()
