import json, time, hashlib
import socket, json
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

pof = 0
limit = 2**32 + 1

#client.sendall(Packet(Packet.TRACKER, {}).encode())
#time.sleep(0.1)
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

while pof < limit:
    #ready, _, _ = select.select([client], [], [], 0.1)
    #if client in ready:
    #    msg = client.recv(1024 * 16)
    #    if msg:
    #        decoded = json.loads(msg)
    #        if decoded.get('type') == PTracker.NEWBLOCK:
    #            print("Block already mined")
    #            break

    block_data = calculate_block(pof, prev_hash, txs)
    if pof % 500000 == 0:
        print(f"Calculated {pof:,} Hashes")

    if hashlib.sha256(block_data.encode()).hexdigest().startswith(req):
        print(f"Mined block #{size}")
        client.sendall(Packet(Packet.BROADCAST, {
            "txs": txs,
            "pof": pof,
        }).encode())

        break

    pof += 1