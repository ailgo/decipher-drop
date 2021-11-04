from algosdk import *
from algosdk.future.transaction import *
from algosdk.future.transaction import AssetTransferTxn, PaymentTxn, assign_group_id
from algosdk.v2client.algod import *
from seed import populate_teal

client = AlgodClient("a"*64, "http://localhost:4001") 

def recover(seeder: str, seeder_key: str, pw: str, nft: int):

    lsig = populate_teal(seeder, pw)

    # Create txns to reclaim asset back to seeder
    sp = client.suggested_params()

    cosignTxn = PaymentTxn(seeder, sp, seeder, 0)
    nftClose = AssetTransferTxn(lsig.address(), sp, seeder, 0, nft, close_assets_to=seeder)
    algoClose = PaymentTxn(lsig.address(), sp, seeder, 0, close_remainder_to=seeder)

    grouped = assign_group_id([cosignTxn, nftClose, algoClose])

    signed = [
       grouped[0].sign(seeder_key),
       LogicSigTransaction(grouped[1], lsig),
       LogicSigTransaction(grouped[2], lsig)
    ]

    txid = client.send_transactions(signed)
    
    return wait_for_confirmation(client, txid, 3)
