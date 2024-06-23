# Lucoin Client
## Instructions
* Edit config.py for changing your information, fees, etc.
* Check **Commands** for usage info. <br/>
* Responses are in JSON format.
* Check for client updates once in a while and update it.
## Commands:
Check balance
```bash
$ python client.py balance {optional: address}
```
Send LUC (fee is configurable)
```bash
$ python client.py {amount} {recipient}
```
Get blockchain (limit: 25)
```bash
$ python client.py blockchain
```
Create a wallet
```bash
$ python client.py create
```
Get unconfirmed transactions (MemPool)
```bash
$ python client.py mempool
```
Mine a block
```bash
$ python miner.py
```