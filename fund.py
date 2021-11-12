from typing import List

from pyteal import *
from algosdk.account import address_from_private_key
from algosdk.encoding import decode_address
from algosdk.v2client.algod import *
from algosdk.future.transaction import *

from util import write_drops, create_account, client, populate_teal
from escrow import get_contract


def initialize_accounts(seeder, seeder_key, nfts: List[int]):
    # Create len(nfts) pseudo-accounts
    pws = [create_account() for _ in range(len(nfts))]
    # Fund escrow accounts with the password set
    escrows = fund_accounts(seeder, seeder_key, pws, nfts)
    write_drops(escrows, pws)


# Create and fund the escrow accounts, return list of escrow addresses
def fund_accounts(
    seeder: str, seeder_key: str, pws: List[str], nfts: List[int]
) -> List[str]:
    accts = []
    sp = client.suggested_params()
    for idx in range(len(pws)):
        (addr, _) = pws[idx]
        nftId = nfts[idx]

        lsig = populate_teal(seeder, addr)

        accts.append(lsig.address())

        # seed, opt in, xfer
        payTxn = PaymentTxn(seeder, sp, lsig.address(), int(0.3 * 1e6))
        optInTxn = AssetTransferTxn(lsig.address(), sp, lsig.address(), 0, nftId)
        xferTxn = AssetTransferTxn(seeder, sp, lsig.address(), 1, nftId)

        # group
        grouped = assign_group_id([payTxn, optInTxn, xferTxn])

        # sign
        signed = [
            grouped[0].sign(seeder_key),
            LogicSigTransaction(grouped[1], lsig),
            grouped[2].sign(seeder_key),
        ]

        # send
        txid = client.send_transactions(signed)

        # wait
        result = wait_for_confirmation(client, txid, 2)
        if result["pool-error"] != "":
            print("Failed to send transaction: {}".format(result["pool-error"]))

        print("Confirmed in round {}: {}".format(result["confirmed-round"], result))

    return accts
