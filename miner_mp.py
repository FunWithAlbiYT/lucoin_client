import json, time, hashlib
import socket, json

import multiprocessing as mp

#import select, sys

#sys.path.append('../')
from config import CONFIG
from packet import Packet
#, PTracker

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((CONFIG['url'], CONFIG['port']))
client.settimeout(CONFIG['socket_timeout'] / 1000)

def calculate_block(pof, prev_hash, txs):
    return (
        str(pof)
        + str(prev_hash)
        + json.dumps(txs)
    )

def minor_worker_i_love_child_labour(*args):
    start, step, prev_hash, txs_str, req, lim = args[0]
    pof = start

    while pof < lim:
        block_data = str(pof) + prev_hash + txs_str
        hash = hashlib.sha256(block_data.encode()).hexdigest()
        if pof % 1000000 == 0:
            print(f"Calculated {pof:,} Hashes")

        if hash.startswith(req):
            print(f"FOUND!!! POF={pof}")
            return pof
        
        pof += step
    
    return None

def parallel_mine(prev_hash, txs_str, req, lim, num_workers):
    start = time.time()

    pool = mp.Pool(num_workers)
    step = num_workers
    args = [(i, step, prev_hash, txs_str, req, lim) for i in range(num_workers)]

    results = pool.map_async(minor_worker_i_love_child_labour, args)
    results.wait()

    results = results.get()

    for result in results:
        if result is not None:
            end = time.time()
            pool.terminate()
            return result, end - start
    
    
    return None

if __name__ == "__main__":
    mp.freeze_support()

    pof = 0
    limit = 2**32 + 1

    client.sendall(Packet(Packet.GETSIZE, {}).encode())

    size = json.loads(client.recv(1024).decode())['data']['size']
    halvings = size // 120_000
    reward = 50 / (2 ** halvings)

    def compute_fees(txs):
        fees = 0
        for tx in txs:
            fees += tx['fee']
        return fees

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
        calculate_block(prev['pof'], prev['prevhash'], json.loads(prev['transactions'])).encode()
    ).hexdigest()

    client.sendall(Packet(Packet.GETREQ, {}).encode())
    difficulty = json.loads(client.recv(1024).decode())['data']['difficulty']
    req = '0' * int(difficulty)

    mined, time = parallel_mine(prev_hash, json.dumps(txs), req, limit, CONFIG["num_workers"])

    if mined is not None:
        print(f"Mined block #{size} with pof={mined} in {time:.2f}s!")
        client.sendall(Packet(Packet.BROADCAST, {
            "txs": txs,
            "pof": mined
        }).encode())
    else:
        print(f"Failed to mine a block within 2^32+1 hashes.")