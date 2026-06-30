import { ethers } from 'ethers';

// Your token contract address on MintMe
const TOKEN_ADDRESS = '0xf3fdd20beb696f53bdcd0e8051b00c5f79cd29c0';

// Minimal ERC-20 ABI for token transfers
const TOKEN_ABI = [
  'function transfer(address to, uint256 amount) public returns (bool)',
  'function decimals() public view returns (uint8)',
  'function symbol() public view returns (string)',
  'function balanceOf(address account) public view returns (uint256)'
];

export default async function handler(req, res) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ 
      success: false, 
      error: 'Method not allowed' 
    });
  }

  // Get private key from Vercel environment variables (COMPLETELY HIDDEN)
  const privateKey = process.env.PRIVATE_KEY;
  
  if (!privateKey) {
    console.error('PRIVATE_KEY not set in Vercel environment');
    return res.status(500).json({ 
      success: false, 
      error: 'Server configuration error' 
    });
  }

  try {
    // Connect to MintMe blockchain
    const provider = new ethers.JsonRpcProvider(
      process.env.RPC_URL || 'https://rpc.mintme.com/'
    );
    
    // Create wallet from private key (NEVER exposed in response)
    const wallet = new ethers.Wallet(privateKey, provider);
    const fromAddress = wallet.address;
    
    // Get token contract
    const tokenContract = new ethers.Contract(
      TOKEN_ADDRESS,
      TOKEN_ABI,
      wallet
    );
    
    // Get token decimals and symbol
    const decimals = await tokenContract.decimals();
    const symbol = await tokenContract.symbol();
    
    // Send 0.1 tokens (or adjust as needed)
    const amount = ethers.parseUnits('0.1', decimals);
    
    // Check balance first
    const balance = await tokenContract.balanceOf(fromAddress);
    console.log(`Wallet Balance: ${ethers.formatUnits(balance, decimals)} ${symbol}`);
    
    if (balance < amount) {
      return res.status(400).json({
        success: false,
        error: `Insufficient balance. You have ${ethers.formatUnits(balance, decimals)} ${symbol}`
      });
    }
    
    // Send tokens to the contract address (as requested)
    console.log(`Sending 0.1 ${symbol} to ${TOKEN_ADDRESS}...`);
    const tx = await tokenContract.transfer(TOKEN_ADDRESS, amount);
    
    console.log(`Transaction sent! Hash: ${tx.hash}`);
    
    // Wait for confirmation
    const receipt = await tx.wait();
    console.log(`Confirmed in block: ${receipt.blockNumber}`);
    
    // Return success - NEVER include private key
    res.status(200).json({
      success: true,
      txHash: tx.hash,
      from: fromAddress,
      to: TOKEN_ADDRESS,
      amount: `0.1 ${symbol}`,
      blockNumber: receipt.blockNumber,
      explorerUrl: `https://www.mintme.com/explorer/tx/${tx.hash}`
    });
    
  } catch (error) {
    console.error('Transaction failed:', error);
    
    res.status(500).json({
      success: false,
      error: error.message || 'Transaction failed',
      code: error.code || 'UNKNOWN_ERROR'
    });
  }
}
