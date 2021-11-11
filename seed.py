from typing import List
import base64
import string
import hashlib
import random

from pyteal import *
from algosdk.account import address_from_private_key
from algosdk.encoding import decode_address
from algosdk.v2client.algod import *
from algosdk.future.transaction import *

from escrow import get_contract

import scrypt



client = AlgodClient("a"*64, "http://localhost:4001")


tmpl_source = "" # lazy populated
def populate_teal(seeder: str, addr: str) -> str:
    global tmpl_source

    if tmpl_source == "":
        tmpl_source = get_contract(seeder)


    src = tmpl_source.replace(
        "TMPL_GEN_ADDR",
        "0x{}".format(decode_address(addr).hex())
    )

    result = client.compile(src)

    return LogicSigAccount(base64.b64decode(result['result']))


def fund_accounts(seeder: str, seeder_key: str, pws: List[str], nfts: List[int]) -> List[str]:
    """
        fund_accounts takes
            the seed acddress and ,
            a list of generated pk/sks,
            and nft ids
        populate_teal returns the populated logic sig
        it hash the password, add it to the contract, compile the contract, and return
    """
    accts = []
    sp = client.suggested_params()
    for idx in range(len(pws)):

        pw = pws[idx]
        nftId = nfts[idx]

        addr, _ = get_address_from_pw(pw)

        lsig = populate_teal(seeder, pw)

        accts.append(lsig.address())

        # seed, opt in, xfer
        payTxn = PaymentTxn(seeder, sp, lsig.address(), int(0.3*10e6))
        optInTxn = AssetTransferTxn(lsig.address(), sp, lsig.address(), 0, nftId)
        xferTxn = AssetTransferTxn(seeder, sp, lsig.address(), 1, nftId)

        # group
        grouped = assign_group_id([payTxn, optInTxn, xferTxn])

        # sign 
        signed = [
            grouped[0].sign(seeder_key),
            LogicSigTransaction(grouped[1], lsig),
            grouped[2].sign(seeder_key)
        ]

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


salt = b'aa1f2d3f4d23ac44e9c5a6c3d8f9ee8c'
def get_address_from_pw(pw: str):
    key = scrypt.hash(pw, salt, 2048, 8, 1, 32)

    sk = SigningKey(key)
    vk = sk.verify_key
    a = encoding.encode_address(vk.encode())
    private_key = base64.b64encode(sk.encode() + vk.encode()).decode()

    return [a, private_key]

def initialize_accounts(seeder, seeder_key, nfts: List[int], pw_length=5):
    # Create n passwords
    pws = [get_address_from_pw(gen_pw(pw_length)) for _ in range(len(nfts))]
    # Fund escrow accounts with the password set
    escrows = fund_accounts(seeder, seeder_key, pws, nfts)

    with open("drops.csv", "w") as f:
        for i in range(len(nfts)):
            f.write("{},{},{}\n".format(escrows[i], pws[i][0], pws[i][1]))

