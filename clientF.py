# import socket
# import ssl
# import threading

# def receive():
#     while True:
#         try:
#             message = client_ssl.recv(1024).decode('utf-8')
#             if message == 'HARINI':
#                 client_ssl.send(nickname.encode('utf-8'))
#             elif message.startswith('/history'):
#                 print("Chat History:\n", message[9:])
#             elif message.startswith('/list_rooms'):
#                 print("Available Chatrooms:", message.split(': ')[1])
#             elif message.startswith('/kick') or message.startswith('/ban'):
#                 print(message)
#                 stop_thread = True
#             else:
#                 print(message)
#         except ConnectionResetError:
#             print("Connection closed by server.")
#             stop_thread = True
#             break
#         except Exception as e:
#             print("An error occurred:", e)
#             stop_thread = True
#             break

# def write():
#     while True:
#         message = input()
#         if message.startswith('/'):
#             client_ssl.send(message.encode('utf-8'))
#         else:
#             client_ssl.send(f'{nickname}: {message}'.encode('utf-8'))

# # Set up the client socket
# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# # Input nickname from the user
# nickname = input("Choose a nickname: ")

# # Set up SSL context
# context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
# context.check_hostname = False
# context.load_verify_locations("server.crt")  # Provide the server's certificate

# # Wrap the client socket with the SSL context
# client_ssl = context.wrap_socket(client, server_hostname="127.0.0.1")

# # Connect to the server
# client_ssl.connect(('127.0.0.1', 55555))

# stop_thread = False

# # Start the receive thread
# receive_thread = threading.Thread(target=receive)
# receive_thread.start()

# # Start the write thread
# write_thread = threading.Thread(target=write)
# write_thread.start()

import socket
import ssl
import threading

def receive():
    while True:
        try:
            message = client_ssl.recv(1024).decode('utf-8')
            if message == 'HARINI':
                client_ssl.send(nickname.encode('utf-8'))
            elif message.startswith('/history'):
                print("Chat History:\n", message[9:])
            elif message.startswith('/list_rooms'):
                print("Available Chatrooms:", message.split(': ')[1])
            elif message.startswith('/kick') or message.startswith('/ban'):
                print(message)
                stop_thread = True
            else:
                print(message)
        except ConnectionResetError:
            print("Connection closed by server.")
            stop_thread = True
            break
        except Exception as e:
            print("An error occurred:", e)
            stop_thread = True
            break

def write():
    while True:
        message = input()
        if message.startswith('/admin_login'):
            if nickname.lower() == "admin":
                password = input("Enter admin password: ")
                client_ssl.send(f'{message} {password}'.encode('utf-8'))
            else:
                print("Only 'admin' alias can perform admin login.")
        elif message.startswith('/'):
            client_ssl.send(message.encode('utf-8'))
        else:
            client_ssl.send(f'{nickname}: {message}'.encode('utf-8'))

# Set up the client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Input nickname from the user
nickname = input("Choose a nickname: ")

# Set up SSL context
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.check_hostname = False
context.load_verify_locations("server.crt")  # Provide the server's certificate

# Wrap the client socket with the SSL context
client_ssl = context.wrap_socket(client, server_hostname="127.0.0.1")

# Connect to the server
client_ssl.connect(('127.0.0.1', 55555))

stop_thread = False

# Start the receive thread
receive_thread = threading.Thread(target=receive)
receive_thread.start()

# Start the write thread
write_thread = threading.Thread(target=write)
write_thread.start()
