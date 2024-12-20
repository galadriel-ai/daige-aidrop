import json
from datetime import datetime

ADDRESS_TO_FILTER = "GRxFdQamfio1NgwbfLfMXAiSNVByYaUHQ5jD6maueFcz"

def filter_and_sort_transfers(transfers_data, address):
    # Extract all transfers
    all_transfers = []
    for transfer_group in transfers_data["transfers"]:
        if transfer_group["success"]:
            all_transfers.extend(transfer_group["data"])

    # Filter by address
    filtered_transfers = [
        transfer for transfer in all_transfers
        if transfer["from_address"] == address or transfer["to_address"] == address
    ]

    print(f"Found {len(filtered_transfers)} transfers for address {address}")
    # Sort transfers by time
    sorted_transfers = sorted(
        filtered_transfers,
        key=lambda x: datetime.strptime(x["time"], "%Y-%m-%dT%H:%M:%S.%fZ")
    )

    return sorted_transfers

def main():
    # Read transfers data from token_transfers.json
    with open('token_transfers.json', 'r') as file:
        transfers_data = json.load(file)

    # Get filtered and sorted transfers
    filtered_sorted_transfers = filter_and_sort_transfers(transfers_data, ADDRESS_TO_FILTER)

    # Print the result
    print(json.dumps(filtered_sorted_transfers, indent=4))

if __name__ == "__main__":
    main()