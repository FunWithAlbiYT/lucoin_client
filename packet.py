import json

class Packet:
    RESPONSE = 0
    GETCHAIN = 1
    ADDWALLET = 2
    BALANCE = 3
    TRANSACT = 4
    TRACKER = 5
    GETMEM = 6
    BROADCAST = 7
    GETSIZE = 8
    GETREQ = 9

    def __init__(self, ptype, data):
        self.type = ptype
        self.data = data

    def encode(self):
        return json.dumps({
            "type": self.type,
            "data": self.data
        }).encode()
    
class PTracker:
    TRANSACTION = 50
    NEWBLOCK = 51