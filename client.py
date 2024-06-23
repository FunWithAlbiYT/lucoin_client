import socket, sys
from config import CONFIG
from packet import Packet

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((CONFIG['url'], CONFIG['port']))

arg = sys.argv[1]
if arg == "blockchain":
    packet = Packet(Packet.GETCHAIN, {"limit": 25})
elif arg == "create":
    packet = Packet(Packet.ADDWALLET, {})
elif arg == "balance":
    wallet = sys.argv[2] if len(sys.argv) > 2 else CONFIG['wallet']
    packet = Packet(Packet.BALANCE, {"address": wallet})
elif arg == "send":
    amount, recipient = sys.argv[2:4]
    fee = float(amount) * CONFIG['fee']
    packet = Packet(Packet.TRANSACT, {
        "recipient": recipient,
        "amount": float(amount),
        "fee": fee,
        "sender": CONFIG['wallet'],
        "key": CONFIG['key']
    })
elif arg == "mempool":
    limit = sys.argv[2] if len(sys.argv) > 2 else 25
    packet = Packet(Packet.GETMEM, {
        "limit": limit,
        "highfee": False
    })
else:
    sys.exit(1)

client.settimeout(CONFIG['socket_timeout'] / 1000)
client.sendall(packet.encode())
data = client.recv(1024 * 8)

if data:
    print(data.decode())
else:
    print("Network error!")