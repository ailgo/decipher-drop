import React from 'react'
import { SessionWallet } from 'algorand-session-wallet';
import AlgorandWalletConnector from './AlgorandWalletConnector'
import { Alignment, Button, Navbar } from '@blueprintjs/core';
import { collect }  from './lib/algorand'

const conf = {
  network:""
}

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

    const params = new URLSearchParams(window.location.search);
    const secret = params.get("secret")

    if(secret === undefined || secret === null){
      alert("No secret in url? Probly Ben's fault")
      return
    }

    // Set loading
    // showToast("Sign the transaction dawg")

    await collect(secret)

    // Set !loading 
    // showToast("Aight check yer wallet g")
  }

  return (
    <div className="App">
      <Navbar>
        <Navbar.Group align={Alignment.LEFT}>
          <Navbar.Heading>Decipher Al Goanna</Navbar.Heading>
          <Navbar.Divider />
        </Navbar.Group>
        <Navbar.Group  align={Alignment.RIGHT}>
          <AlgorandWalletConnector  
            darkMode={false}
            sessionWallet={sessionWallet}
            accts={accts}
            connected={connected} 
            updateWallet={updateWallet}
          />
        </Navbar.Group>
      </Navbar>
      <div className='container'>
        <Button icon='circle' text='Collect' onClick={handleCollect}  />
      </div>
    </div>
  );
}

export default App;
