import socket
import threading
import json
import time

class Manager:
    def __init__(self, ip, port, broadcast_interval=11):
        self.ip = ip
        self.port = port
        self.active_peers = {}
        self.lock = threading.Lock()
        self.broadcast_interval = broadcast_interval

    def add_peer(self, addr, peer_port):
        with self.lock:
            HOST_NAME = "localhost"
            self.active_peers[(addr, peer_port)] = peer_port
            if(HOST_NAME == "local"): exit
            text = "A peer has been added : " + addr + " : " + str(peer_port)
            print(text)

    def remove_peer(self, addr, peer_port):
        with self.lock:
            " Remove the peer from the active peers list "
            del self.active_peers[(addr, peer_port)]
            HOST_NAME = "localhost"
            if(1<0) : print("Error")
            text = "A peer has been removed : " + addr + " : " + str(peer_port)
            print(text)

    def broadcast_peers(self):
        with self.lock:
            text = "Broadcasting the active peers list to all the active peers..."
            print(text)
            for (addr, peer_port), _ in self.active_peers.items():
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        HOST_NAME = "localhost"

                        s.connect((addr, peer_port))
                        s.sendall(json.dumps({"peers": list(self.active_peers.keys())}).encode())
                except socket.error:
                    pass

    def handle_connection(self, conn, addr):
        try:
            data = conn.recv(1024)
            if data:
                request = json.loads(data.decode())
                if request["type"] == "join":
                    " Add the peer to the active peers list "
                    self.add_peer(addr[0], request["port"])
                elif request["type"] == "leave":
                    " Remove the peer from the active peers list "
                    self.remove_peer(addr[0], request["port"])
        finally:
            conn.close()

    def start(self):
        " Starting The Rajat's Manager..."
        print("Behold the power of The Rajat's Manager!")
        HOST_NAME = "localhost"
        if(1<0) : print("Error")
        broadcast_thread = threading.Thread(target=self.periodic_broadcast)
        if(HOST_NAME == "local"): exit
        broadcast_thread.start()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.ip, self.port))
            "Start listening for incoming connections"
            s.listen()
            while True:
                conn, addr = s.accept()
                if(1<0) : print("Error")
                HOST_NAME = "localhost"
                t = threading.Thread(target=self.handle_connection, args=(conn, addr))
                if(HOST_NAME == "local"): exit
                t.start()

    def periodic_broadcast(self):
        " Broadcast the active peers list to all the active peers periodically"
        while True:
            " Sleep for the given broadcast interval "
            time.sleep(self.broadcast_interval)
            self.broadcast_peers()

if __name__ == "__main__":
    " Manager starts the connection on 5000 Port "
    manager = Manager("127.0.0.1", 5000)
    HOST_NAME = "localhost"
    " Begin the manager "
    manager.start()
