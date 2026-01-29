/**
 * ATROZ Dashboard - Enhanced Analytics & Visualization Module
 * ============================================================
 *
 * Provides advanced data visualization and analytics capabilities:
 * - Interactive data mining queries
 * - Comparative analysis visualizations
 * - Trend analysis with forecasting
 * - Gap analysis dashboards
 * - Performance benchmarking
 * - Correlation heatmaps
 * - Municipality drill-down
 * - Export capabilities
 *
 * Version: 1.0.0
 */

class AtrozAnalytics {
    constructor(apiBaseUrl = '/api/v1') {
        this.apiBaseUrl = apiBaseUrl;
        this.charts = {};
        this.currentData = {};
    }

    /**
     * Execute data mining query
     */
    async executeDataMiningQuery(queryParams) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/data-mining/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(queryParams)
            });

            if (!response.ok) {
                throw new Error(`Query failed: ${response.statusText}`);
            }

            const result = await response.json();
            this.currentData.miningResult = result;
            return result;
        } catch (error) {
            console.error('Data mining query failed:', error);
            throw error;
        }
    }

    /**
     * Get municipality profile with comprehensive data
     */
    async getMunicipalityProfile(municipalityCode) {
        try {
            const response = await fetch(
                `${this.apiBaseUrl}/data-mining/municipality/${municipalityCode}`
            );

            if (!response.ok) {
                throw new Error(`Failed to load municipality profile: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to load municipality profile:', error);
            throw error;
        }
    }

    /**
     * Generate comparative analysis between two entities
     */
    async generateComparativeAnalysis(entityA, entityB, entityType = 'municipality') {
        try {
            const response = await fetch(`${this.apiBaseUrl}/analytics/comparative`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    entity_a: entityA,
                    entity_b: entityB,
                    entity_type: entityType
                })
            });

            if (!response.ok) {
                throw new Error(`Comparative analysis failed: ${response.statusText}`);
            }

            const result = await response.json();
            this.currentData.comparativeAnalysis = result;
            return result;
        } catch (error) {
            console.error('Comparative analysis failed:', error);
            throw error;
        }
    }

    /**
     * Generate trend analysis for an entity
     */
    async generateTrendAnalysis(entity, entityType = 'municipality', timeWindowDays = 90) {
        try {
            const response = await fetch(
                `${this.apiBaseUrl}/analytics/trend/${entity}?entity_type=${entityType}&time_window_days=${timeWindowDays}`
            );

            if (!response.ok) {
                throw new Error(`Trend analysis failed: ${response.statusText}`);
            }

            const result = await response.json();
            this.currentData.trendAnalysis = result;
            return result;
        } catch (error) {
            console.error('Trend analysis failed:', error);
            throw error;
        }
    }

    /**
     * Generate gap analysis for an entity
     */
    async generateGapAnalysis(entity, entityType = 'municipality', targetLevel = 'macro') {
        try {
            const response = await fetch(
                `${this.apiBaseUrl}/analytics/gap/${entity}?entity_type=${entityType}&target_level=${targetLevel}`
            );

            if (!response.ok) {
                throw new Error(`Gap analysis failed: ${response.statusText}`);
            }

            const result = await response.json();
            this.currentData.gapAnalysis = result;
            return result;
        } catch (error) {
            console.error('Gap analysis failed:', error);
            throw error;
        }
    }

    /**
     * Generate performance benchmark
     */
    async generateBenchmark(entity, entityType = 'municipality') {
        try {
            const response = await fetch(
                `${this.apiBaseUrl}/analytics/benchmark/${entity}?entity_type=${entityType}`
            );

            if (!response.ok) {
                throw new Error(`Benchmark generation failed: ${response.statusText}`);
            }

            const result = await response.json();
            this.currentData.benchmark = result;
            return result;
        } catch (error) {
            console.error('Benchmark generation failed:', error);
            throw error;
        }
    }

    /**
     * Generate correlation matrix
     */
    async generateCorrelationMatrix(entities, entityType = 'municipality') {
        try {
            const response = await fetch(`${this.apiBaseUrl}/analytics/correlation`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    entities: entities,
                    entity_type: entityType
                })
            });

            if (!response.ok) {
                throw new Error(`Correlation matrix failed: ${response.statusText}`);
            }

            const result = await response.json();
            this.currentData.correlationMatrix = result;
            return result;
        } catch (error) {
            console.error('Correlation matrix generation failed:', error);
            throw error;
        }
    }

    /**
     * Export data mining results
     */
    async exportResults(queryParams, format = 'json') {
        try {
            const response = await fetch(`${this.apiBaseUrl}/data-mining/export`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: queryParams,
                    format: format
                })
            });

            if (!response.ok) {
                throw new Error(`Export failed: ${response.statusText}`);
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `atroz-export-${Date.now()}.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Export failed:', error);
            throw error;
        }
    }

    /**
     * Create comparative analysis visualization
     */
    createComparativeChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        // Destroy existing chart
        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }

        const metrics = Object.keys(data.metrics_comparison);
        const valuesA = metrics.map(m => data.metrics_comparison[m].entity_a);
        const valuesB = metrics.map(m => data.metrics_comparison[m].entity_b);

        this.charts[containerId] = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: metrics,
                datasets: [
                    {
                        label: data.entity_a,
                        data: valuesA,
                        borderColor: 'rgba(196, 30, 58, 1)',
                        backgroundColor: 'rgba(196, 30, 58, 0.2)',
                        pointBackgroundColor: 'rgba(196, 30, 58, 1)',
                    },
                    {
                        label: data.entity_b,
                        data: valuesB,
                        borderColor: 'rgba(0, 212, 255, 1)',
                        backgroundColor: 'rgba(0, 212, 255, 0.2)',
                        pointBackgroundColor: 'rgba(0, 212, 255, 1)',
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { color: '#E5E7EB', backdropColor: 'transparent' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        pointLabels: { color: '#E5E7EB', font: { size: 11 } }
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: '#E5E7EB', font: { size: 12 } }
                    }
                }
            }
        });
    }

    /**
     * Create trend visualization with forecast
     */
    createTrendChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        // Destroy existing chart
        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }

        const historicalLabels = data.data_points.map(dp => new Date(dp[0]).toLocaleDateString());
        const historicalValues = data.data_points.map(dp => dp[1]);

        const forecastLabels = data.forecast ?
            data.forecast.map(dp => new Date(dp[0]).toLocaleDateString()) : [];
        const forecastValues = data.forecast ?
            data.forecast.map(dp => dp[1]) : [];

        this.charts[containerId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [...historicalLabels, ...forecastLabels],
                datasets: [
                    {
                        label: 'Historical Data',
                        data: [...historicalValues, ...Array(forecastLabels.length).fill(null)],
                        borderColor: 'rgba(196, 30, 58, 1)',
                        backgroundColor: 'rgba(196, 30, 58, 0.1)',
                        borderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        fill: true
                    },
                    {
                        label: 'Forecast',
                        data: [...Array(historicalLabels.length).fill(null), ...forecastValues],
                        borderColor: 'rgba(0, 212, 255, 1)',
                        backgroundColor: 'rgba(0, 212, 255, 0.1)',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { color: '#E5E7EB' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    x: {
                        ticks: { color: '#E5E7EB', maxRotation: 45, minRotation: 45 },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' }
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: '#E5E7EB', font: { size: 12 } }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(10, 10, 10, 0.9)',
                        titleColor: '#E5E7EB',
                        bodyColor: '#E5E7EB',
                        borderColor: 'rgba(196, 30, 58, 0.5)',
                        borderWidth: 1
                    }
                }
            }
        });
    }

    /**
     * Create correlation heatmap
     */
    createCorrelationHeatmap(containerId, correlationMatrix) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        // Create heatmap HTML
        const policyAreas = Object.keys(correlationMatrix);
        let html = '<div class="correlation-heatmap">';
        html += '<table class="heatmap-table">';

        // Header row
        html += '<tr><th></th>';
        policyAreas.forEach(pa => {
            html += `<th>${pa}</th>`;
        });
        html += '</tr>';

        // Data rows
        policyAreas.forEach(pa1 => {
            html += `<tr><th>${pa1}</th>`;
            policyAreas.forEach(pa2 => {
                const value = correlationMatrix[pa1][pa2];
                const intensity = Math.abs(value);
                const color = value >= 0 ?
                    `rgba(0, 212, 255, ${intensity})` :
                    `rgba(196, 30, 58, ${intensity})`;
                html += `<td style="background-color: ${color}; color: white;" title="${value.toFixed(3)}">${value.toFixed(2)}</td>`;
            });
            html += '</tr>';
        });

        html += '</table></div>';
        container.innerHTML = html;
    }

    /**
     * Create gap analysis visualization
     */
    createGapChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        // Destroy existing chart
        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }

        const milestones = data.improvement_path.map(step => `Q${step.quarter}`);
        const targetScores = data.improvement_path.map(step => step.target_score);

        this.charts[containerId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Current', ...milestones],
                datasets: [{
                    label: 'Improvement Path',
                    data: [data.current_score, ...targetScores],
                    borderColor: 'rgba(57, 255, 20, 1)',
                    backgroundColor: 'rgba(57, 255, 20, 0.1)',
                    borderWidth: 3,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    fill: true,
                    tension: 0.3
                }, {
                    label: 'Target',
                    data: Array(milestones.length + 1).fill(data.target_score),
                    borderColor: 'rgba(196, 30, 58, 1)',
                    borderWidth: 2,
                    borderDash: [10, 5],
                    pointRadius: 0,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { color: '#E5E7EB' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    x: {
                        ticks: { color: '#E5E7EB' },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' }
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: '#E5E7EB', font: { size: 12 } }
                    }
                }
            }
        });
    }

    /**
     * Create benchmark comparison visualization
     */
    createBenchmarkChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        // Destroy existing chart
        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }

        const comparison = data.benchmark_comparison;

        this.charts[containerId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Entity', 'National Avg', 'PDET Avg', 'Top Performer', 'Min Acceptable'],
                datasets: [{
                    label: 'Score',
                    data: [
                        comparison.entity_score,
                        comparison.national_average,
                        comparison.pdet_average,
                        comparison.top_performer,
                        comparison.minimum_acceptable
                    ],
                    backgroundColor: [
                        'rgba(196, 30, 58, 0.8)',
                        'rgba(178, 100, 46, 0.8)',
                        'rgba(23, 165, 137, 0.8)',
                        'rgba(57, 255, 20, 0.8)',
                        'rgba(147, 51, 234, 0.8)'
                    ],
                    borderColor: [
                        'rgba(196, 30, 58, 1)',
                        'rgba(178, 100, 46, 1)',
                        'rgba(23, 165, 137, 1)',
                        'rgba(57, 255, 20, 1)',
                        'rgba(147, 51, 234, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { color: '#E5E7EB' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    x: {
                        ticks: { color: '#E5E7EB' },
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    /**
     * Create statistics summary card
     */
    createStatsSummary(containerId, stats) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        const html = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Mean</div>
                    <div class="stat-value">${stats.mean?.toFixed(2) || 'N/A'}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Median</div>
                    <div class="stat-value">${stats.median?.toFixed(2) || 'N/A'}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Std Dev</div>
                    <div class="stat-value">${stats.std_dev?.toFixed(2) || 'N/A'}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Min</div>
                    <div class="stat-value">${stats.min?.toFixed(2) || 'N/A'}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Max</div>
                    <div class="stat-value">${stats.max?.toFixed(2) || 'N/A'}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">P95</div>
                    <div class="stat-value">${stats.p95?.toFixed(2) || 'N/A'}</div>
                </div>
            </div>
        `;

        container.innerHTML = html;
    }

    /**
     * Destroy all charts
     */
    destroyAllCharts() {
        Object.values(this.charts).forEach(chart => chart.destroy());
        this.charts = {};
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AtrozAnalytics;
}
