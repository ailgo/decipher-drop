#e2e demo of use
from nftcreate import *
from fund import *
from claim import *
from recover import *
from util import *

N=5

genesis_accts = get_accounts()
[seeder, seeder_key] = genesis_accts[0]
print("Using {} to create nfts and seed accounts ".format(seeder))

print ("Creating {} dummy NFTs".format(N))
nftIds = createNFTs(seeder, seeder_key, N)
print("Created {}".format(nftIds))

print("Creating escrow accounts to hold nfts")
initialize_accounts(seeder, seeder_key, nftIds)

base_url = "http://localhost:3000"
#base_url = "https://algorand-devrel.github.io/decipher-tickets"
drops = read_drops(False)
print(drops)
for drop in drops:
    print("{}?escrow={}&addr={}&secret={}".format(base_url, drop[0], drop[1], drop[2]))

print("Claiming {} NFTs".format(N-1))
for idx in range(N-1):
    simulate_claim(seeder, drops[idx][1], drops[idx][2], nftIds[idx])

print("Recovering unclaimed NFT")
recover(seeder, seeder_key, drops[-1][1], nftIds[-1])