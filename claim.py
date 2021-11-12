from os import write
from typing import List
from algosdk import *
from algosdk.v2client.algod import *
from algosdk.future.transaction import *

from util import client, sign_txid, get_accounts , populate_teal

def simulate_claim(seeder: str, pwaddr: str, pw: str, nft: int):
    [cpk, csk] = generate_claimer()

    print("Claiming on behalf of {}".format(cpk))
    claim(seeder, cpk, csk, pwaddr, pw, nft)

def generate_claimer():
    #create acct
    [sk, pk] = account.generate_account()

    #fund test acct
    sp = client.suggested_params()
    acct = get_accounts()[0]

    payTxn = PaymentTxn(acct[0], sp, pk, int(1e6))
    signed = payTxn.sign(acct[1])

    #Send testnet algos
    txid = client.send_transaction(signed)
    wait_for_confirmation(client, txid, 3)

    #return claimer pk/sk
    return [pk, sk]

def claim(seeder, cpk, csk, pwaddr, pw, nft):

    key = base64.b64decode(pw)

    claim_lsig = populate_teal(seeder, pwaddr)
    close_lsig = populate_teal(seeder, pwaddr)

    sp = client.suggested_params()

    optinTxn = AssetTransferTxn(cpk, sp, cpk, 0, nft)
    claimTxn = AssetTransferTxn(claim_lsig.address(), sp, cpk, 0, nft, cpk)
    closeTxn = PaymentTxn(close_lsig.address(), sp, seeder, 0, close_remainder_to=seeder)

    [goptin, gclaim, gclose] = assign_group_id([optinTxn, claimTxn, closeTxn])

    # Sign _after_ we group, otherwise txid changes
    claim_lsig.lsig.args = [sign_txid(gclaim.get_txid(), claim_lsig.address(), key)]

    signed = [
        goptin.sign(csk),
        LogicSigTransaction(gclaim, claim_lsig),
        LogicSigTransaction(gclose, close_lsig),
    ]

    write_to_file(signed, "tmp.txns")

    txid = client.send_transactions(signed)
    return wait_for_confirmation(client, txid, 3)