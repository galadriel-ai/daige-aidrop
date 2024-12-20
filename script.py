import json
import os

import requests

TOKEN_ADDRESS = "A9LfgjnWUxujnpud5E3ssKbnNiS1nxRC8Gh74hJTpump"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MzQ2MDQzNDQ3MjUsImVtYWlsIjoibWFjaWVqQGdhbGFkcmllbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJhcGlWZXJzaW9uIjoidjIiLCJpYXQiOjE3MzQ2MDQzNDR9.iwpUyOdUeMH747C3rYhp6rpsYA2nj9o1FH5ilGiWkEI"  # Your API key
TRANSACTIONS_URL = "https://pro-api.solscan.io/v2.0/account/transactions"
ADDRESS = "A9LfgjnWUxujnpud5E3ssKbnNiS1nxRC8Gh74hJTpump"
TX_DETAILS_URL= "https://pro-api.solscan.io/v2.0/transaction/detail"

def fetch_and_store_tx_details(tx_hash):
    headers = {"token": API_KEY}
    params = {
        'tx': tx_hash,
    }
    response = requests.get(TX_DETAILS_URL, params=params, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching transactions: {response.status_code}")
        return

    filename = "transaction_details.json"
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            json.dump({"transactions": []}, file)

    data = response.json()
    with open(filename, 'r+') as file:
        file_data = json.load(file)
        file_data["transactions"].append(data)
        file.seek(0)
        json.dump(file_data, file, indent=4)

def save_transactions_to_file(tx_hash):
    # Save transaction hashes to transactions.json
    json_filename = "transactions.json"
    if not os.path.exists(json_filename):
        with open(json_filename, 'w') as file:
            json.dump({"transactions": []}, file)

    with open(json_filename, 'r+') as file:
        file_data = json.load(file)
        file_data["transactions"].append(tx_hash)
        file.seek(0)
        json.dump(file_data, file, indent=4)

def fetch_transactions(address, limit):
    headers = {"token": API_KEY}
    transactions = []
    before = None

    while True:
        params = {
            'address': address,
            'limit': limit
        }
        if before:
            params['before'] = before

        response = requests.get(TRANSACTIONS_URL, params=params, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching transactions: {response.status_code}")
            break

        data = response.json()
        if not data['success'] or not data['data']:
            break

        for tx in data['data']:
            tx_hash = tx['tx_hash']
            transactions.append(tx_hash)
            # Save transaction to a file
            save_transactions_to_file(tx_hash)

            # Process transaction details sequentially
            fetch_and_store_tx_details(tx_hash)

        # Update the 'before' parameter for the next batch
        before = data['data'][-1]['tx_hash']

        # If fewer results are returned than the limit, exit the loop
        if len(data['data']) < limit:
            break

    return transactions

# Main function
def main():
    fetch_transactions(TOKEN_ADDRESS, 40)

if __name__ == "__main__":
    main()
