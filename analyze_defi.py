import json
from collections import defaultdict

# Sample DeFi activities data (replace with actual data)
def process_defi_activities(defi_activities, token_contract):
    address_reports = defaultdict(lambda: {'gain': 0, 'loss': 0})
    token_contracts = set()
    report = {} # Address to report

    for data in defi_activities:
        activity = data['data']
        address = activity['from_address']
        value = activity['value']
        activity_type = activity['activity_type']
        token1 = activity['routers']['token1']
        token2 = activity['routers']['token2']

        # Track tokens involved
        token_contracts.add(token1)
        if token2:
            token_contracts.add(token2)

        # Calculate profit/loss based on activity type for each address
        if activity_type == 'ACTIVITY_TOKEN_SWAP':
            address_reports[address]['gain'] += value
        elif activity_type == 'ACTIVITY_TOKEN_REMOVE_LIQ':
            address_reports[address]['gain'] += value
        elif activity_type == 'ACTIVITY_TOKEN_ADD_LIQ':
            # Adding liquidity locks value, treat as a loss if related to the token contract
            if token1 == token_contract or token2 == token_contract:
                address_reports[address]['loss'] += value

    # Summarize results for each address
    report = {}
    for address, values in address_reports.items():
        net_result = values['gain'] - values['loss']
        report[address] = {
            'total_gain': values['gain'],
            'total_loss': values['loss'],
            'net_result': net_result
        }

    return report

# Example usage
if __name__ == "__main__":
    token_contract = "A9LfgjnWUxujnpud5E3ssKbnNiS1nxRC8Gh74hJTpump"
    with open('defi_activities.json', 'r') as file:
        defi_activities = json.load(file)['transfers']

    report = process_defi_activities(defi_activities, token_contract)
    print(json.dumps(report, indent=4))