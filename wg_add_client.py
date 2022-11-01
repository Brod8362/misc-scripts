#!/bin/python3
import sys
import os
import subprocess
import re

def parseline(line: str):
    accepted = ""
    for char in line:
        if char == '#':
            break
        accepted += char
    return accepted

def gen_private() -> str:
    return os.popen("wg genkey").read()


def gen_public(private: str) -> str:
    p = subprocess.Popen(["wg", "pubkey"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = p.communicate(input=private.encode("utf-8"))
    return output[0].decode()

def generate_keypair() -> "(str, str)":
    """(private, public)"""
    priv = gen_private()
    pub = gen_public(priv.strip())
    return (priv.strip(), pub.strip())

class WireguardConfig:
    def __init__(self, filepath: str | None = None):
        self.peers = []
        self.interface = {}
        self.meta = {}
        if filepath:
            with open(filepath, "r") as fd:
                status = ""
                peer_buffer = {}
                for line in fd.read().split("\n"):
                    if line.startswith("##"): #meta information
                        arr = line.replace(" ", "").split("=", 1)
                        if len(arr) == 2:
                            self.meta[arr[0][2:]] = arr[1]
                        continue
                    parsed = parseline(line.replace(" ", ""))
                    if parsed == "[Interface]":
                        status = "interface"
                    elif parsed == "[Peer]":
                        status = "peer"
                        if peer_buffer:
                            self.peers.append(peer_buffer)
                            peer_buffer = {}
                    elif not parsed:
                        #empty line
                        continue
                    else:
                        arr = parsed.split("=", 1)
                        if len(arr) < 2:
                            continue
                        k = arr[0]
                        v = arr[1]
                        #print(f"k: {k}, v: {v}")
                        if status == "interface":
                            self.interface[k] = v
                        elif status == "peer":
                            peer_buffer[k] = v
                self.peers.append(peer_buffer)
                            
    def export(self) -> str:
        output = "[Interface]\n"
        for m in self.meta:
            output += f"##{m} = {self.meta[m]}\n"
        for option in self.interface:
            output += f"{option} = {self.interface[option]}\n"
        for peer in self.peers:
            output += "\n[Peer]\n"
            for option in peer:
                output += f"{option} = {peer[option]}\n"
        return output

    def write(self, filename: str):
        with open(filename, "w") as fd:
            fd.write(self.export())

    def add_peer(self, pubkey: str, allowedIP: str):
        peer = {
            "PublicKey": pubkey,
            "AllowedIPs": allowedIP+"/32"
        }
        self.peers.append(peer)

    def ip_in_use(self, ip: str) -> bool:
        """expected input 127.0.0.1 not 127.0.0.1/32"""
        for peer in self.peers:
            for x in peer["AllowedIPs"].split(","):
                if ip in x:
                    return True
        return ip in self.interface["Address"]

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("wg_add_client.py: <server_config> <client_config>")
        sys.exit(1)
    if os.path.abspath(sys.argv[1]) == os.path.abspath(sys.argv[2]):
        print("server and client file may not be identical")
        sys.exit(1)
    if os.path.exists(sys.argv[2]):
        print("destination already exists")
        sys.exit(1)
    serverConfig = WireguardConfig(sys.argv[1])
    required_meta = ["PublicKey", "EndpointIP"]
    for m in required_meta:
        if not m in serverConfig.meta:
            print(f"server config is not configured correctly, please add {m} meta")
            sys.exit(1)
    clientConfig = WireguardConfig() #not expecting to read anything here
    private_key, public_key = generate_keypair()
    new_client_ip = None
    while True:
        new_client_ip = input("New client IP address (x.x.x.x):")
        octet_count = 0
        for octet in new_client_ip.split("."):
            octet_count += 1
            try:
                if int(octet) > 255:
                    octet_count = -9999
            except Exception:
                octet_count = -9999
        if serverConfig.ip_in_use(new_client_ip):
            print("\033[1;31mip address already in use\033[0m")
        elif octet_count == 4:
            break
        else:
            print("\033[1;31minvalid ip address\033[0m")

    with open(sys.argv[1], "a") as fd:
        peer_content = (
            "\n\n[Peer] #added by wg_add_client\n"
            f"AllowedIPs = {new_client_ip}/32\n"
            f"PublicKey = {public_key}\n"
        )
        fd.write(peer_content)

    clientConfig.interface = {
        "Address": new_client_ip+"/24",
        "PrivateKey": private_key
    }
    clientConfig.peers.append({
        "PublicKey" : serverConfig.meta["PublicKey"],
        "AllowedIPs" : serverConfig.interface["Address"],
        "Endpoint" : serverConfig.meta["EndpointIP"]+":"+serverConfig.interface["ListenPort"],
        "PersistentKeepalive" : "60"
    })
    clientConfig.write(sys.argv[2])
