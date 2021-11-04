import base64
from types import List
from algosdk import *
import random
import string
import hashlib

tmpl_source = ""

def populate_teal(pw: string) -> str:
    global tmpl_source

    if tmpl_source == "":
        with open("escrow.tmpl.teal", "r") as f:
            tmpl_source = f.read()

    h = hashlib.sha256(pw)

    return tmpl_source.replace(
        "TMPL_HASH_PREIMAGE", 
        "b64({})".format(base64.b64encode(h.digest()))
    )

def fund_accounts(pws: List[str]) -> List[str]:
    """
        fund_accounts takes a list of password strings, hashes the password and 
        hardcodes it into the escrow contract
    """
    for pw in pws:
        source = populate_teal(pw)
        # Create Transactions 
        # Sign with logic
        # Send Transactions
        return


def gen_pw(N=5) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))


def initialize_accounts(N=5):
    # Create n passwords
    pws = [gen_pw(5) for _ in range(N)]
    with open("passwords.csv", "W") as f:
        for pw in pws:
            f.write("{}\n".format(pw))

    # Fund escrow accounts with the password set
    escrows = fund_accounts(pws)
    with open("escrows.csv", "W") as f:
        for escrow in escrows:
            f.write("{}\n".format(escrow))


initialize_accounts(N=1)