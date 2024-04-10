import socket
import threading

def get_server_details():
    server_ip = input("Enter the server IP address to bind to (default 127.0.0.1): ")
    server_port = input("Enter the server port (default 12345): ")
    
    # Default values
    server_ip = server_ip if server_ip else '127.0.0.1'
    server_port = int(server_port) if server_port else 12345
    
    return server_ip, server_port

# Get HOST ip and PORT number
HOST, PORT = get_server_details()

# AF_INET = IPv4
#SOCK_STREAM = TCP oriented
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the server to ip and port
server.bind((HOST, PORT))
# thread for listening on the port and incoming traffic
server.listen()

clients = []
nicknames = []
channels = {}

# messaging
def broadcast(message, channel, sender, private_recipient=None):
    sender_nickname = nicknames[clients.index(sender)] if sender in clients else "Unknown"
    if private_recipient:
        try:
            recipient_index = nicknames.index(private_recipient)
            recipient_client = clients[recipient_index]
            formatted_message = f"[Private]{sender_nickname}: {message.decode('utf-8')}".encode('utf-8')
            try:
                if recipient_client:  # Ensure the recipient client socket is still valid
                    recipient_client.send(formatted_message)
            except Exception as e:
                print(f"Error sending private message: {e}")
        except ValueError:
            print(f"Recipient {private_recipient} not found.")
            sender.send(f"Recipient {private_recipient} not found.".encode('utf-8'))
    else:
        formatted_message = f"{message.decode('utf-8')}".encode('utf-8')
        if channel and channel in channels:
            for client in channels[channel]:
                if client != sender and client:  # Avoid sending the message back to the sender
                    try:
                        client.send(formatted_message)
                    except OSError as e:
                        print(f"Error sending message to a client: {e}")
                        channels[channel].remove(client)
                        client.close()

def handle_client(client):
    channel = None
    nickname = None
    try:
        # get nickname from client and add a new client to the list if successful
        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)
        print(f"Nickname of the client is {nickname}")

        while True:
            message = client.recv(1024).decode('utf-8')
            if message.startswith("/join"):
                _, channel_name = message.split()

                # create new channel
                if channel_name not in channels:
                    channels[channel_name] = []

                # join existing channel with client socket
                if client not in channels[channel_name]:
                    channels[channel_name].append(client)
                channel = channel_name

            # broadcast private message
            elif message.startswith("/msg"):
                _, recipient_nickname, *private_msg = message.split()
                private_message = ' '.join(private_msg)
                broadcast(f"{private_message}".encode('utf-8'), channel, client, private_recipient=recipient_nickname)
            
            # break connection to client(depending on answer yes/no)
            elif message.strip() == "/quit":
                raise Exception("Client requested disconnect")
            
            #list all the current channels
            elif message.strip() == "/list":  # New condition for listing channels
                available_channels = ", ".join(channels.keys())
                client.send(f"Available chat rooms: {available_channels}".encode('utf-8'))

            #sending messages in the channel
            else:
                if channel:
                    formatted_message = f"{nickname}: {message}"
                    broadcast(formatted_message.encode('utf-8'), channel, client)
    
    # exception
    except Exception as e:
        print(f"{nickname} disconnected: {str(e)}")

    # remove client from lists and server
    finally:
        if client in clients:
            clients.remove(client)
            nicknames.remove(nickname)
        if channel and client in channels[channel]:
            channels[channel].remove(client)
        client.close()
        if channel:
            broadcast(f"{nickname} left the chat.".encode('utf-8'), channel, client)


def receive():
    print(f"Server is listening on {HOST}:{PORT}...")

    # server running
    while True:

        # create thread that listens on the server port
        client, address = server.accept()
        print(f"Connected with {str(address)}")
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

if __name__ == "__main__":
    receive()
