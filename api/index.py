from flask import Flask, request, jsonify
import requests
import re
from datetime import datetime

app = Flask(__name__)

# Add CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# ===== ROUTES =====

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'name': 'MintMe Wallet Transaction API',
        'version': '1.0.6',
        'endpoints': {
            '/': 'API info',
            '/transactions?wallet=0x...': 'Get wallet transactions',
            '/test': 'Test if API is working'
        },
        'status': 'running'
    })

@app.route('/test', methods=['GET'])
def test():
    """Simple test endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'API is working!',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/transactions', methods=['GET'])
def get_transactions():
    """Get transactions for a wallet"""
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
            'message': 'Please provide a wallet address',
            'example': '/transactions?wallet=0x1b3aa657e0d114bc9a6bd8f16cb32233f34875e9'
        }), 400
    
    if not re.match(r'^0x[a-fA-F0-9]{40}$', wallet_address):
        return jsonify({
            'error': 'Invalid wallet address format',
            'message': 'Must start with "0x" and be 42 characters long'
        }), 400
    
    try:
        # Fetch transactions
        wallet_lower = wallet_address.lower()
        transactions = []
        
        # Try RPC
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "apis_getRecentTransactions",
            "params": ["0x7D0", "0x0"]  # 2000 transactions
        }
        
        response = requests.post(
            "https://node1.mintme.com",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            all_tx = data.get('result', [])
            
            for tx in all_tx:
                tx_from = tx.get('from', '').lower()
                tx_to = tx.get('to', '').lower()
                
                if tx_from == wallet_lower or tx_to == wallet_lower:
                    value = tx.get('value', '0')
                    try:
                        value_mintme = float(value) / 1e18 if value != '0' else 0
                    except:
                        value_mintme = 0
                    
                    timestamp = tx.get('timestamp', 'N/A')
                    if timestamp != 'N/A':
                        try:
                            dt = datetime.fromtimestamp(int(timestamp))
                            timestamp = dt.isoformat() + 'Z'
                        except:
                            pass
                    
                    transactions.append({
                        'hash': tx.get('transactionHash', tx.get('hash', 'N/A')),
                        'from': tx.get('from', 'N/A'),
                        'to': tx.get('to', 'N/A'),
                        'value': value,
                        'value_mintme': value_mintme,
                        'timestamp': timestamp,
                        'blockNumber': tx.get('blockNumber', 'N/A'),
                        'direction': 'INCOMING' if tx_to == wallet_lower else 'OUTGOING'
                    })
                    
                    if len(transactions) >= limit:
                        break
        
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
                'message': 'No transactions found in recent blockchain history',
                'check_explorer': f'https://www.mintme.com/explorer/addr/{wallet_address}'
            })
        
        incoming = [t for t in transactions if t['direction'] == 'INCOMING']
        outgoing = [t for t in transactions if t['direction'] == 'OUTGOING']
        
        return jsonify({
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
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

# ===== VERCEL =====
# This is required for Vercel
app = app

if __name__ == '__main__':
    app.run(debug=True, port=5000)
