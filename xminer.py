import json, time, hashlib
import socket, json
from colorama import Fore, Back, Style, init
init()

from multiprocessing import *

#import select, sys

#sys.path.append('../')
from config import CONFIG
from packet import Packet
#, PTracker

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((CONFIG['url'], CONFIG['port']))
client.settimeout(CONFIG['socket_timeout'] / 1000)

def compute_fees(txs):
        fees = 0
        for tx in txs:
            fees += tx['fee']
        return fees

def worker(start, step, base, req, q):
    pof = start

    while True:
        if pof % 1000000 == 0:
            print(f"{Fore.LIGHTBLUE_EX} Calculated: {Fore.LIGHTGREEN_EX}{pof:,} {Fore.WHITE} Hashes {Fore.WHITE}...")
        block_data = str(pof) + base
        hash = hashlib.sha256(block_data.encode()).hexdigest()

        if hash.startswith(req):
            q.put(pof)
            return
    
        pof += step

def miner(base, req, num_workers):
    q = Queue()
    processes = []

    for x in range(num_workers):
        p = Process(target=worker, args=(x, num_workers, base, req, q))
        processes.append(p)
        p.start()
    
    pof = q.get()

    for p in processes:
        p.terminate()
    
    return pof

def init_miner(num_workers):
    start = time.time()
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

    mined = miner(prev_hash + json.dumps(txs), req, num_workers)

    if mined is not None:
        end = time.time()
        print(f"{Fore.RED}{Back.GREEN} Mined block {Fore.WHITE}{Back.BLACK}:: {Fore.GREEN} #{size} {Fore.WHITE}with pof={mined} in {Fore.GREEN}{round(end - start)}s")
        client.sendall(Packet(Packet.BROADCAST, {
            "txs": txs,
            "pof": mined
        }).encode())

        res = client.recv(1024).decode()
        if CONFIG["debug_mode"]:
            print(res)
    else:
        print(f"{Style.BRIGHT}{Fore.WHITE}{Back.RED} Failed to mine a block within 2^32+1 hashes.{Back.BLACK}")

def miner_loop(num_workers):
    while True:
        init_miner(num_workers)
        time.sleep(5)

if __name__ == "__main__":
    freeze_support()

    miner_loop(cpu_count() if CONFIG["dedicated_mode"] else int(cpu_count() / 4))
