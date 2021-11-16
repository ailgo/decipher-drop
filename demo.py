# e2e demo of use
from argparse import ArgumentParser

from nftcreate import createNFTs
from fund import fund_escrows
from claim import simulate_claim
from recover import recover
from util import get_accounts, read_drops, read_asa_ids, write_asa_ids


def demo(args):
    genesis_accts = get_accounts()
    [seeder, seeder_key] = genesis_accts[0]
    print("Using {} to create nfts and seed accounts ".format(seeder))

    if args.create:
        print("Creating {} dummy NFTs".format(args.count))
        createNFTs(seeder, seeder_key, args.count)
    else:
        print("Skipping nft create")

    nftIds = read_asa_ids()

    if args.fund:
        print("Funding escrow accounts to hold nfts")
        fund_escrows(seeder, seeder_key, nftIds)
    else:
        print("Skipping fund")

    drops = read_drops(False)

    if args.claim:
        print("Claiming {} NFTs".format(len(nftIds) - 1))
        for idx in range(len(nftIds) - 1):
            simulate_claim(seeder, drops[idx][1], drops[idx][2], nftIds[idx])
    else:
        print("Skipping claim")

    if args.recover:
        print("Recovering unclaimed NFT")
        recover(seeder, seeder_key, drops[len(nftIds) - 1][1], nftIds[len(nftIds) - 1])
    else:
        print("Skipping recover")


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument(
        "-count", default=5, required=False, type=int, help="Number of NFTs to create"
    )
    parser.add_argument("-create", action="store_true", help="Create Set of NFTs")
    parser.add_argument(
        "-fund", action="store_true", help="Send Algos and NFT to escrow accounts"
    )
    parser.add_argument(
        "-claim",
        action="store_true",
        help="Create accounts and attempt to claim nfts from escrows",
    )
    parser.add_argument(
        "-recover",
        action="store_true",
        help="Use the seeder account to recover nfts from escrows",
    )
    args = parser.parse_args()

    demo(args)
