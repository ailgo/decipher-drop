from claim import get_passwords, get_escrows
from algosdk import *

def recover(escrow: str):
    # Create txns to reclaim asset back to seeder

    # Asset Close to seeder
    # Algo close to seeder
    # 0 amt pay txn

    pass

if __name__ == "__main__":
    escrows = get_escrows() 

    for escrow in escrows:
        recover(escrow)




