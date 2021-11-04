from pyteal import *

def escrow(seed_addr: str):
    seeder = Bytes(seed_addr)
    is_valid_seed = And(
        Global.group_size() == Int(3),

        # Seed with funds
        Gtxn[0].type_enum() == TxnType.Payment,
        Gtxn[0].sender() == seeder,
        Gtxn[0].amount() == Int(int(0.3 * 10e6)), # 0.3 algos
        Gtxn[0].close_remainder_to() == Global.zero_address(),

        # Opt escrow into asset
        Gtxn[1].type_enum() == TxnType.AssetTransfer,
        Gtxn[1].asset_amount() == Int(0),
        Gtxn[1].asset_receiver() == Gtxn[1].sender(),
        Gtxn[1].asset_receiver() == Gtxn[0].receiver(),

        # Xfer asset from creator to escrow
        Gtxn[2].type_enum() == TxnType.AssetTransfer,
        Gtxn[2].asset_amount() == Int(1),
        Gtxn[2].asset_receiver() == Gtxn[0].receiver(),
        Gtxn[2].sender() == Gtxn[0].sender(),
        Gtxn[2].asset_close_to() == Global.zero_address(),
        Gtxn[2].xfer_asset() == Gtxn[1].xfer_asset()
    )

    is_valid_claim = And(
        Global.group_size() == Int(3),

        Sha256(Arg(0)) == Tmpl.Bytes("TMPL_HASH_PREIMAGE"),

        # Account Opt in
        Gtxn[0].type_enum() == TxnType.AssetTransfer,
        Gtxn[0].sender() == Gtxn[0].asset_receiver(),
        Gtxn[0].asset_amount() == Int(0),
        Gtxn[0].asset_close_to() == Global.zero_address(),

        # Close Asset to Account 
        Gtxn[1].type_enum() == TxnType.AssetTransfer,
        Gtxn[1].asset_amount() == Int(0),
        Gtxn[1].xfer_asset() == Gtxn[0].xfer_asset(),
        Gtxn[1].asset_close_to() == Gtxn[0].sender(),

        # Close algos back to seeder
        Gtxn[2].type_enum() == TxnType.Payment,
        Gtxn[2].amount() == Int(0),
        Gtxn[2].close_remainder_to() == seeder
    )

    is_valid_recover = And(
        Global.group_size() == Int(3),


        # Close out asset
        Gtxn[0].type_enum() == TxnType.AssetTransfer,
        Gtxn[0].asset_amount() == Int(0),
        Gtxn[0].asset_close_to() == seeder,

        # Close out algos 
        Gtxn[1].type_enum() == TxnType.Payment,
        Gtxn[1].amount() == Int(0),
        Gtxn[1].close_remainder_to() == seeder,

        # Make sure seeder cosigned
        Gtxn[2].type_enum() == TxnType.Payment,
        Gtxn[2].sender() == seeder,
        Gtxn[2].receiver() == seeder,
        Gtxn[2].amount() == Int(0),
        Gtxn[2].close_remainder_to() == Global.zero_address(),
        Gtxn[2].rekey_to() == Global.zero_address()
    )

    return Or(
       is_valid_seed,
       is_valid_claim,
       is_valid_recover,
    )

if __name__=="__main__":
    seed_addr = "BLKW2VKNJMIXYB2STAQHWTUIIERBKOSU2ZPJFP7NJWWPKQAJMQMJ3RRSZM"
    with open("escrow.tmpl.teal", "w") as f:
        f.write(compileTeal(
            escrow(seed_addr), 
            mode=Mode.Signature, 
            version=5
        ))
