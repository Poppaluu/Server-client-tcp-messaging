import socket
import threading
import sys

# creating connection with prompts to user
def get_server_details():
    server_ip = input("Enter server IP address (default 127.0.0.1): ")
    server_port = input("Enter server port (default 12345): ")
    
    # Default server values
    server_ip = server_ip if server_ip else '127.0.0.1'
    server_port = int(server_port) if server_port else 12345
    
    return server_ip, server_port

def client_program():
    server_ip, server_port = get_server_details()
    nickname = input("Choose your nickname: ")

    # create socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # connect to server
        client.connect((server_ip, server_port))
    except:
        print("Connection to the server failed.")
        return

    def receive():
        while True:
            try:

                # receive info from server and send messages or nickname
                message = client.recv(1024).decode('utf-8')
                if message == 'NICK':
                    client.send(nickname.encode('utf-8'))
                else:
                    print(message)
            except:
                print("You have been disconnected from the server.")
                client.close()
                break

    def write():

        # writing messages
        while True:
            message = input('')
            if message == "/quit":
                client.send(message.encode('utf-8'))
                break
            client.send(message.encode('utf-8'))

    # thread to receive messages from server
    receive_thread = threading.Thread(target=receive)

    # thread to send messages to the server
    write_thread = threading.Thread(target=write)

    #starting threads
    receive_thread.start()
    write_thread.start()

    write_thread.join()
    client.close()
    receive_thread.join()

if __name__ == "__main__":
    while True:
        client_program()
        restart = input("Do you want to reconnect? (yes/no): ").lower()
        if restart != "yes":
            break
