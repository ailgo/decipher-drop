import algosdk, { Transaction } from 'algosdk'
import nacl from 'tweetnacl';

const client = new algosdk.Algodv2("", "http://localhost:4001", "")

export async function collect(secret: string) {
    const key = makeKey(secret)

    const sp = await client.getTransactionParams().do()
    sp.lastRound = sp.firstRound + 10

    //const optinTxn = new Transaction({
    //    from:"",
    //}) 

    //const xferTxn = new Transaction({
    //    from:"", // lsig
    //    ...sp
    //}) 

    //const closeAlgo = new Transaction({
    //closeTxn = PaymentTxn(close_lsig.address(), sp, seeder, 0, close_remainder_to=seeder)
    //})

    nacl.sign.detached(new Uint8Array(), key);
}

// Create secret key from b64 key in url
function makeKey(secret: string): Uint8Array {
    const rawkey = new Uint8Array(Buffer.from(secret, "base64"))
    return rawkey
}

// Send transactions to the network 
function sendWait(txns: algosdk.Transaction[]) {

}