# Lucoin Client

## Description

Lucoin Client is a command-line tool for interacting with the Lucoin cryptocurrency. It allows users to check balances, send transactions, retrieve blockchain data, and more.

## Installation
Install Python 3.10. You can download it from [here](https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe) for Windows and [here](https://www.python.org/ftp/python/3.10.0/python-3.10.0post2-macos11.pkg) for macOS.\
Make sure to select `Add Python to PATH` in the installer!\
Head to the [release page](https://github.com/FunWithAlbiYT/lucoin_client/releases/tag/Universal) and download the `install.py` artefact. Download it to wherever you'd like to install the Lucoin Client.\
Finally, run install.py and it'll install everything for you.\

## Configuration
Edit the config.py file to configure your information, fees, and other settings.

## Usage
The Lucoin Client supports the following commands:

### Check Balance
To check the balance of your wallet (or a specified address):


```bash
python client.py balance [optional: address]
```
### Send LUC
To send Lucoin (LUC) to a recipient (fees are configurable):
```bash
python client.py {amount} {recipient}
```
### Get Blockchain Data
To retrieve the blockchain data (limited to 25 blocks):

```bash
python client.py blockchain
```
### Create a Wallet
To create a new wallet:

```bash
python client.py create
```
### Get Unconfirmed Transactions (MemPool)
To retrieve unconfirmed transactions from the MemPool:

```bash
python client.py mempool
```
### Mine a Block
To mine a new block:

```bash
python miner.py
```
## Responses
All responses from the client are in JSON format.

## Updates
Check for client updates periodically and update to the latest version.
