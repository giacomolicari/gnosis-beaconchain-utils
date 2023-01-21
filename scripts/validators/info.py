import os, requests
from functools import reduce
from datetime import datetime

API_TOKEN = os.getenv('API_TOKEN')
OWN_VALIDATORS_API_URL = '%s/lighthouse/validators' % os.getenv('OWN_VALIDATORS_API_URL', 'http://localhost:5064')
EXPLORER_VALIDATORS_API_URL = 'https://beacon.gnosischain.com/api/v1/validator/'
GNO_DEPOSIT_AMOUNT = 1 # 32 mGNO = 1 GNO
VALIDATORS_PER_PAGE = 70

def print_info(validators_data):
    """
    validators_data: [Dict{}]
    """
    total_balance = reduce(lambda x, y: x + y['balance'], validators_data, 0)/32000000000
    num_validators = len(validators_data)
    print('Date                : %s' % datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print('Number of Validators: %d' % num_validators)
    print('Total Balance (GNO) : %f' % total_balance)
    print('Net Balance (GNO)   : %f' % (total_balance - num_validators)*GNO_DEPOSIT_AMOUNT)
    print('Slashed             : %d' % reduce(lambda x, y: x + 1 if y['slashed'] else 0, validators_data, 0))

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
    list_validators_request = requests.get(OWN_VALIDATORS_API_URL, headers={'Authorization': 'Bearer ' + API_TOKEN})
    if list_validators_request.ok:
        pubkeys = [x['voting_pubkey'] for x in list_validators_request.json()['data']]

        if len(pubkeys) > VALIDATORS_PER_PAGE:
            chunks = [pubkeys[i:i + VALIDATORS_PER_PAGE] for i in range(0, len(pubkeys), VALIDATORS_PER_PAGE)]

            validators_data = []
            for c in chunks:
                validators_request = requests.get(EXPLORER_VALIDATORS_API_URL + ','.join(c))
                if not validators_request.ok:
                    validators_request.raise_for_status()

                validators_data += validators_request.json()['data']
        else:
            validators_request = requests.get(EXPLORER_VALIDATORS_API_URL + ','.join(pubkeys))
            if not validators_request.ok:
                validators_request.raise_for_status()
            validators_data = validators_request.json()['data']

        print_info(validators_data)
    else:
        # There was an issue with the HTTP request, raise the error
        list_validators_request.raise_for_status()

if __name__ == '__main__':
    main()
