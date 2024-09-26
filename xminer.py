from multiprocessing import Process, Queue, freeze_support, cpu_count

from datetime import datetime
from platform import system
from pathlib import Path
from os import path

import json
import time
import hashlib
import socket

import colorama
from desktop_notifier import DesktopNotifierSync, Icon

from config import CONFIG
from packet import Packet

if system() == "Windows":
    import threading

    # pylint: disable-next=import-error
    import msvcrt
else:
    import select
    import sys

lucoin_icon = Icon(Path(path.abspath("./resources/lucoin.ico")))
notifier = DesktopNotifierSync("XMiner - Lucoin", lucoin_icon)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((CONFIG['url'], CONFIG['port']))
client.settimeout(CONFIG['socket_timeout'] / 1000)

# an amalgamation of a few things i found on the internet regarding this subject
def read_input(default, timeout=5):
    if system() == "Windows":
        class KbThread(threading.Thread):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.timedout = False
                self.input = ""
            def run(self):
                while True:
                    if msvcrt.kbhit():
                        char = msvcrt.getche().decode()
                        if ord(char) == 13:
                            break
                        if ord(char) >= 32:
                            self.input += char

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
            # pylint: disable-next=line-too-long
            print(f"{colorama.Fore.BLUE}Calculated {colorama.Fore.WHITE}{pof:,} {colorama.Fore.BLUE}Hashes")
        block_data = str(pof) + base
        hash_digest = hashlib.sha256(block_data.encode()).hexdigest()

        if hash_digest.startswith(req):
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
    except ValueError as exc:
        raise ValueError("You didn't input a number!") from exc

    start = time.time()

    client.sendall(Packet(Packet.GETSIZE, {}).encode())

    size = json.loads(client.recv(1024).decode())['data']
    if CONFIG["debug_mode"]:
        print(size)

    size = size["size"]

    # pylint: disable-next=line-too-long
    print(f"Starting miner at {datetime.fromtimestamp(start).strftime('%H:%M:%S on %A')} with starting PoW {starting_pof} - Mining block #{size} - Iteration #{iteration}")

    halvings = size // 120_000
    reward = 50 / (2 ** halvings)

    client.sendall(Packet(Packet.GETMEM, {"highfee": True, "limit": 5}).encode())
    mem_txs = json.loads(client.recv(1024 * 8).decode())['data']

    reward_tx = {
        "txid": size,
        "timestamp": round(time.time()),
        "amount": reward + compute_fees(mem_txs),
        "fee": 0.0,
        "key": CONFIG['wallet'][:25],
        "recipient": CONFIG['wallet'],
        "sender": "Block Reward",
    }

    txs = [reward_tx]
    txs.extend(mem_txs)

    client.sendall(Packet(Packet.GETCHAIN, {"limit": 1}).encode())
    prev = json.loads(client.recv(1024 * 8).decode())['data'][0]
    prev_hash = hashlib.sha256(
        (str(prev["pof"]) + str(prev["prevhash"]) + prev["transactions"]).encode()
    ).hexdigest()

    client.sendall(Packet(Packet.GETREQ, {}).encode())
    difficulty = json.loads(client.recv(1024).decode())['data']['difficulty']
    req = '0' * int(difficulty)

    mined, worker_id = miner(starting_pof, prev_hash + json.dumps(txs), req, num_workers)

    if mined is not None:
        end = time.time()

        client.sendall(Packet(Packet.BROADCAST, {
            "txs": txs,
            "pof": mined
        }).encode())

        res = json.loads(client.recv(1024).decode())
        if CONFIG["debug_mode"]:
            print(res)

        if res.get("code", None) is None:
            if CONFIG["send_notifications"]:
                # pylint: disable-next=line-too-long
                notifier.send(title="Block mined!", message=f"Block #{size} has been mined successfully!", icon=lucoin_icon)
            # pylint: disable-next=line-too-long
            string = f"{colorama.Fore.BLUE}Mined block #{colorama.Fore.WHITE}{size}{colorama.Fore.BLUE}!\n POF/PoW: {colorama.Fore.WHITE}{mined}{colorama.Fore.BLUE}\nTime Taken: {colorama.Fore.WHITE}{end - start:.2f}s{colorama.Fore.BLUE}\nWorker: {colorama.Fore.WHITE}{worker_id}"
            coloured_bar = f"{colorama.Back.GREEN}{' ' * len(string)}"
            print("")
            print(coloured_bar)
            print("")
            print(string)
            print("")
            print(coloured_bar)
            print("")
        else:
            if CONFIG["send_notifications"]:
                # pylint: disable-next=line-too-long
                notifier.send(title="Invalid block found...", message=f"Block #{size} was mined, however was found to be invalid.", icon=lucoin_icon)
            string = f"{colorama.Fore.BLUE}Block #{colorama.Fore.WHITE}{size} is invalid!"
            coloured_bar = f"{colorama.Back.RED}{' ' * len(string)}"
            print("")
            print(coloured_bar)
            print("")
            print(string)
            print("")
            print(coloured_bar)
            print("")
    else:
        # Unreachable
        print("Failed to mine a block within 2^32+1 hashes.")

def miner_loop(num_workers):
    i = 0
    while True:
        i += 1
        init_miner(num_workers, i)

if __name__ == "__main__":
    if system() == "Windows":
        freeze_support() # required on Windows
    colorama.init(autoreset=True)

    miner_loop(cpu_count() if CONFIG["dedicated_mode"] else int(cpu_count() / 4))
