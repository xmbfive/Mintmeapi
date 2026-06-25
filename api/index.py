<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MintMe Wallet Transaction Viewer</title>
    <style>
        /* ===== RESET & BASE ===== */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }
        
        /* ===== CONTAINER ===== */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* ===== HEADER ===== */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 30px;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, #e94560, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header .version {
            color: #888;
            font-size: 0.9rem;
            background: rgba(255, 255, 255, 0.1);
            padding: 5px 15px;
            border-radius: 20px;
        }
        
        /* ===== SEARCH SECTION ===== */
        .search-section {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        .search-section .label {
            font-size: 0.9rem;
            color: #aaa;
            margin-bottom: 10px;
            display: block;
        }
        
        .search-row {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .search-row input {
            flex: 1;
            min-width: 300px;
            padding: 15px 20px;
            border-radius: 12px;
            border: 2px solid rgba(255, 255, 255, 0.15);
            background: rgba(0, 0, 0, 0.4);
            color: #fff;
            font-size: 1rem;
            transition: all 0.3s;
        }
        
        .search-row input:focus {
            outline: none;
            border-color: #e94560;
            box-shadow: 0 0 20px rgba(233, 69, 96, 0.2);
        }
        
        .search-row input::placeholder {
            color: #666;
        }
        
        .search-row button {
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            background: linear-gradient(135deg, #e94560, #c73652);
            color: #fff;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            min-width: 120px;
        }
        
        .search-row button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(233, 69, 96, 0.3);
        }
        
        .search-row button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .search-row button.secondary {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .search-row button.secondary:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        /* ===== QUICK ADDRESSES ===== */
        .quick-addresses {
            margin-top: 15px;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .quick-addresses .chip {
            padding: 8px 16px;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.08);
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.3s;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .quick-addresses .chip:hover {
            background: rgba(233, 69, 96, 0.2);
            border-color: #e94560;
        }
        
        /* ===== STATUS BAR ===== */
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 12px;
            margin-bottom: 25px;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .status-bar .status {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-bar .dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
        }
        
        .status-bar .dot.idle {
            background: #666;
        }
        .status-bar .dot.loading {
            background: #ffd93d;
            animation: pulse 1s infinite;
        }
        .status-bar .dot.success {
            background: #6bcb77;
        }
        .status-bar .dot.error {
            background: #ff6b6b;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        
        .status-bar .stats {
            display: flex;
            gap: 25px;
            color: #aaa;
            font-size: 0.9rem;
        }
        
        .status-bar .stats span {
            color: #fff;
            font-weight: 600;
        }
        
        /* ===== SUMMARY CARDS ===== */
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .summary-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            text-align: center;
        }
        
        .summary-card .label {
            font-size: 0.8rem;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .summary-card .value {
            font-size: 1.8rem;
            font-weight: 700;
            margin-top: 5px;
        }
        
        .summary-card .value.incoming {
            color: #6bcb77;
        }
        .summary-card .value.outgoing {
            color: #ff6b6b;
        }
        .summary-card .value.total {
            color: #ffd93d;
        }
        
        /* ===== TRANSACTIONS TABLE ===== */
        .transactions-section {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 15px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .transactions-section .header-row {
            display: grid;
            grid-template-columns: 2fr 2fr 2fr 1.5fr 1.5fr 1fr;
            padding: 15px 20px;
            background: rgba(255, 255, 255, 0.05);
            font-size: 0.85rem;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            gap: 10px;
        }
        
        .transaction-row {
            display: grid;
            grid-template-columns: 2fr 2fr 2fr 1.5fr 1.5fr 1fr;
            padding: 15px 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            transition: background 0.3s;
            gap: 10px;
            align-items: center;
        }
        
        .transaction-row:hover {
            background: rgba(255, 255, 255, 0.05);
        }
        
        .transaction-row .hash {
            font-family: monospace;
            font-size: 0.85rem;
            color: #a8d8ea;
        }
        
        .transaction-row .address {
            font-family: monospace;
            font-size: 0.85rem;
            color: #ccc;
            word-break: break-all;
        }
        
        .transaction-row .amount {
            font-weight: 600;
        }
        
        .transaction-row .amount.incoming {
            color: #6bcb77;
        }
        .transaction-row .amount.outgoing {
            color: #ff6b6b;
        }
        
        .transaction-row .direction-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-align: center;
            display: inline-block;
            width: fit-content;
        }
        
        .transaction-row .direction-badge.incoming {
            background: rgba(107, 203, 119, 0.2);
            color: #6bcb77;
        }
        
        .transaction-row .direction-badge.outgoing {
            background: rgba(255, 107, 107, 0.2);
            color: #ff6b6b;
        }
        
        .transaction-row .time {
            font-size: 0.8rem;
            color: #888;
        }
        
        /* ===== EMPTY STATE ===== */
        .empty-state {
            padding: 60px 20px;
            text-align: center;
            color: #666;
        }
        
        .empty-state .icon {
            font-size: 4rem;
            margin-bottom: 20px;
        }
        
        .empty-state h3 {
            color: #aaa;
            margin-bottom: 10px;
        }
        
        /* ===== LOADING ===== */
        .loading-state {
            padding: 40px;
            text-align: center;
        }
        
        .loading-state .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-top-color: #e94560;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* ===== RESPONSIVE ===== */
        @media (max-width: 992px) {
            .transactions-section .header-row,
            .transaction-row {
                grid-template-columns: 1fr 1fr 1fr 1fr;
            }
            .transactions-section .header-row .hide-mobile,
            .transaction-row .hide-mobile {
                display: none;
            }
        }
        
        @media (max-width: 768px) {
            .container { padding: 15px; }
            .header h1 { font-size: 1.8rem; }
            .search-row input { min-width: 200px; }
            .summary-grid { grid-template-columns: 1fr 1fr; }
            .transactions-section .header-row,
            .transaction-row {
                grid-template-columns: 1fr 1fr;
                font-size: 0.8rem;
                gap: 5px;
            }
            .transaction-row .hash { font-size: 0.7rem; }
            .transaction-row .address { font-size: 0.7rem; }
        }
        
        @media (max-width: 480px) {
            .summary-grid { grid-template-columns: 1fr; }
            .search-row { flex-direction: column; }
            .search-row input { min-width: 100%; }
            .search-row button { width: 100%; }
            .status-bar { flex-direction: column; align-items: flex-start; }
            .status-bar .stats { flex-wrap: wrap; gap: 10px; }
        }
        
        /* ===== SCROLLBAR ===== */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.05);
        }
        ::-webkit-scrollbar-thumb {
            background: #e94560;
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #c73652;
        }
    </style>
</head>
<body>
    <div class="container" id="app">
        <!-- HEADER -->
        <div class="header">
            <h1>🔍 MintMe Wallet Viewer</h1>
            <div class="version">v1.0.0</div>
        </div>
        
        <!-- SEARCH -->
        <div class="search-section">
            <label class="label">Enter Wallet Address</label>
            <div class="search-row">
                <input 
                    type="text" 
                    id="walletInput" 
                    placeholder="0x1b3aa657e0d114bc9a6bd8f16cb32233f34875e9"
                    value="0x1b3aa657e0d114bc9a6bd8f16cb32233f34875e9"
                />
                <button id="fetchBtn" onclick="fetchTransactions()">🔍 Fetch</button>
                <button class="secondary" onclick="clearAll()">🗑️ Clear</button>
            </div>
            <div class="quick-addresses">
                <span style="color:#666; font-size:0.85rem;">Quick test:</span>
                <span class="chip" onclick="setAddress('0x1b3aa657e0d114bc9a6bd8f16cb32233f34875e9')">Test Wallet 1</span>
                <span class="chip" onclick="setAddress('0x067fa59cd5d5cd62be16c8d1df0d80e35a1d88dc')">WETH</span>
                <span class="chip" onclick="setAddress('0x9D8dd79F2d4ba9E1C3820d7659A5F5D2FA1C22eF')">BONE</span>
            </div>
        </div>
        
        <!-- STATUS BAR -->
        <div class="status-bar">
            <div class="status">
                <span class="dot idle" id="statusDot"></span>
                <span id="statusText">Ready</span>
            </div>
            <div class="stats">
                <div>Total Tx: <span id="totalTx">0</span></div>
                <div>Incoming: <span id="incomingCount">0</span></div>
                <div>Outgoing: <span id="outgoingCount">0</span></div>
            </div>
        </div>
        
        <!-- SUMMARY GRID -->
        <div class="summary-grid" id="summaryGrid">
            <div class="summary-card">
                <div class="label">Total Transactions</div>
                <div class="value total" id="summaryTotal">0</div>
            </div>
            <div class="summary-card">
                <div class="label">Total Incoming</div>
                <div class="value incoming" id="summaryIncoming">0</div>
            </div>
            <div class="summary-card">
                <div class="label">Total Outgoing</div>
                <div class="value outgoing" id="summaryOutgoing">0</div>
            </div>
            <div class="summary-card">
                <div class="label">Total Value In (MINTME)</div>
                <div class="value incoming" id="summaryValueIn">0.000</div>
            </div>
            <div class="summary-card">
                <div class="label">Total Value Out (MINTME)</div>
                <div class="value outgoing" id="summaryValueOut">0.000</div>
            </div>
            <div class="summary-card">
                <div class="label">Net Change</div>
                <div class="value" id="summaryNet" style="color:#ffd93d;">0.000</div>
            </div>
        </div>
        
        <!-- TRANSACTIONS TABLE -->
        <div class="transactions-section">
            <div class="header-row">
                <div>Hash</div>
                <div>From</div>
                <div>To</div>
                <div class="hide-mobile">Amount</div>
                <div>Direction</div>
                <div class="hide-mobile">Time</div>
            </div>
            <div id="transactionsContainer">
                <div class="empty-state">
                    <div class="icon">🔍</div>
                    <h3>No transactions yet</h3>
                    <p>Enter a wallet address and click Fetch</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // ============================================================
        // ===== CONFIGURATION =========================================
        // ============================================================
        
        const CONFIG = {
            RPC_URL: 'https://node1.mintme.com',
            RPC_METHOD: 'apis_getRecentTransactions',
            FETCH_LIMIT: 2000,  // Number of transactions to fetch
            MAX_DISPLAY: 100     // Max transactions to show
        };
        
        // ============================================================
        // ===== STATE =================================================
        // ============================================================
        
        let state = {
            transactions: [],
            wallet: '',
            isLoading: false,
            error: null
        };
        
        // ============================================================
        // ===== DOM REFERENCES ========================================
        // ============================================================
        
        const $ = (id) => document.getElementById(id);
        
        const elements = {
            walletInput: $('walletInput'),
            fetchBtn: $('fetchBtn'),
            statusDot: $('statusDot'),
            statusText: $('statusText'),
            totalTx: $('totalTx'),
            incomingCount: $('incomingCount'),
            outgoingCount: $('outgoingCount'),
            summaryTotal: $('summaryTotal'),
            summaryIncoming: $('summaryIncoming'),
            summaryOutgoing: $('summaryOutgoing'),
            summaryValueIn: $('summaryValueIn'),
            summaryValueOut: $('summaryValueOut'),
            summaryNet: $('summaryNet'),
            transactionsContainer: $('transactionsContainer')
        };
        
        // ============================================================
        // ===== UTILITY FUNCTIONS =====================================
        // ============================================================
        
        function truncateAddress(addr, start = 8, end = 6) {
            if (!addr || addr.length < 20) return addr;
            return addr.slice(0, start) + '...' + addr.slice(-end);
        }
        
        function truncateHash(hash, start = 10, end = 8) {
            if (!hash || hash.length < 20) return hash;
            return hash.slice(0, start) + '...' + hash.slice(-end);
        }
        
        function formatTimestamp(timestamp) {
            if (!timestamp || timestamp === 'N/A') return 'N/A';
            try {
                const date = new Date(parseInt(timestamp) * 1000);
                if (isNaN(date.getTime())) return 'N/A';
                return date.toLocaleString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
            } catch {
                return 'N/A';
            }
        }
        
        function formatValue(value) {
            try {
                const num = parseFloat(value);
                if (isNaN(num)) return '0.000';
                if (num === 0) return '0.000';
                if (num < 0.001) return '< 0.001';
                return num.toFixed(4);
            } catch {
                return '0.000';
            }
        }
        
        function setAddress(address) {
            elements.walletInput.value = address;
            fetchTransactions();
        }
        
        function clearAll() {
            state.transactions = [];
            state.wallet = '';
            state.error = null;
            render();
            updateStatus('idle', 'Ready');
            elements.walletInput.focus();
        }
        
        // ============================================================
        // ===== API FUNCTIONS =========================================
        // ============================================================
        
        async function fetchTransactions() {
            const wallet = elements.walletInput.value.trim();
            
            if (!wallet) {
                setStatus('error', 'Please enter a wallet address');
                return;
            }
            
            // Validate wallet address
            if (!/^0x[a-fA-F0-9]{40}$/i.test(wallet)) {
                setStatus('error', 'Invalid wallet address (must be 0x + 40 hex characters)');
                return;
            }
            
            // Start loading
            state.isLoading = true;
            state.wallet = wallet;
            state.error = null;
            state.transactions = [];
            render();
            setStatus('loading', 'Fetching transactions...');
            elements.fetchBtn.disabled = true;
            
            try {
                // Build RPC request
                const payload = {
                    jsonrpc: '2.0',
                    id: 1,
                    method: CONFIG.RPC_METHOD,
                    params: [hex(CONFIG.FETCH_LIMIT), '0x0']
                };
                
                const response = await fetch(CONFIG.RPC_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error.message || 'RPC error');
                }
                
                const allTransactions = data.result || [];
                
                // Filter transactions for this wallet
                const walletLower = wallet.toLowerCase();
                const filtered = [];
                
                for (const tx of allTransactions) {
                    const txFrom = (tx.from || '').toLowerCase();
                    const txTo = (tx.to || '').toLowerCase();
                    
                    if (txFrom === walletLower || txTo === walletLower) {
                        const valueWei = tx.value || '0';
                        let valueMintme = 0;
                        try {
                            valueMintme = parseFloat(valueWei) / 1e18;
                        } catch {
                            valueMintme = 0;
                        }
                        
                        filtered.push({
                            hash: tx.transactionHash || tx.hash || 'N/A',
                            from: tx.from || 'N/A',
                            to: tx.to || 'N/A',
                            value: valueWei,
                            valueMintme: valueMintme,
                            timestamp: tx.timestamp || 'N/A',
                            blockNumber: tx.blockNumber || 'N/A',
                            direction: txTo === walletLower ? 'INCOMING' : 'OUTGOING'
                        });
                    }
                }
                
                state.transactions = filtered.slice(0, CONFIG.MAX_DISPLAY);
                
                if (filtered.length === 0) {
                    setStatus('idle', `No transactions found for ${truncateAddress(wallet)}`);
                } else {
                    setStatus('success', `Found ${filtered.length} transactions`);
                }
                
                render();
                
            } catch (error) {
                state.error = error.message;
                setStatus('error', `Error: ${error.message}`);
                render();
            } finally {
                state.isLoading = false;
                elements.fetchBtn.disabled = false;
            }
        }
        
        // ============================================================
        // ===== HELPER FUNCTIONS ======================================
        // ============================================================
        
        function hex(num) {
            return '0x' + num.toString(16);
        }
        
        // ============================================================
        // ===== STATUS FUNCTIONS ======================================
        // ============================================================
        
        function setStatus(type, message) {
            elements.statusDot.className = 'dot ' + type;
            elements.statusText.textContent = message;
        }
        
        function updateStatus(type, message) {
            setStatus(type, message);
        }
        
        // ============================================================
        // ===== RENDER FUNCTIONS ======================================
        // ============================================================
        
        function render() {
            renderSummary();
            renderTransactions();
            updateStats();
        }
        
        function renderSummary() {
            const txs = state.transactions;
            const total = txs.length;
            const incoming = txs.filter(t => t.direction === 'INCOMING');
            const outgoing = txs.filter(t => t.direction === 'OUTGOING');
            
            const totalIn = incoming.reduce((sum, t) => sum + t.valueMintme, 0);
            const totalOut = outgoing.reduce((sum, t) => sum + t.valueMintme, 0);
            const net = totalIn - totalOut;
            
            elements.summaryTotal.textContent = total;
            elements.summaryIncoming.textContent = incoming.length;
            elements.summaryOutgoing.textContent = outgoing.length;
            elements.summaryValueIn.textContent = formatValue(totalIn);
            elements.summaryValueOut.textContent = formatValue(totalOut);
            elements.summaryNet.textContent = formatValue(net);
            elements.summaryNet.style.color = net >= 0 ? '#6bcb77' : '#ff6b6b';
        }
        
        function renderTransactions() {
            const container = elements.transactionsContainer;
            const txs = state.transactions;
            
            if (state.isLoading) {
                container.innerHTML = `
                    <div class="loading-state">
                        <div class="spinner"></div>
                        <p>Fetching transactions from blockchain...</p>
                        <p style="color:#666; font-size:0.85rem; margin-top:10px;">
                            Scanning ${CONFIG.FETCH_LIMIT} recent transactions
                        </p>
                    </div>
                `;
                return;
            }
            
            if (state.error) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="icon">⚠️</div>
                        <h3 style="color:#ff6b6b;">Error</h3>
                        <p style="color:#ff6b6b;">${state.error}</p>
                        <p style="color:#666; font-size:0.85rem; margin-top:10px;">
                            Try checking the wallet at 
                            <a href="https://www.mintme.com/explorer/addr/${state.wallet}" 
                               target="_blank" 
                               style="color:#e94560;">
                                MintMe Explorer
                            </a>
                        </p>
                    </div>
                `;
                return;
            }
            
            if (txs.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="icon">🔍</div>
                        <h3>No transactions found</h3>
                        <p>This wallet has no transactions in the last ${CONFIG.FETCH_LIMIT} blocks</p>
                        <p style="color:#666; font-size:0.85rem; margin-top:10px;">
                            Try checking the wallet at 
                            <a href="https://www.mintme.com/explorer/addr/${state.wallet}" 
                               target="_blank" 
                               style="color:#e94560;">
                                MintMe Explorer
                            </a>
                        </p>
                    </div>
                `;
                return;
            }
            
            let html = '';
            for (const tx of txs) {
                const isIncoming = tx.direction === 'INCOMING';
                html += `
                    <div class="transaction-row">
                        <div class="hash" title="${tx.hash}">${truncateHash(tx.hash)}</div>
                        <div class="address" title="${tx.from}">${truncateAddress(tx.from)}</div>
                        <div class="address" title="${tx.to}">${truncateAddress(tx.to)}</div>
                        <div class="hide-mobile amount ${isIncoming ? 'incoming' : 'outgoing'}">
                            ${formatValue(tx.valueMintme)} MINTME
                        </div>
                        <div>
                            <span class="direction-badge ${isIncoming ? 'incoming' : 'outgoing'}">
                                ${isIncoming ? '⬇ IN' : '⬆ OUT'}
                            </span>
                        </div>
                        <div class="hide-mobile time">${formatTimestamp(tx.timestamp)}</div>
                    </div>
                `;
            }
            
            container.innerHTML = html;
        }
        
        function updateStats() {
            const txs = state.transactions;
            const total = txs.length;
            const incoming = txs.filter(t => t.direction === 'INCOMING');
            const outgoing = txs.filter(t => t.direction === 'OUTGOING');
            
            elements.totalTx.textContent = total;
            elements.incomingCount.textContent = incoming.length;
            elements.outgoingCount.textContent = outgoing.length;
        }
        
        // ============================================================
        // ===== ENTER KEY SUPPORT =====================================
        // ============================================================
        
        document.addEventListener('DOMContentLoaded', () => {
            elements.walletInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    fetchTransactions();
                }
            });
            
            // Auto-fetch on load
            setTimeout(fetchTransactions, 500);
        });
        
        // ============================================================
        // ===== EXPOSE TO GLOBAL ======================================
        // ============================================================
        
        window.fetchTransactions = fetchTransactions;
        window.setAddress = setAddress;
        window.clearAll = clearAll;
        
        console.log('🔍 MintMe Wallet Viewer loaded!');
        console.log('ℹ️  Enter a wallet address and click Fetch');
        console.log('📊 Found transactions will be displayed below');
    </script>
</body>
</html>
