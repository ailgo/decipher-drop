# PASSWORD BASED NFT DROP DEMO

## Summary

Often a creator will want to distribute the NFTs they've created in a pseudo-random way with little interaction from the receiver. This processes is made more difficult because a receiver needs to opt into the ASA ahead of time and it can be diffuclt to coordinate which ASA id they'd need to opt into.

This repository demonstrates the use of a Smart Signature to hold an NFT and an Ed25519 signature validation to ensure security.  

## Details 

Some number of Escrow accounts are created and funded with algos and an NFT. Each escrow account has a hardcoded, unique, ed25519 keypair that will allow any account passing a valid, matching, ed25519 signature of the claim transaction id to claim the NFT. 

In order to claim the NFT, the user is passed the secret key for the relevant escrow account. The key is then used to sign the transaction id of the second transaction in the the atomic group and the signature is passed as the 0th argument.  

The contract validates that the signature passed is a valid for the public key it has hardcoded and approves the transaction.

In this demo there is also the concept of a "recover" transaction which will allow the funding account to reclaim any unclaimed NFTs.


## Contract Operations

Three operations against the Escrow logic are allowed:

1) Fund: payment from `seeder`, `escrow` opt in to NFT, `seeder` xfer nft to `escrow`

2) Claim: `claimer` opts in to NFT, `escrow` close NFT to `claimer`, `escrow` close algos to `seeder`

3) Recover: `escrow` close NFT to `seeder`, `escrow` close algos to `seeder`, `seeder` dummy payment to act as "cosign"

## Files

*escrow.py* - contains PyTEAL logic to generate template contract

*fund.py* - Functions to create `escrow` and send initial seed group txns from `seeder`

*claim.py* - Functions to simulate what a `claimer` will need to send to claim the NFT

*recover.py* - Functions to simulate what the `seeder` will need to send to recover any unclaimed NFTs

*nftcreate.py* - Functions to create NFTs to place in escrow 

*demo.py* - Python logic to run e2e to simulate NFTs creation, escrow NFT and algo funding, run NFT claim txns, recover unclaimed NFTs

*util.py* - Some utility related functions that are used in multiple places

## Running

clone sandbox and run:
```sh
cd sandbox && ./sandbox up dev
```

cd to this repo and run:
```sh
python demo.py -h
```


```sh
usage: demo.py [-h] [-count COUNT] [-create] [-fund] [-claim] [-recover]

optional arguments:
  -h, --help    show this help message and exit
  -count COUNT  Number of NFTs to create
  -create       Create Set of NFTs
  -fund         Send Algos and NFT to escrow accounts
  -claim        Create accounts and attempt to claim nfts from escrows
  -recover      Use the seeder account to recover nft from escrow
```

to run through the full demo
```sh
python demo.py -count 10 -create -fund -claim -recover
```
