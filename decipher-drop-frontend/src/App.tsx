import React, { useEffect } from 'react'
import { SessionWallet } from 'algorand-session-wallet';
import AlgorandWalletConnector from './AlgorandWalletConnector'
import { Alignment, Button, Card, Elevation, Navbar, ProgressBar } from '@blueprintjs/core';
import { conf, collect, sendWait, getAsaId, getNFT }  from './lib/algorand'
import { Classes, Dialog } from "@blueprintjs/core";




function App() {
  const sw = new SessionWallet(conf.network)
  const [sessionWallet, setSessionWallet] =  React.useState(sw)

  const [nft, setNFT]               = React.useState({id: 0, url:'/algo-gator.png', name:"TBD"})
  const [accts, setAccounts]        = React.useState(sw.accountList())
  const [connected, setConnected]   = React.useState(sw.connected())
  const [claimable, setClaimable]   = React.useState(true)

  const [loading, setLoading]       = React.useState(false)
  const [signed, setSigned]         = React.useState(false)
  const [open, setOpen]             = React.useState(false)


  const params  = new URLSearchParams(window.location.search);
  const escrow  = params.get("escrow")
  const addr    = params.get("addr")
  const secret  = params.get("secret")

  //useEffect(()=>{
  //  if(secret === null || addr === null || escrow === null){
  //    setClaimable(false)
  //  }
  //}, [escrow, addr, secret])
  

  function updateWallet(sw: SessionWallet){ 
    setSessionWallet(sw)
    setAccounts(sw.accountList())
    setConnected(sw.connected())
  }

  async function handleCollect() {
    if(secret === null || addr == null || escrow == null){
      return
    }

    setLoading(true)
    setOpen(true)

    const asaId = await getAsaId(escrow)
    const txn_group = await collect(sw, asaId, escrow, addr, secret)

    setSigned(true)

    await sendWait(txn_group)

    const nft = await getNFT(asaId)

    setNFT(nft)
    setOpen(false)
    setLoading(false)

  }

 /*

For #1-444 (IRL)
Congrats on successfully collecting your Decipher Ticket!
Please make sure the asset is in your Algorand Mobile Wallet and ready to be presented when you arrive at the venue.
See you at Decipher!
-----------------------------------
For #445-888 (Virtual)
Congrats on successfully collecting your Algo Gator NFT!
Enjoy it as a commemorative token that you’ve earned by being part of the Algorand community and signing up as a virtual VIP.
See you online at Decipher!
  
 */

  return (
    <div className="App">
      <Navbar>
        <Navbar.Group align={Alignment.LEFT}>
          <Navbar.Heading>Decipher Dropper</Navbar.Heading>
          <Navbar.Divider />
        </Navbar.Group>
        <Navbar.Group  align={Alignment.RIGHT}>
          <AlgorandWalletConnector  
            darkMode={true}
            sessionWallet={sessionWallet}
            accts={accts}
            connected={connected} 
            updateWallet={updateWallet}
          />
        </Navbar.Group>
      </Navbar>
      <div className='container'>
        <Card elevation={Elevation.THREE}>
          <div className='content'>

            <div className='content-piece' >
              <img className='gator' src={nft.url} />
              <h3> {nft.name + " ("+ nft.id + ")"} </h3>
            </div>
            <div className='content-details' >

              <p> This is where we'll write stuff </p>

              <div className='collect-button' >
                <Button 
                    minimal={true} 
                    outlined={true} 
                    intent='success' 
                    large={true} 
                    icon='circle' 
                    text='Collect' 
                    onClick={handleCollect}  
                    disabled={!claimable || !connected}
                    loading={open}
                  />
                </div>
            </div>
          </div>
        </Card>
      </div>
      <ClaimDialog open={open} signed={signed} />
    </div>
  );
}

interface ClaimDialogProps {
  open: boolean
  signed: boolean
}

function ClaimDialog(props: ClaimDialogProps){
  const [isOpen, setIsOpen] = React.useState(props.open)
  const [signed, setSigned] = React.useState(props.signed)
  const [progress, setProgress] = React.useState(0)

  const handleClose = React.useCallback(() => setIsOpen(false), []);

  useEffect(() => {
    setIsOpen(props.open)
    setSigned(props.signed)
  }, [props])

  let p = 0
  useEffect(()=>{
    if(!props.signed || p >= 1.0) return;

    const step = 100 / (8 * 1000)
    const interval = setInterval(()=>{
        p += step
        if(p > 1.0) {
          clearInterval(interval)
          setProgress(1.0)
          return
        }
        setProgress(p)
    }, 100)
  }, [signed, p])

  return (
      <Dialog isOpen={isOpen} onClose={handleClose}>
        <div className={Classes.DIALOG_BODY}>
          {!signed?(
          <div className='container'>
            <p>Please Approve the transaction in your Mobile Wallet</p>
          </div>
          ):(
            <ProgressBar animate={true} intent='success' value={progress} />
          )}
        </div>
      </Dialog>
    );
}

export default App;
