import json
import sys

def find_new_addresses(old_file, new_file):
    with open(old_file, 'r') as f:
        old_data = json.load(f)

    with open(new_file, 'r') as f:
        new_data = json.load(f)

    old_addresses = set(old_data.keys())
    new_addresses = set(new_data.keys())

    new_only = new_addresses - old_addresses

    result = {address: new_data[address] for address in new_only}

    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    old_file = "reimbursement_report_sol_old.json"
    new_file = "reimbursement_report_sol.json"

    find_new_addresses(old_file, new_file)
