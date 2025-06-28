// Chart.js utility functions for APIWatch dashboard

// Global chart instances
let charts = {};

/**
 * Create a response time chart for an endpoint
 * @param {string} canvasId - The canvas element ID
 * @param {Array} data - Chart data array
 * @param {Object} options - Chart options
 */
function createResponseTimeChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element with ID '${canvasId}' not found`);
        return null;
    }

    // Destroy existing chart if it exists
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Response Time (ms)'
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Time'
                }
            }
        },
        plugins: {
            legend: {
                display: true,
                position: 'top'
            },
            tooltip: {
                mode: 'index',
                intersect: false,
                callbacks: {
                    afterLabel: function(context) {
                        const index = context.dataIndex;
                        if (data.statusCodes && data.statusCodes[index]) {
                            return `Status: ${data.statusCodes[index]}`;
                        }
                        return '';
                    }
                }
            }
        },
        interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
        }
    };

    const chartOptions = { ...defaultOptions, ...options };

    const chartData = {
        labels: data.labels || [],
        datasets: [{
            label: 'Response Time (ms)',
            data: data.responseTimes || [],
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderWidth: 2,
            tension: 0.1,
            pointRadius: 3,
            pointHoverRadius: 5
        }]
    };

    charts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: chartOptions
    });

    return charts[canvasId];
}

/**
 * Create a status code distribution chart
 * @param {string} canvasId - The canvas element ID
 * @param {Array} data - Status code data
 */
function createStatusCodeChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element with ID '${canvasId}' not found`);
        return null;
    }

    // Destroy existing chart if it exists
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    const statusColors = {
        '2xx': '#27ae60',
        '3xx': '#3498db',
        '4xx': '#f39c12',
        '5xx': '#e74c3c',
        'error': '#95a5a6'
    };

    const chartData = {
        labels: data.labels || [],
        datasets: [{
            data: data.values || [],
            backgroundColor: data.colors || Object.values(statusColors),
            borderWidth: 2,
            borderColor: '#fff'
        }]
    };

    charts[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });

    return charts[canvasId];
}

/**
 * Create a success rate trend chart
 * @param {string} canvasId - The canvas element ID
 * @param {Array} data - Success rate data over time
 */
function createSuccessRateChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element with ID '${canvasId}' not found`);
        return null;
    }

    // Destroy existing chart if it exists
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    const chartData = {
        labels: data.labels || [],
        datasets: [{
            label: 'Success Rate (%)',
            data: data.successRates || [],
            borderColor: 'rgb(39, 174, 96)',
            backgroundColor: 'rgba(39, 174, 96, 0.2)',
            borderWidth: 2,
            tension: 0.1,
            fill: true
        }]
    };

    charts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Success Rate (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });

    return charts[canvasId];
}

/**
 * Create a performance comparison chart for multiple endpoints
 * @param {string} canvasId - The canvas element ID
 * @param {Array} data - Performance data for multiple endpoints
 */
function createPerformanceComparisonChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element with ID '${canvasId}' not found`);
        return null;
    }

    // Destroy existing chart if it exists
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    const colors = [
        'rgb(75, 192, 192)',
        'rgb(255, 99, 132)',
        'rgb(54, 162, 235)',
        'rgb(255, 205, 86)',
        'rgb(153, 102, 255)',
        'rgb(255, 159, 64)'
    ];

    const datasets = data.endpoints.map((endpoint, index) => ({
        label: endpoint.name,
        data: endpoint.responseTimes || [],
        borderColor: colors[index % colors.length],
        backgroundColor: colors[index % colors.length].replace('rgb', 'rgba').replace(')', ', 0.2)'),
        borderWidth: 2,
        tension: 0.1
    }));

    const chartData = {
        labels: data.labels || [],
        datasets: datasets
    };

    charts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Response Time (ms)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });

    return charts[canvasId];
}

/**
 * Update chart data dynamically
 * @param {string} chartId - The chart ID
 * @param {Array} newData - New data to update
 * @param {boolean} append - Whether to append or replace data
 */
function updateChartData(chartId, newData, append = false) {
    if (!charts[chartId]) {
        console.error(`Chart with ID '${chartId}' not found`);
        return;
    }

    const chart = charts[chartId];
    
    if (append) {
        // Append new data points
        chart.data.labels.push(...newData.labels);
        chart.data.datasets.forEach((dataset, index) => {
            dataset.data.push(...newData.datasets[index].data);
        });
    } else {
        // Replace all data
        chart.data.labels = newData.labels;
        chart.data.datasets = newData.datasets;
    }

    chart.update('none'); // Update without animation for better performance
}

/**
 * Destroy all charts
 */
function destroyAllCharts() {
    Object.values(charts).forEach(chart => {
        if (chart) {
            chart.destroy();
        }
    });
    charts = {};
}

/**
 * Format timestamp for chart labels
 * @param {string} timestamp - ISO timestamp string
 * @param {string} format - Format type ('time', 'date', 'datetime')
 * @returns {string} Formatted timestamp
 */
function formatTimestamp(timestamp, format = 'time') {
    const date = new Date(timestamp);
    
    switch (format) {
        case 'time':
            return date.toLocaleTimeString();
        case 'date':
            return date.toLocaleDateString();
        case 'datetime':
            return date.toLocaleString();
        default:
            return date.toLocaleTimeString();
    }
}

/**
 * Process monitoring data for chart display
 * @param {Array} monitoringData - Raw monitoring data from API
 * @returns {Object} Processed data for charts
 */
function processMonitoringData(monitoringData) {
    const labels = monitoringData.map(item => formatTimestamp(item.timestamp));
    const responseTimes = monitoringData.map(item => item.response_time);
    const statusCodes = monitoringData.map(item => item.status_code);
    const isSuccess = monitoringData.map(item => item.is_success);

    return {
        labels,
        responseTimes,
        statusCodes,
        isSuccess
    };
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        createResponseTimeChart,
        createStatusCodeChart,
        createSuccessRateChart,
        createPerformanceComparisonChart,
        updateChartData,
        destroyAllCharts,
        formatTimestamp,
        processMonitoringData
    };
}
