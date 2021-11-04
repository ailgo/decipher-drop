# DECIPHER NFT DROP DEMO

## Summary

To support a low touch claiming of NFTs for the Decipher Event.

Some number of Escrow accounts are seeded with algos and an NFT. The Escrow account will allow any account holding the password to claim the NFT given the correct password. The password passed as the first argument in the transaction is hashed using `Sha256` and compared with the hash hardcoded in the contract. 

## Contract Operations

Three operations against the Escrow logic are allowed:

1) Seed: payment from `seeder`, `escrow` opt in to NFT, `seeder` xfer nft to `escrow`

2) Claim: `claimer` opts in to NFT, `escrow` close NFT to `claimer`, `escrow` close algos to `seeder`

3) Recover: `escrow` close NFT to `seeder`, `escrow` close algos to `seeder`, `seeder` dummy payment to act as "cosign"

## Files

*demo.py* - Python logic to run e2e to simulate create nfts, create escrows, create claimers/claim txns, recover unclaimed

*escrow.py* - contains PyTEAL logic to generate template contract

*seed.py* - Python logic to create `escrow` and send initial seed group txns from `seeder`

*claim.py* - Python logic to simulate what a `claimer` will need to send to claim the NFT

*recover.py* - Python logic to simulate what the `seeder` will need to send to recover any unclaimed NFTs


## Running

clone sandbox and run:

```sh
cd sandbox && ./sandbox up dev
```

cd to this repo and run:
```sh
python demo.py
```
