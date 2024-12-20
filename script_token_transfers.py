import json
import os
import requests
import os
import json
from threading import Thread, Lock
from queue import Queue
import requests

TOKEN_ADDRESS = "A9LfgjnWUxujnpud5E3ssKbnNiS1nxRC8Gh74hJTpump"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MzQ2MDQzNDQ3MjUsImVtYWlsIjoibWFjaWVqQGdhbGFkcmllbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJhcGlWZXJzaW9uIjoidjIiLCJpYXQiOjE3MzQ2MDQzNDR9.iwpUyOdUeMH747C3rYhp6rpsYA2nj9o1FH5ilGiWkEI"  # Your API key
TOKEN_TRANSFER_URL= "https://pro-api.solscan.io/v2.0/token/transfer"

lock = Lock()
transaction_queue = Queue()
output_lock = Lock()
results = {}
def transaction_worker(task_queue):
    while True:
        page_number = task_queue.get()
        if page_number is None:  # Sentinel value to stop the thread
            break

        print(f"fetching page {page_number}")

        headers = {"token": API_KEY}
        params = {
            'address': TOKEN_ADDRESS,
            'page': page_number,
            'page_size': 100
        }

        response = requests.get(TOKEN_TRANSFER_URL, params=params, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching transactions on page {page_number}: {response.status_code}")
            task_queue.task_done()
            continue

        data = response.json()
        if not data.get('success') or not data.get('data'):
            task_queue.task_done()
            continue

        with output_lock:
            results[page_number] = data

        task_queue.task_done()

def save_ordered_transactions():
    # Save ordered transaction hashes to a file
    filename = "token_transfers.json"
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            json.dump({"transfers": []}, file)

    with open(filename, 'r+') as file:
        file_data = json.load(file)
        ordered_results = []
        for page in sorted(results.keys()):
            ordered_results.append(results[page])

        file_data["transfers"].extend(ordered_results)
        file.seek(0)
        json.dump(file_data, file, indent=4)

def fetch_transfers():
    task_queue = Queue()
    threads = []
    total_pages = 476  # Based on https://solscan.io/token/A9LfgjnWUxujnpud5E3ssKbnNiS1nxRC8Gh74hJTpump

    # Start worker threads
    for _ in range(10):
        thread = Thread(target=transaction_worker, args=(task_queue,))
        thread.start()
        threads.append(thread)

    # Enqueue tasks for each page
    for page_number in range(1, total_pages + 1):
        task_queue.put(page_number)

    # Wait for all tasks to be processed
    task_queue.join()

    # Stop worker threads
    for _ in threads:
        task_queue.put(None)
    for thread in threads:
        thread.join()

    # Save ordered transactions to a file
    save_ordered_transactions()

# Main function
def main():
    fetch_transfers()

if __name__ == "__main__":
    main()
