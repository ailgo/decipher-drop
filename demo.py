#e2e demo of use
from nftcreate import *
from seed import *
from claim import *
from recover import *

N=30
pw_length=10

genesis_accts = get_accounts()
[seeder, seeder_key] = genesis_accts[0]
print("Using {} to create nfts and seed accounts ".format(seeder))

print ("Creating {} dummy NFTs".format(N))
nftIds = createNFTs(seeder, seeder_key, N)
print("Created {}".format(nftIds))

print("Creating escrow accounts to hold nfts")
initialize_accounts(seeder, seeder_key, nftIds, pw_length)

#print("Claiming {} NFTs".format(N-1))
drops = get_drops(False)
print(drops)
for drop in drops:
    print("http://localhost:3000?escrow={}&addr={}&secret={}".format(drop[0], drop[1], drop[2]))

#for idx in range(N-1):
#    simulate_claim(seeder, drops[idx][0], drops[idx][1], drops[idx][2], nftIds[idx])
#
#
#print("Recovering unclaimed NFT")
#recover(seeder, seeder_key, drops[-1][1], nftIds[-1])
