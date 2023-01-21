import os, requests
from functools import reduce
from datetime import datetime

API_TOKEN = os.getenv('API_TOKEN')
OWN_VALIDATORS_API_URL = '%s/lighthouse/validators' % os.getenv('OWN_VALIDATORS_API_URL', 'http://localhost:5064')
EXPLORER_VALIDATORS_API_URL = 'https://beacon.gnosischain.com/api/v1/validator/'
GNO_DEPOSIT_AMOUNT = 1 # 32 mGNO = 1 GNO

def print_info(validators_data):
    """
    validators_data: {'status': 'OK', 'data': Dict{} }
    """
    total_balance = reduce(lambda x, y: x + y['balance'], validators_data['data'], 0)/32000000000
    num_validators = len(validators_data['data'])
    print('Date                : %s' % datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print('Request Status      : %s' % validators_data['status'])
    print('Number of Validators: %d' % num_validators)
    print('Total Balance (GNO) : %f' % total_balance)
    print('Net Balance (GNO)   : %f' % (total_balance - num_validators)*GNO_DEPOSIT_AMOUNT)
    print('Slashed             : %d' % reduce(lambda x, y: x + 1 if y['slashed'] else 0, validators_data['data'], 0))

def run_checks():
    """
    raise: Exception
    """
    if not API_TOKEN:
        raise Exception('API_TOKEN is not set')

def main():
    """
    Entrypoint: void
    """
    # Run checks before getting started
    run_checks()
    # Get list of validators you own from the Validators API
    validators = requests.get(OWN_VALIDATORS_API_URL, headers={'Authorization': 'Bearer ' + API_TOKEN})
    if validators.ok:
        pubkeys = [x['voting_pubkey'] for x in validators.json()['data']]
        #
        validators_data = requests.get(EXPLORER_VALIDATORS_API_URL + ','.join(pubkeys))
        if not validators_data.ok:
            validators_data.raise_for_status()

        print_info(validators_data.json())
    else:
        # There was an issue with the HTTP request, raise the error
        validators.raise_for_status()

if __name__ == '__main__':
    main()
