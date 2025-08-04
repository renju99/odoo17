/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, useState, onWillStart } from "@odoo/owl";
// Chart.js is loaded globally

export class ESGAdvancedDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.rpc = useService("rpc");
        this.state = useState({
            dashboardData: null,
            loading: true,
            error: null,
            selectedPeriod: 'current_year',
            selectedCategory: 'all',
            realTimeUpdates: true,
            charts: {},
            predictions: {},
            alerts: []
        });
        
        onWillStart(async () => {
            await this.loadDashboardData();
        });
        
        onMounted(() => {
            this.initializeCharts();
            this.startRealTimeUpdates();
        });
    }

    async loadDashboardData() {
        try {
            this.state.loading = true;
            this.state.error = null;
            
            // Load comprehensive ESG data
            const data = await this.orm.call(
                'esg.analytics',
                'get_comprehensive_dashboard_data',
                [this.state.selectedPeriod, this.state.selectedCategory]
            );
            
            this.state.dashboardData = data;
            
            // Load predictions
            const predictions = await this.orm.call(
                'esg.analytics',
                'get_predictive_analytics',
                []
            );
            this.state.predictions = predictions;
            
            // Load alerts
            const alerts = await this.orm.call(
                'esg.analytics',
                'get_esg_alerts',
                []
            );
            this.state.alerts = alerts;
            
        } catch (error) {
            console.error("Error loading ESG dashboard data:", error);
            this.state.error = "Failed to load dashboard data";
        } finally {
            this.state.loading = false;
        }
    }

    async initializeCharts() {
        // ESG Score Trend Chart
        this.createESGScoreChart();
        
        // Emission Reduction Chart
        this.createEmissionChart();
        
        // Diversity Metrics Chart
        this.createDiversityChart();
        
        // Risk Assessment Heatmap
        this.createRiskHeatmap();
        
        // Target Progress Chart
        this.createTargetProgressChart();
    }

    createESGScoreChart() {
        const ctx = document.getElementById('esg-score-chart');
        if (!ctx) return;
        
        const data = this.state.dashboardData?.esg_scores || [];
        
        this.state.charts.esgScore = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.month),
                datasets: [{
                    label: 'Environmental Score',
                    data: data.map(d => d.environmental),
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Social Score',
                    data: data.map(d => d.social),
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Governance Score',
                    data: data.map(d => d.governance),
                    borderColor: '#6f42c1',
                    backgroundColor: 'rgba(111, 66, 193, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Overall Score',
                    data: data.map(d => d.overall),
                    borderColor: '#fd7e14',
                    backgroundColor: 'rgba(253, 126, 20, 0.1)',
                    tension: 0.4,
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'ESG Performance Trends'
                    },
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    createEmissionChart() {
        const ctx = document.getElementById('emission-chart');
        if (!ctx) return;
        
        const data = this.state.dashboardData?.emissions || {};
        
        this.state.charts.emission = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Scope 1', 'Scope 2', 'Scope 3', 'Offset'],
                datasets: [{
                    data: [
                        data.scope1 || 0,
                        data.scope2 || 0,
                        data.scope3 || 0,
                        data.offset || 0
                    ],
                    backgroundColor: [
                        '#dc3545',
                        '#fd7e14',
                        '#ffc107',
                        '#28a745'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Carbon Footprint Breakdown'
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    createDiversityChart() {
        const ctx = document.getElementById('diversity-chart');
        if (!ctx) return;
        
        const data = this.state.dashboardData?.diversity || {};
        
        this.state.charts.diversity = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Male', 'Female', 'Other'],
                datasets: [{
                    label: 'Overall Workforce',
                    data: [
                        data.male_count || 0,
                        data.female_count || 0,
                        data.other_count || 0
                    ],
                    backgroundColor: [
                        '#007bff',
                        '#e83e8c',
                        '#6c757d'
                    ]
                }, {
                    label: 'Leadership',
                    data: [
                        data.male_leaders || 0,
                        data.female_leaders || 0,
                        data.other_leaders || 0
                    ],
                    backgroundColor: [
                        '#0056b3',
                        '#c73e6b',
                        '#545b62'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Workforce Diversity'
                    },
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    createRiskHeatmap() {
        const ctx = document.getElementById('risk-heatmap');
        if (!ctx) return;
        
        const data = this.state.dashboardData?.risk_assessment || {};
        
        // Prepare data for bar chart heatmap
        const categories = ['Environmental', 'Social', 'Governance'];
        const levels = ['High', 'Medium', 'Low'];
        const datasets = levels.map((level, levelIndex) => ({
            label: level,
            data: categories.map(category => {
                const key = `${category.toLowerCase()}_${level.toLowerCase()}`;
                return data[key] || 0;
            }),
            backgroundColor: function(context) {
                const value = context.raw;
                const alpha = Math.min(value / 100, 1);
                const colors = ['#dc3545', '#ffc107', '#28a745']; // Red, Yellow, Green
                const color = colors[levelIndex];
                return `rgba(${color}, ${alpha})`;
            },
            borderColor: function(context) {
                const colors = ['#dc3545', '#ffc107', '#28a745']; // Red, Yellow, Green
                return colors[levelIndex];
            },
            borderWidth: 1
        }));
        
        this.state.charts.riskHeatmap = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: categories,
                datasets: datasets
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'ESG Risk Assessment Heatmap'
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'ESG Categories'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Risk Level (%)'
                        },
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    createTargetProgressChart() {
        const ctx = document.getElementById('target-progress-chart');
        if (!ctx) return;
        
        const data = this.state.dashboardData?.targets || [];
        
        this.state.charts.targetProgress = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: data.map(d => d.name),
                datasets: [{
                    label: 'Progress (%)',
                    data: data.map(d => d.progress_percentage),
                    backgroundColor: 'rgba(40, 167, 69, 0.2)',
                    borderColor: '#28a745',
                    pointBackgroundColor: '#28a745'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Target Progress Overview'
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    startRealTimeUpdates() {
        if (!this.state.realTimeUpdates) return;
        
        // Update data every 30 seconds
        setInterval(async () => {
            await this.loadDashboardData();
            this.updateCharts();
        }, 30000);
    }

    updateCharts() {
        // Update all charts with new data
        Object.values(this.state.charts).forEach(chart => {
            if (chart && chart.update) {
                chart.update();
            }
        });
    }

    async onPeriodChange(period) {
        this.state.selectedPeriod = period;
        await this.loadDashboardData();
        this.updateCharts();
    }

    async onCategoryChange(category) {
        this.state.selectedCategory = category;
        await this.loadDashboardData();
        this.updateCharts();
    }

    toggleRealTimeUpdates() {
        this.state.realTimeUpdates = !this.state.realTimeUpdates;
        if (this.state.realTimeUpdates) {
            this.startRealTimeUpdates();
        }
    }

    getESGScoreColor(score) {
        if (score >= 80) return "text-success";
        if (score >= 60) return "text-warning";
        return "text-danger";
    }

    getRiskLevelColor(level) {
        switch (level) {
            case 'low': return 'text-success';
            case 'medium': return 'text-warning';
            case 'high': return 'text-danger';
            case 'critical': return 'text-danger font-weight-bold';
            default: return 'text-muted';
        }
    }

    getTargetStatusColor(status) {
        switch (status) {
            case 'on_track': return 'text-success';
            case 'at_risk': return 'text-warning';
            case 'off_track': return 'text-danger';
            default: return 'text-muted';
        }
    }

    async generateReport() {
        try {
            const reportData = await this.orm.call(
                'esg.analytics',
                'generate_comprehensive_report',
                [this.state.selectedPeriod, this.state.selectedCategory]
            );
            
            // Download or display report
            if (reportData.report_url) {
                window.open(reportData.report_url, '_blank');
            }
        } catch (error) {
            console.error("Error generating report:", error);
        }
    }

    async exportData() {
        try {
            const exportData = await this.orm.call(
                'esg.analytics',
                'export_dashboard_data',
                [this.state.selectedPeriod, this.state.selectedCategory]
            );
            
            // Create and download CSV
            const csvContent = this.convertToCSV(exportData);
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `esg_dashboard_${this.state.selectedPeriod}.csv`;
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error("Error exporting data:", error);
        }
    }

    convertToCSV(data) {
        // Convert data to CSV format
        const headers = Object.keys(data[0] || {});
        const csvRows = [headers.join(',')];
        
        for (const row of data) {
            const values = headers.map(header => row[header]);
            csvRows.push(values.join(','));
        }
        
        return csvRows.join('\n');
    }
}

ESGAdvancedDashboard.template = "esg_advanced_dashboard";
ESGAdvancedDashboard.components = {};

// Register the component
registry.category("actions").add("esg_advanced_dashboard", ESGAdvancedDashboard);