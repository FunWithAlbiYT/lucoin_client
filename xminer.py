import json, time, hashlib
import socket, json

from platform import system

from multiprocessing import *

# import select, sys

if system() == "Windows":
    import threading
    import msvcrt
else:
    import select
    import sys

from datetime import datetime

#sys.path.append('../')
from config import CONFIG
from packet import Packet
#, PTracker

import colorama

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((CONFIG['url'], CONFIG['port']))
client.settimeout(CONFIG['socket_timeout'] / 1000)

# an amalgamation of a few things i found on the internet regarding this subject
def read_input(default, timeout=5):
    if system() == "Windows":
        class KbThread(threading.Thread):
            def run(self):
                self.timedout = False
                self.input = ""

                while True:
                    if msvcrt.kbhit():
                        chr = msvcrt.getche().decode()
                        if ord(chr) == 13:
                            break
                        elif ord(chr) >= 32:
                            self.input += chr
                    if len(self.input) == 0 and self.timedout:
                        break
        
        result = default
        thread = KbThread()
        thread.start()
        thread.join(timeout)
        thread.timedout = True

        if len(thread.input) > 0:
            thread.join()
            result = thread.input
        
        print("")

        return result
    else:
        i, _, _ = select.select([sys.stdin], [], [], timeout)

        return i


def compute_fees(txs):
        fees = 0
        for tx in txs:
            fees += tx['fee']
        return fees

def worker(start, step, base, req, q, worker_id):
    pof = start

    while True:
        if pof % 1000000 == 0:
            print(f"{colorama.Fore.BLUE}Calculated {colorama.Fore.WHITE}{pof:,} {colorama.Fore.BLUE}Hashes")
        block_data = str(pof) + base
        hash = hashlib.sha256(block_data.encode()).hexdigest()

        if hash.startswith(req):
            q.put((pof, worker_id))
            return
    
        pof += step

def miner(starting_pof, base, req, num_workers):
    q = Queue()
    processes = []

    for x in range(num_workers):
        p = Process(target=worker, args=(starting_pof + x, num_workers, base, req, q, x))
        processes.append(p)
        p.start()
    
    data = q.get()

    for p in processes:
        p.terminate()
    
    return data

def init_miner(num_workers, iteration):
    starting_pof = 0
    print("Choose starting PoW? This input will timeout in 5 seconds.")

    try:
        starting_pof = int(read_input("0"))
    except ValueError:
        raise ValueError("You didn't input a number!")

    start = time.time()
    print(f"Starting miner at {datetime.fromtimestamp(start).strftime('%H:%M:%S on %A')} with starting pof {starting_pof} - Iteration #{iteration}")
    
    client.sendall(Packet(Packet.GETSIZE, {}).encode())

    size = json.loads(client.recv(1024).decode())['data']

    if CONFIG["debug_mode"]:
        print(size)
    size = size["size"]
    halvings = size // 120_000
    reward = 50 / (2 ** halvings)

    client.sendall(Packet(Packet.GETMEM, {"highfee": True, "limit": 5}).encode())
    memTxs = json.loads(client.recv(1024 * 8).decode())['data']

    rewardTx = {
        "txid": size,
        "timestamp": round(time.time()),
        "amount": reward + compute_fees(memTxs),
        "fee": 0.0,
        "key": CONFIG['wallet'][:25],
        "recipient": CONFIG['wallet'],
        "sender": "Block Reward",
    }

    txs = [rewardTx]
    txs.extend(memTxs)

    client.sendall(Packet(Packet.GETCHAIN, {"limit": 1}).encode())
    prev = json.loads(client.recv(1024 * 8).decode())['data'][0]
    prev_hash = hashlib.sha256(
        (str(prev["pof"]) + str(prev["prevhash"]) + prev["transactions"]).encode()
    ).hexdigest()

    client.sendall(Packet(Packet.GETREQ, {}).encode())
    difficulty = json.loads(client.recv(1024).decode())['data']['difficulty']
    req = '0' * int(difficulty)

    mined, worker = miner(starting_pof, prev_hash + json.dumps(txs), req, num_workers)

    if mined is not None:
        end = time.time()
        string = f"{colorama.Fore.BLUE}Mined block #{colorama.Fore.WHITE}{size}{colorama.Fore.BLUE}!\n POF/PoW: {colorama.Fore.WHITE}{mined}{colorama.Fore.BLUE}\nTime Taken: {colorama.Fore.WHITE}{end - start:.2f}s{colorama.Fore.BLUE}\nWorker: {colorama.Fore.WHITE}{worker}"
        bar = f"{colorama.Back.GREEN}{' ' * len(string)}"
        print(bar)
        print("\n")
        print(string)
        print("\n")
        print(bar)
        client.sendall(Packet(Packet.BROADCAST, {
            "txs": txs,
            "pof": mined
        }).encode())

        res = client.recv(1024).decode()
        if CONFIG["debug_mode"]:
            print(res)
    else:
        print(f"Failed to mine a block within 2^32+1 hashes.")#

def miner_loop(num_workers):
    i = 0
    while True:
        i += 1
        init_miner(num_workers, i)

if __name__ == "__main__":
    freeze_support()
    colorama.init(autoreset=True)

    miner_loop(cpu_count() if CONFIG["dedicated_mode"] else int(cpu_count() / 4))
