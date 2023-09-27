import asyncio
import sys
import socket
import os


class Server:

    def __init__(self, TCP_host, TCP_port):
        self.TCP_host = TCP_host
        self.TCP_port = TCP_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def listen(self):
        print(self.TCP_port)
        self.sock.bind(("", self.TCP_port))
        self.sock.listen(2048)

    async def run(self):
        self.sock.settimeout(5)
        self.listen()
        self.sock.setblocking(False)
        loop = asyncio.get_event_loop()

        while True:
            client, addr = await loop.sock_accept(self.sock)
            print("connected to client :", addr)
            loop.create_task(self.handle_client(client, addr))

    async def handle_client(self, client, addr):
        # global response
        loop = asyncio.get_event_loop()
        loop.sock_sendall(client, 'connected to server'.encode())
        request = ["x"]
        while request != 'quit':
            request = (await loop.sock_recv(client, 255)).decode('utf8')
            # print(f'got from {addr} : {request}')

            request = request.split()
            if len(request) != 0:

                if request[0] == "hi":
                    response = b'thank you'


                elif request[0] == "download":
                    print(request)
                    with open(f"./{self.TCP_port}/{request[1]}", "rb") as file:
                        data = file.readlines()
                        print(data)
                        response = b''.join(data)
                        # asyncio.ALL_COMPLETED

                if request[0] == "quit":
                    # response = b"bye"
                    break
                if request[0] == "ping":
                    response = b"pong"
                # try:
                await loop.sock_sendall(client, response)
                if response == b"pong":
                    break
                # except BrokenPipeError:
                #     loop.close()
            # try:
            print(request)
            if request[0] == "download":
                break



class Client():
    def __init__(self, peer_litening_addr, filename):
        self.sock = socket.socket()
        self.peer_litening_addr = peer_litening_addr
        self.filename = filename

    def connect_to_server(self, server_IP, server_port):
        print("x= ", server_IP, server_port)
        self.sock.connect((server_IP, int(server_port)))
        self.sock.send('hi'.encode())
        print(self.sock.recv(2048).decode())

        while True:
            send_message = input()

            if send_message == 'quit':
                break

            # print(received_message)
            if send_message == "download":
                send_message = "download " + self.filename
                self.sock.send(send_message.encode())
                received_message = self.sock.recv(2048).decode()
                print("x = " + self.filename)
                dir = f"./{self.peer_litening_addr[1]}"
                if not os.path.exists(dir):
                    os.makedirs(dir)
                with open(f"./{self.peer_litening_addr[1]}/{self.filename}", "wb") as file:
                    file.write(received_message.encode())
                    print("file received successfuly")
            print("got message from server :", received_message)
            self.close()
            break
            # self.close()

    # close the connection
    def close(self):
        self.sock.send(b"quit")
        self.sock.close()



async def share(tracker_addr, filename, listening_addr, UDP_socket):
    UDP_socket.sendto(f"share {filename} {listening_addr[0]} {listening_addr[1]}".encode(), tracker_addr)
    UDP_socket.settimeout(5)
    data, addr = UDP_socket.recvfrom(1500)
    return data.decode()


async def get(tracker_addr, filename, listening_addr, UDP_socket):
    print(listening_addr)
    UDP_socket.sendto(f"get {filename} {listening_addr[0]} {listening_addr[1]}".encode(), tracker_addr)
    UDP_socket.settimeout(5)
    data, addr = UDP_socket.recvfrom(1500)
    # decoded_data = data.decode().split(":")
    return data.decode()


async def main():
    if len(sys.argv) < 5:
        print("Usage: python peer.py <share|get> <filename> <tracker_address:port> <peer_address:port>")
        sys.exit(1)
    mode = sys.argv[1]
    filename = sys.argv[2]
    tracker_addr = tuple(sys.argv[3].split(":"))
    tracker_addr = (tracker_addr[0], int(tracker_addr[1]))
    peer_listening_addr = tuple(sys.argv[4].split(":"))
    peer_listening_addr = (peer_listening_addr[0], int(peer_listening_addr[1]))

    UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        if mode == "share":
            response = await share(tracker_addr, filename, peer_listening_addr, UDP_socket)
            # response = response.split()
            if response == "ACK":
                server = Server(peer_listening_addr[0], peer_listening_addr[1])
                await server.run()
                print(f"Sharing '{filename}' ")
            else:
                print("Error sharing the file.")
        elif mode == "get":
            response = await get(tracker_addr, filename, peer_listening_addr, UDP_socket)
            if response == "NOT_FOUND":
                print(f"No peers found sharing '{filename}'.")
                break
            else:
                print(f"Peer found at {response} sharing '{filename}'.")
                client = Client(peer_listening_addr, filename)
                adrr = response.split()
                client.connect_to_server(adrr[0], adrr[1])
                mode = "share"

        else:
            print("Invalid mode. Use 'share' or 'get'.")


if __name__ == "__main__":
    asyncio.run(main())
