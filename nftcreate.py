from typing import List

from algosdk import *
from algosdk.v2client.algod import *
from algosdk.future.transaction import *
from util import client


def createNFTs(pk, sk, N=5) -> List[int]:
    created = []
    for _ in range(N):
        created.append(create(pk, sk))
    return created


def create(pk, sk):
    sp = client.suggested_params()
    createTxn = AssetConfigTxn(
        pk,
        sp,
        index=0,
        total=1,
        default_frozen=False,
        asset_name="rando",
        url="https://ipfs.io/ipfs/bafkreic6gizvypdrtzqitvbi5x6tzwvgpi6murkjt4icx4qlxs4m7oslwu",
        strict_empty_address_check=False,
    )
    signed = createTxn.sign(sk)
    txid = client.send_transaction(signed)
    res = wait_for_confirmation(client, txid, 3)
    return res["asset-index"]
