import React from 'react'
import { SessionWallet } from 'algorand-session-wallet';
import AlgorandWalletConnector from './AlgorandWalletConnector'
import { Alignment, Button, Card, Elevation, Navbar } from '@blueprintjs/core';
import { conf, collect }  from './lib/algorand'
import { Popover2, Tooltip2 } from "@blueprintjs/popover2";



function App() {
  const sw = new SessionWallet(conf.network)
  const [sessionWallet, setSessionWallet] =  React.useState(sw)
  const [accts, setAccounts] = React.useState(sw.accountList())
  const [connected, setConnected] = React.useState(sw.connected())


  function updateWallet(sw: SessionWallet){ 
    setSessionWallet(sw)
    setAccounts(sw.accountList())
    setConnected(sw.connected())
  }

  async function handleCollect() {
    //if(!connected){
    //  alert("Connect your wallet to collect your Al Goana")
    //}

    const params  = new URLSearchParams(window.location.search);
    const escrow  = params.get("escrow")
    const addr    = params.get("addr")
    const secret  = params.get("secret")

    console.log(secret)

    if(secret === null || addr == null || escrow == null){
      alert("Something aint right, Probly Ben's fault")
      return
    }

    // Set loading
    // showToast("Sign the transaction dawg")

    await collect(sw, escrow, addr, secret)

    // Set !loading 
    // showToast("Aight check yer wallet g")
  }

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
              <img className='gator' src='/algo-gator.png' />
            </div>
            <div className='content-details' >

              <p>
                This is where we'll write stuff
              </p>
              
              <div className='collect-button' >
                <Button 
                    minimal={true} 
                    outlined={true} 
                    intent='success' 
                    large={true} 
                    icon='circle' 
                    text='Collect' 
                    onClick={handleCollect}  
                  />
                </div>

            </div>

          </div>
        </Card>
      </div>
    </div>
  );
}

export default App;
