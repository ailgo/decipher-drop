from typing import List

from algosdk import *
from algosdk.v2client.algod import *
from algosdk.future.transaction import *
from util import client, write_asa_ids


def createNFTs(pk, sk, N=5) -> List[int]:
    created = []
    for idx in range(N):
        print("Creating asset #{}".format(idx))
        created.append(create(pk, sk))

    write_asa_ids(created)
    return created


def create(pk, sk):
    sp = client.suggested_params()
    createTxn = AssetConfigTxn(
        pk,
        sp,
        index=0,
        total=1,
        default_frozen=False,
        asset_name="FakeGator",
        url="ipfs://QmPdVFk9aAWEi4JW4LfbJNbnexWk9mrniRcTYf34vxV6bn",
        strict_empty_address_check=False,
    )
    signed = createTxn.sign(sk)
    txid = client.send_transaction(signed)
    res = wait_for_confirmation(client, txid, 3)
    return res["asset-index"]
