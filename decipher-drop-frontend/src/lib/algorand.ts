import algosdk, { encodeUnsignedTransaction, generateAccount, LogicSigAccount, makePaymentTxnWithSuggestedParams, Transaction, TransactionType } from 'algosdk'
import { SessionWallet } from 'algorand-session-wallet';
import base32 from 'hi-base32';
import nacl from 'tweetnacl';
//@ts-ignore
import escrow_template from './contracts/escrow.tmpl.teal'


export const conf = {
    seeder: "LSQUHBU6G6NN4NIZ2ANFPBTXPP2DYLSA3N5R2ZHD6JA7UIRVT2C7QU23FQ",
    network: ""
}

const mnemonic = "attend brisk rather library panda wood course put gadget dismiss tackle luxury grocery assume vocal beyond festival venue wrong large farm expect wheat about similar"

const client = new algosdk.Algodv2("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "http://localhost", 4001)

interface SignedTxn {
    txID: string,
    blob: Uint8Array
}

export interface NFT {
    id: number
    url: string
    name: string
}

export async function collect(sw: SessionWallet, asaId: number, escrow: string, addr: string, secret: string): Promise<SignedTxn[]> {

    //const claimer = sw.getDefaultAccount()
    const sk = algosdk.mnemonicToSecretKey(mnemonic)
    const claimer = sk.addr

    const lsig = await getLsig(addr)

    const sp = await client.getTransactionParams().do()
    sp.lastRound = sp.firstRound + 10

    const optinTxn = new Transaction({
        from:claimer,
        to:claimer,
        assetIndex: asaId,
        type:TransactionType.axfer,
        amount:0,
        ...sp
    }) 

    const xferTxn = new Transaction({
        from:escrow,
        to:claimer,
        assetIndex: asaId,
        type:TransactionType.axfer,
        amount:0,
        closeRemainderTo: claimer,
        ...sp
    }) 

    const closeTxn = new Transaction({
        from:escrow,
        to:conf.seeder,
        type:TransactionType.pay,
        amount:0,
        closeRemainderTo: conf.seeder,
        ...sp
    })

    const grouped = [optinTxn, xferTxn, closeTxn]

    algosdk.assignGroupID(grouped)

    lsig.lsig.args = [createSignature(xferTxn.txID(), escrow, secret)]

    const s_xfer = algosdk.signLogicSigTransactionObject(xferTxn, lsig)
    const s_close = algosdk.signLogicSigTransactionObject(closeTxn, lsig)

    //const [s_optin, /*xfer*/ , /*close*/] = await sw.signTxn(grouped)
    const s_optin = algosdk.signTransaction(optinTxn, sk.sk)

    return [s_optin, s_xfer, s_close]
}

function createSignature(txid: string, escrow: string, secret: string): Uint8Array {
    const pd    = Buffer.from("ProgData")
    const addr  = algosdk.decodeAddress(escrow).publicKey
    const btxid = base32.decode.asBytes(txid)

    const toSign = new Uint8Array(pd.length + addr.length + btxid.length)
    toSign.set(pd, 0)
    toSign.set(addr, pd.length)
    toSign.set(btxid, pd.length + addr.length)

    const sk = Buffer.from(secret, "base64")
    return nacl.sign.detached(toSign, sk);
}

export async function getNFT(asaId: number): Promise<NFT> {
    const asa = await client.getAssetByID(asaId).do()
    const p = asa['params']
    console.log(asa)
    return {
        id:   asaId,
        url:  p['url'],
        name: p['name']
    } as NFT
}

export async function getAsaId(escrow: string): Promise<number> {
    const ai = await client.accountInformation(escrow).do()
    if(ai['assets'].length !== 1) throw Error("wat")
    return ai['assets'][0]['asset-id']
}

async function getLsig(addr: string): Promise<LogicSigAccount> {
    const addrHex   = "0x"+Buffer.from(algosdk.decodeAddress(addr).publicKey).toString("hex")

    const tmpl      = await get_file(escrow_template)
    const src       = tmpl.replace("TMPL_GEN_ADDR", addrHex)

    const compiled  = await client.compile(src).do()

    return new LogicSigAccount(Buffer.from(compiled['result'], "base64"))
}

async function get_file(program: string): Promise<string> {
    return await fetch(program)
        .then(response => checkStatus(response) && response.arrayBuffer())
        .then(buffer => {
            const td = new TextDecoder()
            return td.decode(buffer)
        }).catch(err => {
            console.error(err)
            return ""
        });
}

function checkStatus(response: Response) {
    if (!response.ok) throw new Error(`HTTP ${response.status} - ${response.statusText}`);
    return response;
}

// Send transactions to the network 
export async function sendWait(signed: SignedTxn[]): Promise<any> {
    const {txId}  = await client.sendRawTransaction(signed.map((t)=>{return t.blob})).do()
    const result = await waitForConfirmation(client, txId, 3)
    return result 
}

async function waitForConfirmation(algodclient: algosdk.Algodv2, txId: string, timeout: number): Promise<any> {
    if (algodclient == null || txId == null || timeout < 0) {
      throw new Error('Bad arguments.');
    }

    const status = await algodclient.status().do();
    if (typeof status === 'undefined')
      throw new Error('Unable to get node status');

    const startround = status['last-round'] + 1;
    let currentround = startround;
  
    /* eslint-disable no-await-in-loop */
    while (currentround < startround + timeout) {
      const pending = await algodclient
        .pendingTransactionInformation(txId)
        .do();

      if (pending !== undefined) {
        if ( pending['confirmed-round'] !== null && pending['confirmed-round'] > 0) 
          return pending;
  
        if ( pending['pool-error'] != null && pending['pool-error'].length > 0) 
          throw new Error( `Transaction Rejected pool error${pending['pool-error']}`);
      }

      await algodclient.statusAfterBlock(currentround).do();
      currentround += 1;
    }

    /* eslint-enable no-await-in-loop */
    throw new Error(`Transaction not confirmed after ${timeout} rounds!`);
}
