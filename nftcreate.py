from algosdk import *

def create():
    pass

def createNFTs(N=5)->List[int]:
    created = []
    for _ in range(N):
        created.push(create())

    return created

