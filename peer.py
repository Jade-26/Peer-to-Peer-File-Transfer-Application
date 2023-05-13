import sys
import socket
import threading
import json
import time

class Peer:
    def __init__(self, manager_ip, manager_port, shareable_files):
        self.manager_ip = manager_ip
        self.manager_port = manager_port
        self.active_peers = {}
        self.shareable_files = shareable_files

    def join_network(self, ip, port):
        text = "Joining the network... as " + ip + " : " + str(port)
        print(text)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((ip, port))
            s.listen()

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as manager_conn:
                " Send a join request to the manager "
                manager_conn.connect((self.manager_ip, self.manager_port))
                join_request = json.dumps({"type": "join", "port": port}).encode()
                
                manager_conn.sendall(join_request)

            while True:
                conn, addr = s.accept()
                t = threading.Thread(target=self.handle_connection, args=(conn, addr))
                t.start()

    def leave_network(self, ip, port):
        text = "Leaving the network... as " + ip + " : " + str(port)
        print(text)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            " Send a leave request to the manager"
            s.connect((self.manager_ip, self.manager_port))
            
            leave_request = json.dumps({"type": "leave", "port": port}).encode()
            s.sendall(leave_request)

    def request_file(self, file_name):
        " Create a separate list of peers that participated in the file transfer "
        transfer_peers = self.active_peers.copy()

        file_fragments = [None] * len(self.active_peers)
        completed_fragments = 0

        " This function handles the file fragment response from other peers "
        def handle_fragment_response(conn, addr):
            nonlocal completed_fragments
            data = conn.recv(1024)
            if data:
                response = json.loads(data.decode())
                if response["type"] == "file_fragment":
                    file_fragments[response["fragment_number"]] = response["file_fragment"]
                    completed_fragments += 1
                    
                    print(f"Received fragment {response['fragment_number']} from {addr[0]}:{addr[1]}")

        " Request file fragments from all active peers "
        for idx, ((addr, port), _) in enumerate(transfer_peers.items()):
            " Connect to the peer and request the file fragment "
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((addr, port))
                request = json.dumps({"type": "request_file", "file_name": file_name, "fragment_number": idx}).encode()
                s.sendall(request)
                text = "Requesting file fragment " + str(idx) + " from " + str(addr) + ":" + str(port)
                  
                text = "Requesting file fragment " + str(idx) + " from " + str(addr) + ":" + str(port)
                print(text)
                

                t = threading.Thread(target=handle_fragment_response, args=(s, (addr, port)))
                t.start()

        " Wait until all file fragments are received "
        while completed_fragments < len(self.active_peers):
            time.sleep(0.15)

        " Reconstruct the original file  "
        reconstructed_file = "".join(file_fragments)
        with open(f"reconstructed_{file_name}", "w") as out_file:
            out_file.write(reconstructed_file)
            

        text = "File transfer is now successfully complete: " + file_name
        print(text)

    def handle_connection(self, conn, addr):
        try:
            data = conn.recv(1024)
            if data:
                request = json.loads(data.decode())
                if "peers" in request:
                    self.update_active_peers(request["peers"])
                elif request["type"] == "request_file":
                    file_name = request["file_name"]
                    if file_name in self.shareable_files:
                        with open(file_name, "r") as file:
                            file_contents = file.read()
                              
                            file_size = len(file_contents)
                            fragment_size = file_size // len(self.active_peers)
                              
                            fragment_start = request["fragment_number"] * fragment_size
                            
                            fragment_end = fragment_start + fragment_size

                            if request["fragment_number"] == len(self.active_peers) - 1:
                                fragment_end = file_size

                            file_fragment = file_contents[fragment_start:fragment_end]
                              
                            response = json.dumps({"type": "file_fragment", "file_name": file_name, "file_fragment": file_fragment, "fragment_number": request["fragment_number"]}).encode()
                            conn.sendall(response)
                            
        finally:
            conn.close()

    def update_active_peers(self, new_peers):
        
        updated_peers = {(peer_addr, peer_port): peer_port for peer_addr, peer_port in new_peers}
          
        self.active_peers.update(updated_peers)
        text = "Updated active peers list: " + str(self.active_peers)
        print(text)

if __name__ == "__main__":
    peer = Peer("127.0.0.1", 5000, ["shared_file.txt"])

    PORT = int(sys.argv[1])

    peer_thread = threading.Thread(target=peer.join_network, args=("127.0.0.1", PORT))
      
    peer_thread.start()

    if PORT == 5001:
        time.sleep(5)
        print()
        print("............The File is in the process of being shared..................")
        time.sleep(4)
        print()
        print(".................The fragments are being collected.........................")
        time.sleep(4)
        peer.request_file("shared_file.txt")

    if len(sys.argv) == 3:
        delay = int(sys.argv[2])
        time.sleep(delay)
        peer.leave_network("127.0.0.1", PORT)