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

@app.route('/', methods=['GET', 'OPTIONS'])
def home():
    return jsonify({
        'name': 'MintMe Wallet Transaction API (DEBUG)',
        'version': '1.0.5',
        'endpoints': {
            '/': 'API info',
            '/transactions?wallet=0x...': 'Get wallet transactions',
            '/debug/<wallet>': 'Debug endpoint - shows raw data',
            '/test-rpc': 'Test RPC connection'
        },
        'status': 'running'
    })

@app.route('/test-rpc', methods=['GET'])
def test_rpc():
    """Test if RPC is working"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "apis_getRecentTransactions",
            "params": ["0x5", "0x0"]  # Get 5 transactions
        }
        
        response = requests.post(
            "https://node1.mintme.com",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        return jsonify({
            'status': 'success',
            'status_code': response.status_code,
            'response_size': len(response.text),
            'sample_data': response.json() if response.status_code == 200 else None,
            'raw_response': response.text[:500] if response.text else 'empty'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

@app.route('/debug/<wallet_address>', methods=['GET'])
def debug_wallet(wallet_address):
    """Debug endpoint to see raw blockchain data"""
    debug_info = {
        'wallet': wallet_address,
        'checks': {}
    }
    
    # Check 1: Validate wallet format
    is_valid = bool(re.match(r'^0x[a-fA-F0-9]{40}$', wallet_address))
    debug_info['checks']['format_valid'] = is_valid
    
    if not is_valid:
        debug_info['checks']['error'] = 'Invalid wallet address format'
        return jsonify(debug_info)
    
    # Check 2: Test RPC connection
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "apis_getRecentTransactions",
            "params": ["0x64", "0x0"]  # Get 100 transactions
        }
        
        response = requests.post(
            "https://node1.mintme.com",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        debug_info['checks']['rpc_connection'] = {
            'status': 'success' if response.status_code == 200 else 'failed',
            'status_code': response.status_code
        }
        
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('result', [])
            
            debug_info['checks']['total_transactions_fetched'] = len(transactions)
            
            # Look for the wallet in transactions
            wallet_lower = wallet_address.lower()
            found_transactions = []
            all_from = set()
            all_to = set()
            
            for tx in transactions:
                tx_from = tx.get('from', '').lower()
                tx_to = tx.get('to', '').lower()
                
                all_from.add(tx_from)
                all_to.add(tx_to)
                
                if tx_from == wallet_lower or tx_to == wallet_lower:
                    found_transactions.append({
                        'hash': tx.get('transactionHash', tx.get('hash', 'N/A')),
                        'from': tx.get('from', 'N/A'),
                        'to': tx.get('to', 'N/A'),
                        'value': tx.get('value', '0'),
                        'timestamp': tx.get('timestamp', 'N/A')
                    })
            
            debug_info['checks']['wallet_found_in_fetched'] = len(found_transactions) > 0
            debug_info['checks']['transactions_found'] = len(found_transactions)
            debug_info['checks']['sample_found_transactions'] = found_transactions[:5]
            debug_info['checks']['unique_from_addresses'] = len(all_from)
            debug_info['checks']['unique_to_addresses'] = len(all_to)
            
            # Check if any address starts with same prefix (to see if we're close)
            wallet_prefix = wallet_lower[:10]
            similar_from = [addr for addr in all_from if addr.startswith(wallet_prefix)]
            similar_to = [addr for addr in all_to if addr.startswith(wallet_prefix)]
            debug_info['checks']['similar_prefix_from'] = similar_from[:5]
            debug_info['checks']['similar_prefix_to'] = similar_to[:5]
            
            # Sample of all transactions (first 3)
            debug_info['checks']['sample_all_transactions'] = [
                {
                    'from': tx.get('from', 'N/A')[:20] + '...',
                    'to': tx.get('to', 'N/A')[:20] + '...',
                    'value': tx.get('value', '0')
                }
                for tx in transactions[:3]
            ]
            
            # Check if the wallet is involved in any transaction
            wallet_in_tx = any(
                wallet_lower in tx.get('from', '').lower() or 
                wallet_lower in tx.get('to', '').lower()
                for tx in transactions
            )
            debug_info['checks']['wallet_in_any_tx'] = wallet_in_tx
            
        else:
            debug_info['checks']['error'] = f"RPC returned status {response.status_code}"
            debug_info['checks']['response'] = response.text[:200]
            
    except Exception as e:
        debug_info['checks']['error'] = str(e)
    
    # Check 3: Try the explorer (just to see if it's accessible)
    try:
        explorer_url = f"https://www.mintme.com/explorer/addr/{wallet_address}"
        response = requests.get(explorer_url, timeout=5)
        debug_info['checks']['explorer_accessible'] = response.status_code == 200
    except:
        debug_info['checks']['explorer_accessible'] = False
    
    return jsonify(debug_info)

@app.route('/transactions', methods=['GET', 'OPTIONS'])
def get_transactions():
    if request.method == 'OPTIONS':
        return '', 200
    
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
    
    if not re.match(r'^0x[a-fA-F0-9]{40}$', wallet_address):
        return jsonify({
            'error': 'Invalid wallet address format',
            'message': 'Wallet address must start with "0x" and be 42 characters long',
            'provided': wallet_address
        }), 400
    
    try:
        # Fetch transactions using RPC
        wallet_lower = wallet_address.lower()
        all_tx = []
        
        # Try to fetch 2000 transactions
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
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('result', [])
            
            for tx in transactions:
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
        
        if not all_tx:
            # Return debug info in response
            debug_url = f"{request.host_url}debug/{wallet_address}"
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
                'message': 'No transactions found in the last 2000 blockchain transactions',
                'debug': 'Check if wallet exists: ' + debug_url,
                'suggestion': 'Visit https://www.mintme.com/explorer/addr/' + wallet_address + ' to verify the wallet'
            })
        
        incoming = [t for t in all_tx if t['direction'] == 'INCOMING']
        outgoing = [t for t in all_tx if t['direction'] == 'OUTGOING']
        
        return jsonify({
            'wallet': wallet_address,
            'total_transactions': len(all_tx),
            'transactions': all_tx,
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

# Vercel requires this
app = app

if __name__ == '__main__':
    app.run(debug=True, port=5000)
