from typing import List
import base64
import string
import hashlib
import random

from pyteal import *
from algosdk import *
from algosdk.v2client.algod import *
from algosdk.future.transaction import *

from escrow import escrow


client = AlgodClient("a"*64, "http://localhost:4001") 

tmpl_source = "" # lazy populated
def populate_teal(seeder: str, pw: str, args=None) -> str:
    global tmpl_source

    if tmpl_source == "":
        tmpl_source = compileTeal(
            escrow(seeder), 
            mode=Mode.Signature, 
            version=5
        )

    h = hashlib.sha256(pw.encode('utf-8'))

    src = tmpl_source.replace(
        "TMPL_HASH_PREIMAGE", 
        "0x{}".format(h.hexdigest())
    )
    with open("tmp.teal", "w") as f:
        f.write(src)

    result = client.compile(src)

    return LogicSigAccount(base64.b64decode(result['result']), args=args)


def fund_accounts(seeder: str, seeder_key: str, pws: List[str], nfts: List[int]) -> List[str]:
    """
        fund_accounts takes the seed acddress and key, a list of password strings, and nft ids
        populate_teal returns the populated logic sig
        it hash the password, add it to the contract, compile the contract, and return
    """
    accts = []
    sp = client.suggested_params()
    for idx in range(len(pws)):

        pw = pws[idx]
        nftId = nfts[idx]
        lsig = populate_teal(seeder, pw)

        accts.append(lsig.address())

        # seed, opt in, xfer
        payTxn = PaymentTxn(seeder, sp, lsig.address(), int(0.3*10e6))
        optInTxn = AssetTransferTxn(lsig.address(), sp, lsig.address(), 0, nftId)
        xferTxn = AssetTransferTxn(seeder, sp, lsig.address(), 1, nftId)

        print(lsig.address())

        # group
        grouped = assign_group_id([payTxn, optInTxn, xferTxn])


        # sign 
        signed = [
            grouped[0].sign(seeder_key), 
            LogicSigTransaction(grouped[1], lsig), 
            grouped[2].sign(seeder_key)
        ]

        write_to_file(signed, "tmp.txns")

        # send
        txid = client.send_transactions(signed)

        # wait 
        result = wait_for_confirmation(client, txid, 2)
        if result['pool-error'] != "":
            print("Failed to send transaction: {}".format(result['pool-error']))            

        print("Confirmed in round {}: {}".format(result['confirmed-round'], result))

    return accts


def gen_pw(N=5) -> str:
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))


def initialize_accounts(seeder, seeder_key, nfts: List[int], pw_length=5):
    # Create n passwords
    pws = [gen_pw(pw_length) for _ in range(len(nfts))]
    with open("passwords.csv", "w") as f:
        f.write("\n".join(pws))

    # Fund escrow accounts with the password set
    escrows = fund_accounts(seeder, seeder_key, pws, nfts)
    with open("escrows.csv", "w") as f:
        f.write("\n".join(escrows))