from types import List
import base64
import string
import hashlib
import random

from pyteal import *
from escrow import escrow
from algosdk import *
from algosdk.v2client.algod import *
from algosdk.future.transaction import *


client = AlgodClient("a"*64, "http://localhost:4001") 

pw_length = 5
seeder = "BLKW2VKNJMIXYB2STAQHWTUIIERBKOSU2ZPJFP7NJWWPKQAJMQMJ3RRSZM"
seeder_key = ""

tmpl_source = "" # lazy populated


def populate_teal(pw: string) -> str:
    global tmpl_source

    if tmpl_source == "":
        tmpl_source = compileTeal(
            escrow(seeder), 
            mode=Mode.Signature, 
            version=5
        )

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

    global seeder, seeder_key

    sp = client.suggested_params()
    for pw in pws:
        nftId = 0

        lsig = LogicSigAccount(populate_teal(pw))

        # Create Transactions 

        # seed, opt in, xfer
        payTxn = PaymentTxn(seeder, sp, int(0.3*10e6), lsig.address())
        optInTxn = AssetTransferTxn(lsig.address(), sp, lsig.address(), 0, nftId)
        xferTxn = AssetTransferTxn(seeder, sp, lsig.address(), 0, nftId)

        # group
        grouped = assign_group_id([payTxn, optInTxn, xferTxn])

        # sign 
        signed = [
            grouped[0].sign(seeder_key), 
            transaction.LogigSigTransaction(grouped[1], lsig), 
            grouped[2].sign(seeder_key)
        ]

        # send
        txid = client.send_transactions(signed)

        # wait 
        result = wait_for_confirmation(client, txid, 2)
        if result['pool-error'] != "":
            print("Failed to send transaction: {}".format(result['pool-error']))            

        print("Confirmed in round: {}".format(result['confirmed-round']))


def gen_pw(N=5) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))


def initialize_accounts(N=5):
    global pw_length

    # Create n passwords
    pws = [gen_pw(pw_length) for _ in range(N)]
    with open("passwords.csv", "W") as f:
        for pw in pws:
            f.write("{}\n".format(pw))

    # Fund escrow accounts with the password set
    escrows = fund_accounts(pws)
    with open("escrows.csv", "W") as f:
        for escrow in escrows:
            f.write("{}\n".format(escrow))


initialize_accounts(N=1)