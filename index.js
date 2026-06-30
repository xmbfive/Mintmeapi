import { ethers } from 'ethers';

const TOKEN_ADDRESS = '0xf3fdd20beb696f53bdcd0e8051b00c5f79cd29c0';

const TOKEN_ABI = [
  'function transfer(address to, uint256 amount) public returns (bool)',
  'function decimals() public view returns (uint8)',
  'function symbol() public view returns (string)',
  'function balanceOf(address account) public view returns (uint256)'
];

module.exports = async (req, res) => {
  console.log('Request received:', req.method, req.url);
  
  // Handle only POST
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const privateKey = process.env.PRIVATE_KEY;
    if (!privateKey) {
      throw new Error('PRIVATE_KEY not set');
    }

    const provider = new ethers.JsonRpcProvider('https://rpc.mintme.com/');
    const wallet = new ethers.Wallet(privateKey, provider);
    const fromAddress = wallet.address;
    
    const tokenContract = new ethers.Contract(TOKEN_ADDRESS, TOKEN_ABI, wallet);
    const decimals = await tokenContract.decimals();
    const symbol = await tokenContract.symbol();
    const amount = ethers.parseUnits('0.1', decimals);
    
    const balance = await tokenContract.balanceOf(fromAddress);
    if (balance < amount) {
      return res.status(400).json({
        success: false,
        error: `Insufficient balance`
      });
    }
    
    const tx = await tokenContract.transfer(TOKEN_ADDRESS, amount);
    const receipt = await tx.wait();
    
    res.status(200).json({
      success: true,
      txHash: tx.hash,
      from: fromAddress,
      to: TOKEN_ADDRESS,
      amount: `0.1 ${symbol}`,
      explorerUrl: `https://www.mintme.com/explorer/tx/${tx.hash}`
    });
    
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
};
