from os import write
from typing import List
from algosdk import *
from algosdk.encoding import decode_address, _correct_padding, _undo_padding, is_valid_address
from algosdk.v2client.algod import *
from algosdk.future.transaction import *

from sandbox import get_accounts
from seed import get_address_from_pw, populate_teal


client = AlgodClient("a"*64, "http://localhost:4001") 

def get_drops(decode: bool) -> List[str]:

    with open("drops.csv", "r") as f:
        drops = [drop.split(",") for drop in f.read().splitlines()]


    if decode:
        import urllib.parse
        for idx in range(len(drops)):
            drops[idx][2] = parse.unquote_plus(drops[idx][2])

    return drops

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

def claim(seeder, cpk, csk, escrow, pwaddr, pw, nft):

    key = base64.b64decode(pw)

    claim_lsig = populate_teal(seeder, pwaddr)
    close_lsig = populate_teal(seeder, pwaddr)

    sp = client.suggested_params()

    optinTxn = AssetTransferTxn(cpk, sp, cpk, 0, nft)
    claimTxn = AssetTransferTxn(claim_lsig.address(), sp, cpk, 0, nft, cpk)
    closeTxn = PaymentTxn(close_lsig.address(), sp, seeder, 0, close_remainder_to=seeder)

    [goptin, gclaim, gclose] = assign_group_id([optinTxn, claimTxn, closeTxn])

    to_sign = (
        b"ProgData" +
        encoding.decode_address(claim_lsig.address()) +
        base64.b32decode(_correct_padding(gclaim.get_txid()))
    )

    signing_key = SigningKey(key[:32])
    signed      = signing_key.sign(to_sign)

    claim_lsig.lsig.args = [signed.signature]

    signed = [
        goptin.sign(csk),
        LogicSigTransaction(gclaim, claim_lsig),
        LogicSigTransaction(gclose, close_lsig),
    ]

    txid = client.send_transactions(signed)
    return wait_for_confirmation(client, txid, 3)

def simulate_claim(seeder: str, escrow: str, pwaddr: str, pw: str, nft: int):
    [cpk, csk] = generate_claimer()

    print("Claiming on behalf of {}".format(cpk))
    claim(seeder, cpk, csk, escrow, pwaddr, pw, nft)
