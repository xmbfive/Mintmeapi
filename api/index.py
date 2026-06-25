from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime
import re

app = Flask(__name__)

# MintMe RPC Configuration
MINTME_RPC_URL = "https://node1.mintme.com"

def validate_wallet_address(address):
    """Validate if the address is a valid MintMe wallet address"""
    if not address:
        return False
    # Basic validation: starts with 0x and is 42 characters long
    if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
        return False
    return True

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
        
        response = requests.post(
            MINTME_RPC_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'result' in data and isinstance(data['result'], list):
                return data['result']
            else:
                return []
        else:
            print(f"RPC Error: HTTP {response.status_code}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
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
            formatted_tx = {
                'hash': tx.get('transactionHash', tx.get('hash', 'N/A')),
                'from': tx.get('from', 'N/A'),
                'to': tx.get('to', 'N/A'),
                'value': tx.get('value', '0'),
                'value_mintme': float(tx.get('value', '0')) / 1e18 if tx.get('value') else 0,
                'timestamp': tx.get('timestamp', 'N/A'),
                'blockNumber': tx.get('blockNumber', 'N/A'),
                'fee': tx.get('fee', '0'),
                'fee_mintme': float(tx.get('fee', '0')) / 1e18 if tx.get('fee') else 0,
                'direction': 'INCOMING' if tx_to == wallet_lower else 'OUTGOING',
                'raw': tx  # Keep raw data for debugging
            }
            filtered.append(formatted_tx)
    
    return filtered

def format_transactions(transactions, wallet_address):
    """
    Format transactions for JSON response with additional metadata
    """
    if not transactions:
        return {
            'wallet': wallet_address,
            'total_transactions': 0,
            'transactions': [],
            'summary': {
                'total_incoming': 0,
                'total_outgoing': 0,
                'total_value_in': 0,
                'total_value_out': 0
            }
        }
    
    summary = {
        'total_incoming': 0,
        'total_outgoing': 0,
        'total_value_in': 0,
        'total_value_out': 0
    }
    
    for tx in transactions:
        if tx['direction'] == 'INCOMING':
            summary['total_incoming'] += 1
            summary['total_value_in'] += tx['value_mintme']
        else:
            summary['total_outgoing'] += 1
            summary['total_value_out'] += tx['value_mintme']
    
    return {
        'wallet': wallet_address,
        'total_transactions': len(transactions),
        'transactions': transactions,
        'summary': summary,
        'fetched_at': datetime.utcnow().isoformat() + 'Z'
    }

@app.route('/', methods=['GET', 'POST'])
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

@app.route('/transactions', methods=['GET'])
def get_transactions():
    """
    Main endpoint to fetch transactions for a specific wallet
    Query parameters:
        - wallet: The wallet address (required)
        - limit: Number of transactions to fetch (optional, default: 20, max: 100)
    """
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
    
    if not validate_wallet_address(wallet_address):
        return jsonify({
            'error': 'Invalid wallet address',
            'message': 'Wallet address must start with "0x" and be 42 characters long',
            'provided': wallet_address
        }), 400
    
    try:
        # Fetch transactions
        raw_transactions = fetch_recent_transactions(limit * 2)  # Fetch more to ensure we get enough
        
        if not raw_transactions:
            return jsonify({
                'error': 'Failed to fetch transactions',
                'message': 'Unable to connect to MintMe blockchain. Please try again later.'
            }), 503
        
        # Filter transactions for this wallet
        filtered_transactions = filter_transactions_by_address(raw_transactions, wallet_address)
        
        # Format response
        response_data = format_transactions(filtered_transactions, wallet_address)
        
        # Add request metadata
        response_data['request'] = {
            'limit': limit,
            'params': {
                'wallet': wallet_address,
                'limit': limit
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested endpoint does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500

# Vercel requires the app to be exported as 'app'
app = app

if __name__ == '__main__':
    app.run(debug=True, port=5000)
