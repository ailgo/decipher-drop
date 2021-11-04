from typing import List
from algosdk import *
from algosdk.v2client.algod import *
from algosdk.future.transaction import *

from sandbox import get_accounts
from seed import populate_teal



client = AlgodClient("a"*64, "http://localhost:4001") 

def get_passwords() -> List[str]:
    with open("passwords.csv", "r") as f:
        return f.readlines()

def get_escrows(seeder: str, pws: List[str]) -> List[str]:
    accts = []
    for pw in pws:
       lsig = populate_teal(seeder, pw) 
       accts.append(lsig.address())
    return accts

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

def claim(seeder, cpk, csk, pw, nft):
    lsig = populate_teal(seeder, pw, [pw])

    sp = client.suggested_params()

    optinTxn = AssetTransferTxn(cpk, sp, cpk, 0, nft)
    claimTxn = AssetTransferTxn(lsig.address(), sp, cpk, 0, nft, cpk)
    closeTxn = PaymentTxn(lsig.address(), sp, seeder, 0, close_remainder_to=seeder)

    [goptin, gclaim, gclose] = assign_group_id([optinTxn, claimTxn, closeTxn])

    signed = [
        goptin.sign(csk),
        LogicSigTransaction(gclaim, lsig),
        gclose.sign(csk)
    ]

    txid = client.send_transactions(signed)
    return wait_for_confirmation(client, txid, 3)

def simulate_claim(seeder: str, pw: str, nft: int):
    [cpk, csk] = generate_claimer()

    print("Claiming on behalf of {}".format(cpk))
    claim(seeder, cpk, csk, pw, nft)