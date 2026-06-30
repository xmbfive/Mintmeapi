import { ethers } from 'ethers';

const TOKEN_CONTRACT_ADDRESS = '0xf3fdd20beb696f53bdcd0e8051b00c5f79cd29c0';

const TOKEN_ABI = [
  'function transfer(address to, uint256 amount) public returns (bool)',
  'function decimals() public view returns (uint8)',
  'function symbol() public view returns (string)',
  'function balanceOf(address account) public view returns (uint256)'
];

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ 
      success: false, 
      error: 'Method not allowed. Use POST.' 
    });
  }

  try {
    const privateKey = process.env.PRIVATE_KEY;
    
    if (!privateKey) {
      return res.status(500).json({ 
        success: false, 
        error: 'PRIVATE_KEY not set' 
      });
    }

    // Parse request body
    const { toAddress, amount = '0.1' } = req.body || {};
    
    if (!toAddress) {
      return res.status(400).json({
        success: false,
        error: 'Missing toAddress in request body'
      });
    }

    // Validate address
    if (!toAddress.startsWith('0x') || toAddress.length !== 42) {
      return res.status(400).json({
        success: false,
        error: 'Invalid address format. Must start with 0x and be 42 characters'
      });
    }

    console.log('Sending tokens...');
    console.log('To:', toAddress);
    console.log('Amount:', amount);

    // Connect to MintMe with timeout
    const provider = new ethers.JsonRpcProvider(
      process.env.RPC_URL || 'https://rpc.mintme.com/'
    );
    
    const wallet = new ethers.Wallet(privateKey, provider);
    const fromAddress = wallet.address;
    
    const tokenContract = new ethers.Contract(
      TOKEN_CONTRACT_ADDRESS, 
      TOKEN_ABI, 
      wallet
    );
    
    const decimals = await tokenContract.decimals();
    const symbol = await tokenContract.symbol();
    const amountToSend = ethers.parseUnits(amount, decimals);
    
    const balance = await tokenContract.balanceOf(fromAddress);
    const balanceFormatted = ethers.formatUnits(balance, decimals);
    
    console.log(`Balance: ${balanceFormatted} ${symbol}`);
    
    if (balance < amountToSend) {
      return res.status(400).json({
        success: false,
        error: `Insufficient balance. Have ${balanceFormatted} ${symbol}`
      });
    }
    
    // Send transaction WITHOUT waiting for confirmation
    console.log(`Sending ${amount} ${symbol}...`);
    const tx = await tokenContract.transfer(toAddress, amountToSend);
    
    console.log('Transaction sent:', tx.hash);
    
    // Return immediately with tx hash (don't wait for confirmation)
    return res.status(200).json({
      success: true,
      txHash: tx.hash,
      from: fromAddress,
      to: toAddress,
      amount: `${amount} ${symbol}`,
      status: 'pending',
      explorerUrl: `https://www.mintme.com/explorer/tx/${tx.hash}`,
      message: 'Transaction sent! Check explorer for confirmation.'
    });
    
  } catch (error) {
    console.error('Error:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'Transaction failed'
    });
  }
}
