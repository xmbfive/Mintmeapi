from flask import Flask, request, jsonify
import requests
import re
import json
from datetime import datetime

app = Flask(__name__)

# MintMe RPC Configuration
MINTME_RPC_URL = "https://node1.mintme.com"

# Add CORS headers for browser requests
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def fetch_recent_transactions(limit=50):
    """
    Fetch recent transactions from MintMe blockchain via JSON-RPC
    """
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "apis_getRecentTransactions",
            "params": [hex(limit), "0x0"]
        }
        
        # Add timeout and headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = requests.post(
            MINTME_RPC_URL,
            json=payload,
            headers=headers,
            timeout=15  # Shorter timeout for Vercel
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'result' in data and isinstance(data['result'], list):
                return data['result']
        
        return []
            
    except requests.exceptions.Timeout:
        print("Timeout connecting to MintMe node")
        return []
    except requests.exceptions.ConnectionError:
        print("Connection error to MintMe node")
        return []
    except Exception as e:
        print(f"Unexpected error fetching transactions: {str(e)}")
        return []

def filter_transactions_by_address(transactions, wallet_address):
    """
    Filter transactions that involve the given wallet address
    """
    if not transactions:
        return []
    
    wallet_lower = wallet_address.lower()
    filtered = []
    
    for tx in transactions:
        tx_from = tx.get('from', '').lower()
        tx_to = tx.get('to', '').lower()
        
        if tx_from == wallet_lower or tx_to == wallet_lower:
            # Format the transaction for cleaner output
            value = tx.get('value', '0')
            try:
                value_mintme = float(value) / 1e18 if value != '0' else 0
            except:
                value_mintme = 0
            
            formatted_tx = {
                'hash': tx.get('transactionHash', tx.get('hash', 'N/A')),
                'from': tx.get('from', 'N/A'),
                'to': tx.get('to', 'N/A'),
                'value': value,
                'value_mintme': value_mintme,
                'timestamp': tx.get('timestamp', 'N/A'),
                'blockNumber': tx.get('blockNumber', 'N/A'),
                'direction': 'INCOMING' if tx_to == wallet_lower else 'OUTGOING'
            }
            filtered.append(formatted_tx)
    
    return filtered

@app.route('/', methods=['GET', 'OPTIONS'])
def home():
    """Home endpoint with API documentation"""
    return jsonify({
        'name': 'MintMe Wallet Transaction API',
        'version': '1.0.0',
        'description': 'Fetch latest transactions for any MintMe wallet address',
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
    Main endpoint to fetch transactions for a specific wallet
    Query parameters:
        - wallet: The wallet address (required)
        - limit: Number of transactions to fetch (optional, default: 20, max: 100)
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
        # Fetch more transactions to ensure we have enough after filtering
        fetch_limit = min(limit * 3, 150)
        raw_transactions = fetch_recent_transactions(fetch_limit)
        
        if not raw_transactions:
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
        
        # Filter transactions for this wallet
        filtered_transactions = filter_transactions_by_address(raw_transactions, wallet_address)
        
        # Limit the results
        filtered_transactions = filtered_transactions[:limit]
        
        # Calculate summary
        incoming = [t for t in filtered_transactions if t['direction'] == 'INCOMING']
        outgoing = [t for t in filtered_transactions if t['direction'] == 'OUTGOING']
        
        response_data = {
            'wallet': wallet_address,
            'total_transactions': len(filtered_transactions),
            'transactions': filtered_transactions,
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
