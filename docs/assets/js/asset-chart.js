// Asset Evolution Chart
// Main page visualization

const dataLoader = new DataLoader();
let chartInstance = null;
let allAgentsData = {};
let isLogScale = false;

// Color palette for different agents
const agentColors = [
    '#00d4ff', // Cyan Blue
    '#00ffcc', // Cyan
    '#ff006e', // Hot Pink
    '#ffbe0b', // Yellow
    '#8338ec', // Purple
    '#3a86ff', // Blue
    '#fb5607', // Orange
    '#06ffa5'  // Mint
];

// Cache for loaded SVG images
const iconImageCache = {};

// Function to load SVG as image
function loadIconImage(iconPath) {
    return new Promise((resolve, reject) => {
        if (iconImageCache[iconPath]) {
            resolve(iconImageCache[iconPath]);
            return;
        }
        
        const img = new Image();
        img.onload = () => {
            iconImageCache[iconPath] = img;
            resolve(img);
        };
        img.onerror = reject;
        img.src = iconPath;
    });
}

// Initialize the page
async function init() {
    showLoading();

    try {
        // Load all agents data
        console.log('Loading all agents data...');
        allAgentsData = await dataLoader.loadAllAgentsData();
        console.log('Data loaded:', allAgentsData);

        // Preload all agent icons
        const agentNames = Object.keys(allAgentsData);
        const iconPromises = agentNames.map(agentName => {
            const iconPath = dataLoader.getAgentIcon(agentName);
            return loadIconImage(iconPath).catch(err => {
                console.warn(`Failed to load icon for ${agentName}:`, err);
            });
        });
        await Promise.all(iconPromises);
        console.log('Icons preloaded');

        // Update stats
        updateStats();

        // Create chart
        createChart();

        // Create legend
        createLegend();

        // Set up event listeners
        setupEventListeners();

    } catch (error) {
        console.error('Error initializing page:', error);
        alert('Failed to load trading data. Please check console for details.');
    } finally {
        hideLoading();
    }
}

// Update statistics cards
function updateStats() {
    const agentNames = Object.keys(allAgentsData);
    const agentCount = agentNames.length;

    // Calculate date range
    let minDate = null;
    let maxDate = null;

    agentNames.forEach(name => {
        const history = allAgentsData[name].assetHistory;
        if (history.length > 0) {
            const firstDate = history[0].date;
            const lastDate = history[history.length - 1].date;

            if (!minDate || firstDate < minDate) minDate = firstDate;
            if (!maxDate || lastDate > maxDate) maxDate = lastDate;
        }
    });

    // Find best performer
    let bestAgent = null;
    let bestReturn = -Infinity;

    agentNames.forEach(name => {
        const returnValue = allAgentsData[name].return;
        if (returnValue > bestReturn) {
            bestReturn = returnValue;
            bestAgent = name;
        }
    });

    // Update DOM
    document.getElementById('agent-count').textContent = agentCount;

    // Format date range for hourly data - show only dates without time
    const formatDateRange = (dateStr) => {
        if (!dateStr) return 'N/A';
        // If the date includes time (hourly format), format date only
        if (dateStr.includes(':')) {
            const date = new Date(dateStr);
            return date.toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            });
        }
        return dateStr;
    };

    document.getElementById('trading-period').textContent = minDate && maxDate ?
        `${formatDateRange(minDate)} to ${formatDateRange(maxDate)}` : 'N/A';
    document.getElementById('best-performer').textContent = bestAgent ?
        dataLoader.getAgentDisplayName(bestAgent) : 'N/A';
    document.getElementById('avg-return').textContent = bestAgent ?
        dataLoader.formatPercent(bestReturn) : 'N/A';
}

// Create the main chart
function createChart() {
    const ctx = document.getElementById('assetChart').getContext('2d');

    // Collect all unique dates and sort them
    const allDates = new Set();
    Object.keys(allAgentsData).forEach(agentName => {
        allAgentsData[agentName].assetHistory.forEach(h => allDates.add(h.date));
    });
    const sortedDates = Array.from(allDates).sort();

    const datasets = Object.keys(allAgentsData).map((agentName, index) => {
        const data = allAgentsData[agentName];
        let color, borderWidth, borderDash;
        
        // Special styling for QQQ benchmark
        if (agentName === 'QQQ') {
            color = dataLoader.getAgentBrandColor(agentName) || '#ff6b00';
            borderWidth = 2;
            borderDash = [5, 5]; // Dashed line for benchmark
        } else {
            color = agentColors[index % agentColors.length];
            borderWidth = 3;
            borderDash = [];
        }

        // Create data points for all dates, filling missing dates with null
        const chartData = sortedDates.map(date => {
            const historyEntry = data.assetHistory.find(h => h.date === date);
            return {
                x: date,
                y: historyEntry ? historyEntry.value : null
            };
        });

        return {
            label: dataLoader.getAgentDisplayName(agentName),
            data: chartData,
            borderColor: color,
            backgroundColor: agentName === 'QQQ' ? 'transparent' : createGradient(ctx, color),
            borderWidth: borderWidth,
            borderDash: borderDash,
            tension: 0.42, // Smooth curves for financial charts
            pointRadius: 0,
            pointHoverRadius: 7,
            pointHoverBackgroundColor: color,
            pointHoverBorderColor: '#fff',
            pointHoverBorderWidth: 3,
            fill: agentName !== 'QQQ', // No fill for QQQ benchmark
            agentName: agentName,
            agentIcon: dataLoader.getAgentIcon(agentName),
            cubicInterpolationMode: 'monotone' // Smooth, monotonic interpolation
        };
    });

    // Create gradient for area fills
    function createGradient(ctx, color) {
        // Parse color and create gradient
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, color + '30'); // 30% opacity at top
        gradient.addColorStop(0.5, color + '15'); // 15% opacity at middle
        gradient.addColorStop(1, color + '05'); // 5% opacity at bottom
        return gradient;
    }

    // Custom plugin to draw icons on chart lines
    const iconPlugin = {
        id: 'iconLabels',
        afterDatasetsDraw: (chart) => {
            const ctx = chart.ctx;

            chart.data.datasets.forEach((dataset, datasetIndex) => {
                const meta = chart.getDatasetMeta(datasetIndex);
                if (!meta.hidden && dataset.data.length > 0) {
                    // Get the last point
                    const lastPoint = meta.data[meta.data.length - 1];

                    if (lastPoint) {
                        const x = lastPoint.x;
                        const y = lastPoint.y;

                        ctx.save();

                        // Draw background circle with glow
                        const iconSize = 30;

                        // Outer glow
                        ctx.shadowColor = dataset.borderColor;
                        ctx.shadowBlur = 15;
                        ctx.fillStyle = dataset.borderColor;
                        ctx.beginPath();
                        ctx.arc(x + 22, y, iconSize / 2, 0, Math.PI * 2);
                        ctx.fill();

                        // Reset shadow
                        ctx.shadowBlur = 0;

                        // Draw icon image if loaded
                        if (iconImageCache[dataset.agentIcon]) {
                            const img = iconImageCache[dataset.agentIcon];
                            const imgSize = iconSize * 0.6; // Icon slightly smaller than circle
                            ctx.drawImage(img, x + 22 - imgSize/2, y - imgSize/2, imgSize, imgSize);
                        }

                        ctx.restore();
                    }
                }
            });
        }
    };

    chartInstance = new Chart(ctx, {
        type: 'line',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            resizeDelay: 200,
            layout: {
                padding: {
                    right: 50,
                    top: 10,
                    bottom: 10
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            },
            elements: {
                line: {
                    borderJoinStyle: 'round',
                    borderCapStyle: 'round'
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false,
                    external: function(context) {
                        // Custom HTML tooltip
                        const tooltipModel = context.tooltip;
                        let tooltipEl = document.getElementById('chartjs-tooltip');

                        // Create element on first render
                        if (!tooltipEl) {
                            tooltipEl = document.createElement('div');
                            tooltipEl.id = 'chartjs-tooltip';
                            tooltipEl.innerHTML = '<div class="tooltip-container"></div>';
                            document.body.appendChild(tooltipEl);
                        }

                        // Hide if no tooltip
                        if (tooltipModel.opacity === 0) {
                            tooltipEl.style.opacity = 0;
                            return;
                        }

                        // Set Text
                        if (tooltipModel.body) {
                            const dataPoints = tooltipModel.dataPoints || [];

                            // Sort data points by value at this time point (descending)
                            const sortedPoints = [...dataPoints].sort((a, b) => {
                                const valueA = a.parsed.y || 0;
                                const valueB = b.parsed.y || 0;
                                return valueB - valueA;
                            });

                            // Format title (date/time)
                            const titleLines = tooltipModel.title || [];
                            let titleHtml = '';
                            if (titleLines.length > 0) {
                                const dateStr = titleLines[0];
                                if (dateStr && dateStr.includes(':')) {
                                    const date = new Date(dateStr);
                                    titleHtml = date.toLocaleString('en-US', {
                                        month: 'short',
                                        day: 'numeric',
                                        year: 'numeric',
                                        hour: '2-digit',
                                        minute: '2-digit'
                                    });
                                } else {
                                    titleHtml = dateStr;
                                }
                            }

                            // Build body HTML with logos and ranked data
                            let innerHtml = `<div class="tooltip-title">${titleHtml}</div>`;
                            innerHtml += '<div class="tooltip-body">';

                            sortedPoints.forEach((dataPoint, index) => {
                                const dataset = dataPoint.dataset;
                                const agentName = dataset.agentName;
                                const displayName = dataset.label;
                                const value = dataPoint.parsed.y;
                                const icon = dataLoader.getAgentIcon(agentName);
                                const color = dataset.borderColor;

                                // Add ranking badge
                                const rankBadge = `<span class="rank-badge">#${index + 1}</span>`;

                                innerHtml += `
                                    <div class="tooltip-row">
                                        ${rankBadge}
                                        <img src="${icon}" class="tooltip-icon" alt="${displayName}">
                                        <span class="tooltip-label" style="color: ${color}">${displayName}</span>
                                        <span class="tooltip-value">${dataLoader.formatCurrency(value)}</span>
                                    </div>
                                `;
                            });

                            innerHtml += '</div>';

                            const container = tooltipEl.querySelector('.tooltip-container');
                            container.innerHTML = innerHtml;
                        }

                        const position = context.chart.canvas.getBoundingClientRect();
                        const tooltipWidth = tooltipEl.offsetWidth || 300;
                        const tooltipHeight = tooltipEl.offsetHeight || 200;

                        // Smart positioning to prevent overflow
                        let left = position.left + window.pageXOffset + tooltipModel.caretX;
                        let top = position.top + window.pageYOffset + tooltipModel.caretY;

                        // Offset to prevent covering the hover point
                        const offset = 15;
                        left += offset;
                        top -= offset;

                        // Check if tooltip would go off right edge
                        const viewportWidth = window.innerWidth;
                        const viewportHeight = window.innerHeight;

                        if (left + tooltipWidth > viewportWidth - 20) {
                            // Position to the left of the cursor instead
                            left = position.left + window.pageXOffset + tooltipModel.caretX - tooltipWidth - offset;
                        }

                        // Check if tooltip would go off bottom edge
                        if (top + tooltipHeight > viewportHeight - 20) {
                            top = viewportHeight - tooltipHeight - 20;
                        }

                        // Check if tooltip would go off top edge
                        if (top < 20) {
                            top = 20;
                        }

                        // Check if tooltip would go off left edge
                        if (left < 20) {
                            left = 20;
                        }

                        // Display, position, and set styles
                        tooltipEl.style.opacity = 1;
                        tooltipEl.style.position = 'absolute';
                        tooltipEl.style.left = left + 'px';
                        tooltipEl.style.top = top + 'px';
                        tooltipEl.style.pointerEvents = 'none';
                        tooltipEl.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
                        tooltipEl.style.transform = 'translateZ(0)'; // GPU acceleration
                    }
                }
            },
            scales: {
                x: {
                    type: 'category',
                    labels: sortedDates,
                    grid: {
                        color: 'rgba(45, 55, 72, 0.3)',
                        drawBorder: false,
                        lineWidth: 1
                    },
                    ticks: {
                        color: '#a0aec0',
                        maxRotation: 45,
                        minRotation: 45,
                        autoSkip: true,
                        maxTicksLimit: 15,
                        font: {
                            size: 11
                        },
                        callback: function(value, index) {
                            // Format hourly timestamps for better readability
                            const dateStr = this.getLabelForValue(value);
                            if (!dateStr) return '';

                            // If it's an hourly timestamp (contains time)
                            if (dateStr.includes(':')) {
                                const date = new Date(dateStr);
                                // Show date and hour
                                const month = (date.getMonth() + 1).toString().padStart(2, '0');
                                const day = date.getDate().toString().padStart(2, '0');
                                const hour = date.getHours().toString().padStart(2, '0');
                                return `${month}/${day} ${hour}:00`;
                            }
                            return dateStr;
                        }
                    }
                },
                y: {
                    type: isLogScale ? 'logarithmic' : 'linear',
                    grid: {
                        color: 'rgba(45, 55, 72, 0.3)',
                        drawBorder: false,
                        lineWidth: 1
                    },
                    ticks: {
                        color: '#a0aec0',
                        callback: function(value) {
                            return dataLoader.formatCurrency(value);
                        },
                        font: {
                            size: 11
                        }
                    }
                }
            }
        },
        plugins: [iconPlugin]
    });
}

// Create legend
function createLegend() {
    const legendContainer = document.getElementById('agentLegend');
    legendContainer.innerHTML = '';

    Object.keys(allAgentsData).forEach((agentName, index) => {
        const data = allAgentsData[agentName];
        let color, borderStyle;
        
        // Special styling for QQQ benchmark
        if (agentName === 'QQQ') {
            color = dataLoader.getAgentBrandColor(agentName) || '#ff6b00';
            borderStyle = 'dashed';
        } else {
            color = agentColors[index % agentColors.length];
            borderStyle = 'solid';
        }
        
        const returnValue = data.return;
        const returnClass = returnValue >= 0 ? 'positive' : 'negative';
        const iconPath = dataLoader.getAgentIcon(agentName);
        const brandColor = dataLoader.getAgentBrandColor(agentName);

        const legendItem = document.createElement('div');
        legendItem.className = 'legend-item';
        legendItem.innerHTML = `
            <div class="legend-icon" ${brandColor ? `style="background: ${brandColor}20;"` : ''}>
                <img src="${iconPath}" alt="${agentName}" class="legend-icon-img" />
            </div>
            <div class="legend-color" style="background: ${color}; border-style: ${borderStyle};"></div>
            <div class="legend-info">
                <div class="legend-name">${dataLoader.getAgentDisplayName(agentName)}</div>
                <div class="legend-return ${returnClass}">${dataLoader.formatPercent(returnValue)}</div>
            </div>
        `;

        legendContainer.appendChild(legendItem);
    });
}

// Toggle between linear and log scale
function toggleScale() {
    isLogScale = !isLogScale;

    const button = document.getElementById('toggle-log');
    button.textContent = isLogScale ? 'Log Scale' : 'Linear Scale';

    // Update chart
    if (chartInstance) {
        chartInstance.destroy();
    }
    createChart();
}

// Export chart data as CSV
function exportData() {
    let csv = 'Date,';

    // Header row with agent names
    const agentNames = Object.keys(allAgentsData);
    csv += agentNames.map(name => dataLoader.getAgentDisplayName(name)).join(',') + '\n';

    // Collect all unique dates
    const allDates = new Set();
    agentNames.forEach(name => {
        allAgentsData[name].assetHistory.forEach(h => allDates.add(h.date));
    });

    // Sort dates
    const sortedDates = Array.from(allDates).sort();

    // Data rows
    sortedDates.forEach(date => {
        const row = [date];
        agentNames.forEach(name => {
            const history = allAgentsData[name].assetHistory;
            const entry = history.find(h => h.date === date);
            row.push(entry ? entry.value.toFixed(2) : '');
        });
        csv += row.join(',') + '\n';
    });

    // Download CSV
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'aitrader_asset_evolution.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

// Set up event listeners
function setupEventListeners() {
    document.getElementById('toggle-log').addEventListener('click', toggleScale);
    document.getElementById('export-chart').addEventListener('click', exportData);

    // Scroll to top button
    const scrollBtn = document.getElementById('scrollToTop');
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            scrollBtn.classList.add('visible');
        } else {
            scrollBtn.classList.remove('visible');
        }
    });

    scrollBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Window resize handler for chart responsiveness
    let resizeTimeout;
    const handleResize = () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            if (chartInstance) {
                console.log('Resizing chart...'); // Debug log
                chartInstance.resize();
                chartInstance.update('none'); // Force update without animation
            }
        }, 100); // Faster response
    };

    window.addEventListener('resize', handleResize);

    // Also handle orientation change for mobile
    window.addEventListener('orientationchange', handleResize);
}

// Loading overlay controls
function showLoading() {
    document.getElementById('loadingOverlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', init);
