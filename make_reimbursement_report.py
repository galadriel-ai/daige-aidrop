import json
from collections import defaultdict
from datetime import datetime

def filter_and_sort_transfers(transfers_data, address):
    # Extract all transfers
    all_transfers = []
    for transfer_group in transfers_data["transfers"]:
        if transfer_group["success"]:
            all_transfers.extend(transfer_group["data"])

    # Filter by address
    filtered_transfers = [
        transfer for transfer in all_transfers
        if transfer["from_address"] == address
    ]

    # Sort transfers by time
    sorted_transfers = sorted(
        filtered_transfers,
        key=lambda x: datetime.strptime(x["time"], "%Y-%m-%dT%H:%M:%S.%fZ")
    )

    return sorted_transfers


# Token mapping
TOKEN_MAP = {
    "So11111111111111111111111111111111111111112": "SOL",
    "A9LfgjnWUxujnpud5E3ssKbnNiS1nxRC8Gh74hJTpump": "Daige"
}


# Sample DeFi activities data (replace with actual data)
def process_defi_activities(defi_activities, token_contract):
    activity_list = []

    if isinstance(defi_activities, str):
        defi_activities = json.loads(defi_activities)

    for activity in defi_activities:
        if not isinstance(activity, dict):
            continue  # Skip if the activity is not a valid dictionary

        activity_type = activity.get('activity_type')
        value = activity.get('value', 0)
        routers = activity.get('routers', {})

        router_info = {
            'from': {
                'token': TOKEN_MAP.get(routers.get('token1'), routers.get('token1')),
                'amount': routers.get('amount1')
            },
            'to': {
                'token': TOKEN_MAP.get(routers.get('token2'), routers.get('token2')),
                'amount': routers.get('amount2')
            }
        }

        activity_list.append((activity_type, value, router_info))

    return activity_list

def calculate_daige_loss(activity_list):
    net = 0

    for activity_type, value, router_info in activity_list:
        # Swap from Daige to SOL - gain
        if activity_type == 'ACTIVITY_TOKEN_SWAP' and router_info['from']['token'] == 'Daige':
            net += value
        # Swap from SOL to Daige - loss
        if activity_type == 'ACTIVITY_TOKEN_SWAP' and router_info['from']['token'] == 'SOL':
            net -= value
        if activity_type == 'ACTIVITY_AGG_TOKEN_SWAP' and router_info['from']['token'] == 'Daige':
            net += value
        # Swap from SOL to Daige - loss
        if activity_type == 'ACTIVITY_AGG_TOKEN_SWAP' and router_info['from']['token'] == 'SOL':
            net -= value

    return net


def convert_to_sol(pairs, sol_price):
    sol_pairs = {}
    for address, usd_amount in pairs:
        sol_amount = usd_amount / sol_price
        sol_pairs[address] = sol_amount

    return sol_pairs


def main():
    # Read transfers data from token_transfers.json
    with open('defi_activities.json', 'r') as file:
        transfers_data = json.load(file)

    with open('addresses.txt', 'r') as addr_file:
        addresses = [line.strip() for line in addr_file if line.strip()]

    # Remove duplicates
    unique_addresses = list(set(addresses))

    # Overwrite addresses.txt with unique addresses
    with open('addresses.txt', 'w') as addr_file:
        addr_file.write('\n'.join(unique_addresses) + '\n')

    address_reports = {}
    for address in addresses:
        filtered_sorted_transfers = filter_and_sort_transfers(transfers_data, address)
        activity_list = process_defi_activities(filtered_sorted_transfers,"A9LfgjnWUxujnpud5E3ssKbnNiS1nxRC8Gh74hJTpump")
        loss = calculate_daige_loss(activity_list)
        address_reports[address] = loss

    # Calculate total reimbursement and top 10 addresses with highest loss
    total_reimbursement = sum(address_reports.values())
    top_10_losses = sorted(address_reports.items(), key=lambda x: x[1])[:10]

    print(f"Total reimbursement to pay: {total_reimbursement}")
    print("Top 10 addresses with highest losses:")
    for address, amount in top_10_losses:
        print(f"{address}: {amount}")

    with open('reimbursement_report.json', 'w') as report_file:
        json.dump(address_reports, report_file, indent=4)

    report_sol = convert_to_sol(address_reports.items(), 190)
    with open('reimbursement_report_sol.json', 'w') as report_file:
        json.dump(report_sol, report_file, indent=4)

if __name__ == "__main__":
    main()