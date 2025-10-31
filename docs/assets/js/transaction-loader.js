// Transaction and Leaderboard Data Loader
// Loads transaction history and agent performance data

class TransactionLoader {
    constructor() {
        this.allTransactions = [];
        this.leaderboardData = [];
    }

    // Load all transactions from all agents
    async loadAllTransactions() {
        const config = window.configLoader;
        const agents = config.getEnabledAgents();

        const promises = agents.map(agent => this.loadAgentTransactions(agent.folder));
        const results = await Promise.all(promises);

        // Flatten and sort by date (most recent first)
        this.allTransactions = results
            .flat()
            .sort((a, b) => new Date(b.date) - new Date(a.date));

        return this.allTransactions;
    }

    // Load transactions for a single agent
    async loadAgentTransactions(agentFolder) {
        try {
            const positionPath = `data/agent_data/${agentFolder}/position/position.jsonl`;
            const response = await fetch(positionPath);
            const text = await response.text();

            const transactions = text
                .trim()
                .split('\n')
                .filter(line => line.trim())
                .map(line => {
                    const data = JSON.parse(line);
                    return {
                        agentFolder: agentFolder,
                        date: data.date,
                        id: data.id,
                        action: data.this_action?.action || 'initial',
                        symbol: data.this_action?.symbol || '',
                        amount: data.this_action?.amount || 0,
                        positions: data.positions,
                        cash: data.CASH || 0
                    };
                })
                .filter(t => {
                    // Filter out non-trades: no action, no_trade, initial state, or 0 amount
                    if (!t.action || t.action === 'initial' || t.action === 'no_trade') {
                        return false;
                    }
                    // Filter out transactions with 0 amount (no real trade)
                    if (!t.amount || t.amount === 0) {
                        return false;
                    }
                    // Filter out transactions with no symbol
                    if (!t.symbol || t.symbol === '') {
                        return false;
                    }
                    return true;
                });

            return transactions;
        } catch (error) {
            console.warn(`Failed to load transactions for ${agentFolder}:`, error);
            return [];
        }
    }

    // Load agent's thinking/response for a specific transaction
    async loadAgentThinking(agentFolder, date) {
        try {
            const logPath = `data/agent_data/${agentFolder}/log/${date}/log.jsonl`;
            const response = await fetch(logPath);
            const text = await response.text();

            const lines = text.trim().split('\n').filter(line => line.trim());

            // Find the last assistant message
            for (let i = lines.length - 1; i >= 0; i--) {
                const data = JSON.parse(lines[i]);
                if (data.new_messages && data.new_messages.length > 0) {
                    const assistantMsg = data.new_messages.find(msg => msg.role === 'assistant');
                    if (assistantMsg) {
                        // Remove <FINISH_SIGNAL> tag if present
                        return assistantMsg.content.replace(/<FINISH_SIGNAL>/g, '').trim();
                    }
                }
            }

            return 'No reasoning available.';
        } catch (error) {
            console.warn(`Failed to load thinking for ${agentFolder} at ${date}:`, error);
            return 'Reasoning not available.';
        }
    }

    // Calculate profit for a transaction
    async calculateTransactionProfit(transaction) {
        // For now, return null - will be calculated when price data is integrated
        // This would need: buy price at transaction time, sell price (if sell), or current price
        return null;
    }

    // Build leaderboard data
    async buildLeaderboard(allAgentsData) {
        const leaderboard = [];

        for (const [agentName, data] of Object.entries(allAgentsData)) {
            const assetHistory = data.assetHistory || [];
            const initialValue = assetHistory[0]?.value || 10000;
            const finalValue = assetHistory[assetHistory.length - 1]?.value || initialValue;
            const gain = finalValue - initialValue;
            const gainPercent = ((finalValue - initialValue) / initialValue) * 100;

            leaderboard.push({
                agentName: agentName,
                displayName: window.configLoader.getDisplayName(agentName),
                icon: window.configLoader.getIcon(agentName),
                color: window.configLoader.getColor(agentName),
                initialValue: initialValue,
                currentValue: finalValue,
                gain: gain,
                gainPercent: gainPercent,
                return: data.return || gainPercent
            });
        }

        // Sort by current value (descending)
        leaderboard.sort((a, b) => b.currentValue - a.currentValue);

        // Add rank
        leaderboard.forEach((item, index) => {
            item.rank = index + 1;
        });

        this.leaderboardData = leaderboard;
        return leaderboard;
    }

    // Get most recent N transactions
    getMostRecentTransactions(n = 100) {
        return this.allTransactions.slice(0, n);
    }

    // Format currency
    formatCurrency(value) {
        if (value === null || value === undefined) return 'N/A';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    }

    // Format percent
    formatPercent(value) {
        if (value === null || value === undefined) return 'N/A';
        const sign = value >= 0 ? '+' : '';
        return `${sign}${value.toFixed(2)}%`;
    }

    // Format date/time
    formatDateTime(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    // Get action icon
    getActionIcon(action) {
        return action === 'buy' ? '📈' : '📉';
    }

    // Get action color
    getActionColor(action) {
        return action === 'buy' ? 'var(--success)' : 'var(--danger)';
    }
}

// Create global instance
window.transactionLoader = new TransactionLoader();
