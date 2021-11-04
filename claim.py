from types import List
from algosdk import *


def get_passwords() -> List[str]:
    pass

def get_escrows() -> List[str]:
    pass

def generate_claimer():
    #create acct
    [sk, pk] = account.generate_account()

    #fund test acct

    #Send testnet algos

    #return pk/sk
    return pk, sk

def simulate_claim(pk, sk, pw, escrow) :

    # Create txns to claim
    pass


if __name__ == "__main__":
    pws = get_passwords()
    escrows = get_escrows()

    for idx in range(len(pws)):
        [pk, sk] = generate_claimer()
        simulate_claim(pk, sk, pws[idx], escrows[idx])