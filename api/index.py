from flask import Flask, request, jsonify
import requests
import re
import json
from datetime import datetime

app = Flask(__name__)

# Add CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def fetch_wallet_transactions(wallet_address, limit=20):
    """
    Fetch transactions for a specific wallet using RPC
    """
    wallet_lower = wallet_address.lower()
    all_tx = []
    
    try:
        # Fetch a large batch of transactions (2000)
        # This ensures we catch older transactions
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "apis_getRecentTransactions",
            "params": ["0x7D0", "0x0"]  # 2000 transactions in hex
        }
        
        response = requests.post(
            "https://node1.mintme.com",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('result', [])
            
            print(f"Fetched {len(transactions)} total transactions")  # For debugging
            
            # Only keep transactions for this specific wallet
            for tx in transactions:
                tx_from = tx.get('from', '').lower()
                tx_to = tx.get('to', '').lower()
                
                if tx_from == wallet_lower or tx_to == wallet_lower:
                    value = tx.get('value', '0')
                    try:
                        value_mintme = float(value) / 1e18 if value != '0' else 0
                    except:
                        value_mintme = 0
                    
                    # Get transaction hash
                    tx_hash = tx.get('transactionHash', tx.get('hash', 'N/A'))
                    
                    # Format timestamp
                    timestamp = tx.get('timestamp', 'N/A')
                    if timestamp != 'N/A':
                        try:
                            dt = datetime.fromtimestamp(int(timestamp))
                            timestamp = dt.isoformat() + 'Z'
                        except:
                            pass
                    
                    all_tx.append({
                        'hash': tx_hash,
                        'from': tx.get('from', 'N/A'),
                        'to': tx.get('to', 'N/A'),
                        'value': value,
                        'value_mintme': value_mintme,
                        'timestamp': timestamp,
                        'blockNumber': tx.get('blockNumber', 'N/A'),
                        'direction': 'INCOMING' if tx_to == wallet_lower else 'OUTGOING',
                        'raw': tx  # Keep raw for debugging if needed
                    })
                    
                    # Stop if we have enough
                    if len(all_tx) >= limit:
                        break
            
            print(f"Found {len(all_tx)} transactions for wallet")  # For debugging
            return all_tx
        
        return []
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

@app.route('/', methods=['GET', 'OPTIONS'])
def home():
    return jsonify({
        'name': 'MintMe Wallet Transaction API',
        'version': '1.0.3',
        'description': 'Fetch transactions for any MintMe wallet address',
        'endpoint': '/transactions?wallet=0x...&limit=20',
        'example': '/transactions?wallet=0x1b3aa657e0d114bc9a6bd8f16cb32233f34875e9&limit=10',
        'status': 'running'
    })

@app.route('/transactions', methods=['GET', 'OPTIONS'])
def get_transactions():
    # Handle OPTIONS request for CORS
    if request.method == 'OPTIONS':
        return '', 200
    
    # Get parameters
    wallet_address = request.args.get('wallet', '').strip()
    limit = request.args.get('limit', 20)
    
    # Validate limit
    try:
        limit = int(limit)
        if limit < 1:
            limit = 20
        elif limit > 100:
            limit = 100
    except ValueError:
        limit = 20
    
    # Validate wallet address
    if not wallet_address:
        return jsonify({
            'error': 'Wallet address is required',
            'message': 'Please provide a wallet address using the "wallet" parameter',
            'example': '/transactions?wallet=0x1b3aa657e0d114bc9a6bd8f16cb32233f34875e9'
        }), 400
    
    # Basic wallet address validation
    if not re.match(r'^0x[a-fA-F0-9]{40}$', wallet_address):
        return jsonify({
            'error': 'Invalid wallet address format',
            'message': 'Wallet address must start with "0x" and be 42 characters long',
            'provided': wallet_address
        }), 400
    
    try:
        # Fetch transactions for this specific wallet
        transactions = fetch_wallet_transactions(wallet_address, limit)
        
        if not transactions:
            return jsonify({
                'wallet': wallet_address,
                'total_transactions': 0,
                'transactions': [],
                'summary': {
                    'total_incoming': 0,
                    'total_outgoing': 0,
                    'total_value_in': 0,
                    'total_value_out': 0
                },
                'message': 'No transactions found for this wallet. The wallet might be new or have no recent activity.'
            })
        
        # Calculate summary
        incoming = [t for t in transactions if t['direction'] == 'INCOMING']
        outgoing = [t for t in transactions if t['direction'] == 'OUTGOING']
        
        response_data = {
            'wallet': wallet_address,
            'total_transactions': len(transactions),
            'transactions': transactions,
            'summary': {
                'total_incoming': len(incoming),
                'total_outgoing': len(outgoing),
                'total_value_in': sum(t.get('value_mintme', 0) for t in incoming),
                'total_value_out': sum(t.get('value_mintme', 0) for t in outgoing)
            },
            'fetched_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'debug': 'Check Vercel logs for more details'
        }), 500

# Vercel requires this
app = app

if __name__ == '__main__':
    app.run(debug=True, port=5000)
