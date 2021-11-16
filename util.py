from typing import List, Tuple
from urllib import parse
import scrypt
import secrets

from algosdk.kmd import KMDClient
from algosdk.v2client.algod import *
from algosdk.future.transaction import *
from algosdk.encoding import _correct_padding, decode_address

from escrow import get_contract
import gc


# The default wallet in a private network in sandbox is named "unencrypted-default-wallet"
# and does not have a password. If you have a wallet locally with a different configuration
# set these parameters appropriately
KMD_WALLET_NAME = "unencrypted-default-wallet"
KMD_WALLET_PASSWORD = ""
KMD_ADDRESS = "http://localhost:4002"
KMD_TOKEN = "a" * 64

drop_file = "drops.csv"

client = AlgodClient("a" * 64, "http://localhost:4001")


tmpl_source = ""  # lazy populated


def populate_teal(seeder: str, addr: str) -> LogicSigAccount:
    global tmpl_source

    if tmpl_source == "":
        # Creates contract source from pyteal with passed
        # "seeder" variable and set it in the global context
        tmpl_source = get_contract(seeder)

    # Replace the template variable in the teal source
    # with the 32 byte address we'll use to verify a signature against
    src = tmpl_source.replace(
        "TMPL_GEN_ADDR", "0x{}".format(decode_address(addr).hex())
    )

    # Compile the populated template contract and return a LogicSsig
    result = client.compile(src)
    return LogicSigAccount(base64.b64decode(result["result"]))


# You may choose to pass your own password/salt here
# for a deterministic key generation. Since this application
# was written for a specific purpose and we are passing the
# key directly, underlying password and salt are not needed
def create_account(pw: bytearray = None, salt: bytearray = None):

    if pw is None:
        pw = secrets.token_bytes(8)

    if salt is None:
        salt = secrets.token_bytes(8)

    key = scrypt.hash(pw, salt, 2048, 8, 1, 32)

    # wipe memory containing pw/salt, not strictly necessary for this use but
    # generally good practice
    del pw
    del salt
    gc.collect()

    sk = SigningKey(key)
    vk = sk.verify_key
    a = encoding.encode_address(vk.encode())
    private_key = base64.b64encode(sk.encode() + vk.encode()).decode()

    return [a, private_key]


# During Ed25519 verify in the teal program, the verify function
# prepends the constant "ProgData" and the address of the program
# that is being evaluated so we need to prepend the same
# bytes prior to signing
def sign_txid(txid: str, escrow: str, key: bytearray) -> bytearray:
    to_sign = (
        b"ProgData"
        + encoding.decode_address(escrow)
        + base64.b32decode(_correct_padding(txid))
    )

    signing_key = SigningKey(key[:32])
    signed = signing_key.sign(to_sign)

    return signed.signature


# Write a list of asa ids to local file
def write_asa_ids(ids: List[int]):
    with open("asa_ids.csv", "w") as f:
        for i in ids:
            f.write("{}\n".format(i))


# Read local file containing asa ids
def read_asa_ids() -> List[int]:
    with open("asa_ids.csv", "r") as f:
        return [int(i) for i in f.read().split("\n")[:-1]]


# Write out the escrows, drop public key, drop private key to a csv
def write_drops(escrows: List[str], pws: List[List[str]], nfts: List[int]):
    with open(drop_file, "w") as f:
        for i in range(len(escrows)):
            f.write("{},{},{},{}\n".format(escrows[i], pws[i][0], pws[i][1], nfts[i]))


# Read in the escrows, drop pk, drop sk (b64)
def read_drops(urlencode: bool) -> List[str]:
    with open(drop_file, "r") as f:
        drops = [drop.split(",") for drop in f.read().splitlines()]

    if urlencode:
        for idx in range(len(drops)):
            drops[idx][2] = parse.quote_plus(drops[idx][2])

    return drops


# Util to get accounts from sandbox wallet for testing
def get_accounts():
    kmd = KMDClient(KMD_TOKEN, KMD_ADDRESS)
    wallets = kmd.list_wallets()

    walletID = None
    for wallet in wallets:
        if wallet["name"] == KMD_WALLET_NAME:
            walletID = wallet["id"]
            break

    if walletID is None:
        raise Exception("Wallet not found: {}".format(KMD_WALLET_NAME))

    walletHandle = kmd.init_wallet_handle(walletID, KMD_WALLET_PASSWORD)

    try:
        addresses = kmd.list_keys(walletHandle)
        privateKeys = [
            kmd.export_key(walletHandle, KMD_WALLET_PASSWORD, addr)
            for addr in addresses
        ]
        kmdAccounts = [(addresses[i], privateKeys[i]) for i in range(len(privateKeys))]
    finally:
        kmd.release_wallet_handle(walletHandle)

    return kmdAccounts
