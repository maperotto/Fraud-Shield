// Dashboard Configuration
const UPDATE_INTERVAL = 5000; // 5 seconds
const CHART_HOURS = 24;

// Chart instances
let transactionFlowChart = null;
let riskDistributionChart = null;

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    fetchDashboardData();
    setInterval(fetchDashboardData, UPDATE_INTERVAL);
});

// Initialize Charts
function initializeCharts() {
    // Transaction Flow Chart
    const flowCtx = document.getElementById('transactionFlowChart').getContext('2d');
    
    const hours = [];
    for (let i = CHART_HOURS - 1; i >= 0; i--) {
        const hour = new Date();
        hour.setHours(hour.getHours() - i);
        hours.push(hour.getHours().toString().padStart(2, '0') + ':00');
    }
    
    transactionFlowChart = new Chart(flowCtx, {
        type: 'line',
        data: {
            labels: hours,
            datasets: [
                {
                    label: 'Transações',
                    data: Array(CHART_HOURS).fill(0),
                    borderColor: '#00D9FF',
                    backgroundColor: 'rgba(0, 217, 255, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointBackgroundColor: '#00D9FF',
                    pointBorderColor: '#0a0e1a',
                    pointBorderWidth: 2
                },
                {
                    label: 'Fraudes',
                    data: Array(CHART_HOURS).fill(0),
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: false,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointBackgroundColor: '#ef4444',
                    pointBorderColor: '#0a0e1a',
                    pointBorderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#1a2332',
                    titleColor: '#f7fafc',
                    bodyColor: '#a0aec0',
                    borderColor: '#2d3748',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(45, 55, 72, 0.3)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#718096',
                        maxRotation: 0
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(45, 55, 72, 0.3)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#718096'
                    },
                    beginAtZero: true
                }
            }
        }
    });

    // Risk Distribution Chart
    const riskCtx = document.getElementById('riskDistributionChart').getContext('2d');
    
    riskDistributionChart = new Chart(riskCtx, {
        type: 'doughnut',
        data: {
            labels: ['Aprovadas', 'Em análise', 'Bloqueadas', 'Revisão manual'],
            datasets: [{
                data: [0, 0, 0, 0],
                backgroundColor: [
                    '#10b981',
                    '#f59e0b',
                    '#ef4444',
                    '#8b5cf6'
                ],
                borderWidth: 0,
                spacing: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '75%',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#1a2332',
                    titleColor: '#f7fafc',
                    bodyColor: '#a0aec0',
                    borderColor: '#2d3748',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return label + ': ' + percentage + '%';
                        }
                    }
                }
            }
        }
    });
}

// Fetch Dashboard Data
async function fetchDashboardData() {
    try {
        const response = await fetch('/api/dashboard/metrics');
        if (!response.ok) throw new Error('Failed to fetch data');
        
        const data = await response.json();
        updateMetrics(data.metrics);
        updateCharts(data.charts);
        updateAlerts(data.alerts);
        updateBehaviorMetrics(data.behavior);
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
        // Use mock data for demonstration
        useMockData();
    }
}

// Update Metrics Cards
function updateMetrics(metrics) {
    if (!metrics) return;
    
    // Transactions Today
    animateValue('transactionsToday', parseInt(document.getElementById('transactionsToday').innerText.replace(/,/g, '')) || 0, metrics.transactions_today, 1000);
    document.getElementById('transactionsChange').innerText = formatChange(metrics.transactions_change);
    document.getElementById('transactionsChange').className = 'metric-change ' + (metrics.transactions_change >= 0 ? 'positive' : 'negative');
    
    // Frauds Detected
    animateValue('fraudsDetected', parseInt(document.getElementById('fraudsDetected').innerText) || 0, metrics.frauds_detected, 1000);
    document.getElementById('fraudsChange').innerText = formatChange(metrics.frauds_change);
    document.getElementById('fraudsChange').className = 'metric-change ' + (metrics.frauds_change >= 0 ? 'negative' : 'positive');
    
    // Precision Rate
    document.getElementById('precisionRate').innerText = metrics.precision_rate.toFixed(2) + '%';
    document.getElementById('precisionChange').innerText = formatChange(metrics.precision_change, true);
    document.getElementById('precisionChange').className = 'metric-change ' + (metrics.precision_change >= 0 ? 'positive' : 'negative');
    
    // Response Time
    document.getElementById('responseTime').innerText = metrics.response_time + 'ms';
    document.getElementById('responseChange').innerText = formatChange(metrics.response_time_change, false, 'ms');
    document.getElementById('responseChange').className = 'metric-change ' + (metrics.response_time_change >= 0 ? 'negative' : 'positive');
}

// Update Charts
function updateCharts(charts) {
    if (!charts) return;
    
    // Update Transaction Flow Chart
    if (charts.transaction_flow && transactionFlowChart) {
        transactionFlowChart.data.datasets[0].data = charts.transaction_flow.transactions;
        transactionFlowChart.data.datasets[1].data = charts.transaction_flow.frauds;
        transactionFlowChart.update('none');
    }
    
    // Update Risk Distribution Chart
    if (charts.risk_distribution && riskDistributionChart) {
        const dist = charts.risk_distribution;
        riskDistributionChart.data.datasets[0].data = [
            dist.approved,
            dist.analyzing,
            dist.blocked,
            dist.review
        ];
        riskDistributionChart.update('none');
        
        // Update risk stats text
        const total = dist.approved + dist.analyzing + dist.blocked + dist.review;
        if (total > 0) {
            const riskStats = document.querySelectorAll('.risk-stat .risk-value');
            riskStats[0].innerText = ((dist.approved / total) * 100).toFixed(1) + '%';
            riskStats[1].innerText = ((dist.analyzing / total) * 100).toFixed(1) + '%';
            riskStats[2].innerText = ((dist.blocked / total) * 100).toFixed(1) + '%';
            riskStats[3].innerText = ((dist.review / total) * 100).toFixed(1) + '%';
        }
    }
}

// Update Alerts
function updateAlerts(alerts) {
    if (!alerts || alerts.length === 0) return;
    
    const alertsList = document.getElementById('alertsList');
    alertsList.innerHTML = '';
    
    alerts.forEach(alert => {
        const alertItem = document.createElement('div');
        alertItem.className = `alert-item ${alert.severity.toLowerCase()}`;
        alertItem.innerHTML = `
            <div class="alert-header">
                <div class="alert-title">${alert.title}</div>
                <div class="alert-badge ${alert.severity.toLowerCase()}">${alert.severity}</div>
            </div>
            <div class="alert-details">${alert.details}</div>
            <div class="alert-time">${alert.time}</div>
        `;
        alertsList.appendChild(alertItem);
    });
}

// Update Behavior Metrics
function updateBehaviorMetrics(behavior) {
    if (!behavior) return;
    
    const metricsContainer = document.getElementById('behaviorMetrics');
    metricsContainer.innerHTML = '';
    
    behavior.forEach(metric => {
        const metricDiv = document.createElement('div');
        metricDiv.className = 'behavior-metric';
        
        const color = getColorForMetric(metric.value);
        
        metricDiv.innerHTML = `
            <div class="behavior-label">
                <span>${metric.label}</span>
                <span class="behavior-value">${metric.value}%</span>
            </div>
            <div class="behavior-bar">
                <div class="behavior-fill" style="width: ${metric.value}%; background: ${color};"></div>
            </div>
        `;
        metricsContainer.appendChild(metricDiv);
    });
}

// Helper Functions
function formatChange(value, isPercentage = true, suffix = '%') {
    const sign = value >= 0 ? '+' : '';
    if (isPercentage) {
        return sign + value.toFixed(2) + suffix;
    }
    return sign + value + suffix;
}

function animateValue(elementId, start, end, duration) {
    const element = document.getElementById(elementId);
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.innerText = Math.floor(current).toLocaleString();
    }, 16);
}

function getColorForMetric(value) {
    if (value >= 70) return '#ef4444'; // Red for high risk
    if (value >= 40) return '#f59e0b'; // Orange for medium risk
    if (value >= 20) return '#fbbf24'; // Yellow for low-medium risk
    return '#10b981'; // Green for low risk
}

function getTimeAgo(minutes) {
    if (minutes < 1) return 'Agora';
    if (minutes === 1) return '1 min atrás';
    if (minutes < 60) return minutes + ' min atrás';
    const hours = Math.floor(minutes / 60);
    if (hours === 1) return '1 hora atrás';
    return hours + ' horas atrás';
}

// Mock Data for demonstration when API is not available
function useMockData() {
    // Generate realistic mock data
    const metrics = {
        transactions_today: 32847,
        transactions_change: 12.5,
        frauds_detected: 72,
        frauds_change: 3.2,
        precision_rate: 99.78,
        precision_change: 0.12,
        response_time: 23,
        response_time_change: -8
    };
    
    const transactionFlow = {
        transactions: generateFlowData(1500, 5000),
        frauds: generateFlowData(0, 50)
    };
    
    const riskDistribution = {
        approved: 30954,
        analyzing: 1018,
        blocked: 591,
        review: 284
    };
    
    const alerts = [
        {
            title: 'Transação incomum detectada — desvio de 340% do padrão',
            details: 'usr_8x92k    R$ 12.450,00',
            time: '2 min atrás',
            severity: 'HIGH'
        },
        {
            title: 'Login de nova localização geográfica',
            details: 'usr_3m71q    R$ 890,00',
            time: '8 min atrás',
            severity: 'MEDIUM'
        },
        {
            title: 'Transação verificada após autenticação adicional',
            details: 'usr_5p44w    R$ 3.200,00',
            time: '15 min atrás',
            severity: 'OK'
        },
        {
            title: 'Múltiplas transações rápidas — possível bot',
            details: 'usr_1a09z    R$ 28.900,00',
            time: '22 min atrás',
            severity: 'HIGH'
        },
        {
            title: 'Horário fora do padrão habitual do usuário',
            details: 'usr_7k33e    R$ 450,00',
            time: '31 min atrás',
            severity: 'LOW'
        }
    ];
    
    const behavior = [
        { label: 'Desvio de Valor Médio', value: 72 },
        { label: 'Frequência Anômala', value: 45 },
        { label: 'Risco Geográfico', value: 88 },
        { label: 'Consistência Temporal', value: 23 },
        { label: 'Score de Confiança', value: 61 }
    ];
    
    updateMetrics(metrics);
    updateCharts({
        transaction_flow: transactionFlow,
        risk_distribution: riskDistribution
    });
    updateAlerts(alerts);
    updateBehaviorMetrics(behavior);
}

function generateFlowData(min, max) {
    const data = [];
    let lastValue = Math.floor(Math.random() * (max - min) + min);
    
    for (let i = 0; i < CHART_HOURS; i++) {
        const change = (Math.random() - 0.5) * (max * 0.3);
        lastValue = Math.max(min, Math.min(max, lastValue + change));
        data.push(Math.floor(lastValue));
    }
    
    return data;
}

// Initialize with mock data on first load
useMockData();
