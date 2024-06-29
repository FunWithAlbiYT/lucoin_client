# Lucoin Client

## Description

Lucoin Client is a command-line tool for interacting with the Lucoin cryptocurrency. It allows users to check balances, send transactions, retrieve blockchain data, and more.

## Installation

Clone the repository:
```bash
git clone https://github.com/FunWithAlbiYT/lucoin-client.git
```
Navigate to the project directory:
```bash
cd lucoin-client
```
Install any necessary dependencies (if applicable).
Configuration
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
