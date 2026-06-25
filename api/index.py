from flask import Flask, request, jsonify
import requests
import re
import json
from datetime import datetime

app = Flask(__name__)

# MintMe API Configuration
MINTME_API_URL = "https://www.mintme.com/api/v2"

# Add CORS headers for browser requests
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def fetch_wallet_transactions(wallet_address, limit=20, offset=0):
    """
    Fetch transactions directly for a specific wallet using MintMe REST API
    """
    try:
        # Using MintMe's REST API to get wallet transactions
        # The endpoint format is based on MintMe API v2
        url = f"{MINTME_API_URL}/addresses/{wallet_address}/transactions"
        
        params = {
            'limit': limit,
            'offset': offset
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('result', [])
        else:
            # If REST API fails, try the RPC method as fallback
            return fetch_wallet_transactions_rpc(wallet_address, limit)
            
    except Exception as e:
        print(f"Error fetching wallet transactions: {str(e)}")
        # Fallback to RPC method
        return fetch_wallet_transactions_rpc(wallet_address, limit)

def fetch_wallet_transactions_rpc(wallet_address, limit=20):
    """
    Fallback: Fetch transactions using RPC but specifically for the wallet
    """
    try:
        wallet_lower = wallet_address.lower()
        all_tx = []
        
        # Fetch a larger batch to ensure we get some transactions
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "apis_getRecentTransactions",
            "params": ["0x3E8", "0x0"]  # Fetch 1000 transactions
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
                    
                    # Convert timestamp
                    timestamp = tx.get('timestamp', 'N/A')
                    if timestamp != 'N/A':
                        try:
                            dt = datetime.fromtimestamp(int(timestamp))
                            timestamp = dt.isoformat() + 'Z'
                        except:
                            pass
                    
                    all_tx.append({
                        'hash': tx.get('transactionHash', tx.get('hash', 'N/A')),
                        'from': tx.get('from', 'N/A'),
                        'to': tx.get('to', 'N/A'),
                        'value': value,
                        'value_mintme': value_mintme,
                        'timestamp': timestamp,
                        'blockNumber': tx.get('blockNumber', 'N/A'),
                        'direction': 'INCOMING' if tx_to == wallet_lower else 'OUTGOING'
                    })
                    
                    if len(all_tx) >= limit:
                        break
            
            return all_tx
        
        return []
            
    except Exception as e:
        print(f"RPC fallback error: {str(e)}")
        return []

@app.route('/', methods=['GET', 'OPTIONS'])
def home():
    """Home endpoint with API documentation"""
    return jsonify({
        'name': 'MintMe Wallet Transaction API',
        'version': '1.0.2',
        'description': 'Fetch transactions directly for a specific wallet address',
        'endpoints': {
            '/transactions': {
                'method': 'GET',
                'parameters': {
                    'wallet': 'Wallet address (required)',
                    'limit': 'Number of transactions to fetch (default: 20, max: 100)'
                },
                'example': '/transactions?wallet=0x1b3aa657e0d114bc9a6bd8f16cb32233f34875e9&limit=10'
            }
        },
        'status': 'running'
    })

@app.route('/transactions', methods=['GET', 'OPTIONS'])
def get_transactions():
    """
    Fetch transactions for a specific wallet address
    Query parameters:
        - wallet: The wallet address (required)
        - limit: Number of transactions to fetch (default: 20, max: 100)
    """
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
                'message': 'No transactions found for this wallet'
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
            'message': str(e)
        }), 500

# Vercel requires this
app = app

if __name__ == '__main__':
    app.run(debug=True, port=5000)
