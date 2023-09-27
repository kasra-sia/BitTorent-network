import asyncio
import random
import socket
from collections import defaultdict
gl_peers = defaultdict(lambda: set())
request_logs = {}
async def keep_alive(tracker, ps):
    while True:
        for file, peer_set in ps.items():
            disconnected_peers = set()
            # print(f"check peers of file {file}")
            for p in peer_set:
                # print(f"check {p}")
                try:
                    sock = socket.socket()
                    addr = p.split()
                    sock.connect((addr[0],int(addr[1])))
                    sock.send(b"ping")
                    ans = sock.recv(150).decode()
                    # print(f"from {p} we got {ans}")
                    if ans != "pong":
                        raise Exception("PONG_FAILED")
                    sock.close()
                except Exception as e:
                    print("{p} has been disconnected")
                    disconnected_peers.add(p)
            ps[file] = ps[file] - disconnected_peers

        await asyncio.sleep(2)

class Tracker:
      
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}
    async def listen(self):
        dp = DatagramProtocol()
        self.transport, _ = await self.loop.create_datagram_endpoint(
            lambda: dp,
            local_addr=("127.0.0.1", self.port)
        )
        print(f"Listening on {self.host}:{self.port}")
        keep_alive_task = asyncio.create_task(keep_alive(self, dp.peers))
        await asyncio.gather(keep_alive_task, asyncio.sleep(3600))

    async def read_user_input(self):
        # global request_logs
        
        while True:
            user_input = await asyncio.to_thread(input)
            if user_input == "request logs":
                for peer in request_logs:
                    print(f"{peer}: {request_logs[peer]}")
            elif user_input == "file_logs -all" :
                for k, v in gl_peers.items():
                    print(f"{k} : {v}")

            elif user_input.startswith("file_logs>") :
                file_name = user_input.split(">")[1]
                if gl_peers[file_name]:
                    print(gl_peers[file_name])
                else :
                    print("file doesn't exist")    
            else: 
                print("invalid command")
    
    async def run(self):
        asyncio.create_task(self.read_user_input())
        self.loop = asyncio.get_running_loop()
        await self.listen()
        
        # while True:
            # await asyncio.sleep(3600)
    def close(self):
        self.transport.close()

class DatagramProtocol(asyncio.DatagramProtocol):

    def __init__(self):
        self.peers = defaultdict(set)
        global gl_peers
        gl_peers = self.peers
        self.counter = 0


    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        
        message = data.decode().split()
        print(message)
        if message[0] == "share":
            self.peers[message[1]].add(message[-2]+" "+message[-1] )
            send = "ACK" 
            request_logs[addr] = f"is sharing {message[1]} on {message[-2]}: {message[-1]}"
            self.transport.sendto(send.encode(), addr)
            # print(message)
            
        
        elif message[0] == "get":
            if message[1] in self.peers and self.peers[message[1]]:
                # print(dict(self.peers),"x",message[-1])
                selected_peer = random.choice(tuple(self.peers[message[1]]))
                self.transport.sendto(selected_peer.encode(), addr)
                # print(selected_peer)
                request_logs[addr] = f"is getting {message[1]} on {message[-2]}: {message[-1]}"

            else:
                request_logs[addr] = f"{message[1]} Not found"
                self.transport.sendto(b"NOT_FOUND", addr)


if __name__ =="__main__":
    tracker = Tracker('127.0.0.1', 8888)
    try:
        asyncio.run(tracker.run())
        
        # while True: 

    except KeyboardInterrupt:
        tracker.close()    
