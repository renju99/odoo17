/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, useState, onWillStart } from "@odoo/owl";

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

    // New helper function to sanitize chart data
    _sanitizeChartData(data) {
        const sanitizedData = { ...data };

        // Sanitize ESG Scores (Array of objects)
        sanitizedData.esg_scores = Array.isArray(sanitizedData.esg_scores) ? sanitizedData.esg_scores : [];

        // Sanitize Emissions (Object)
        sanitizedData.emissions = (sanitizedData.emissions && typeof sanitizedData.emissions === 'object') ? sanitizedData.emissions : {};

        // Sanitize Diversity (Object)
        sanitizedData.diversity = (sanitizedData.diversity && typeof sanitizedData.diversity === 'object') ? sanitizedData.diversity : {};

        // Sanitize Risk Assessment (Object)
        sanitizedData.risk_assessment = (sanitizedData.risk_assessment && typeof sanitizedData.risk_assessment === 'object') ? sanitizedData.risk_assessment : {};

        // Sanitize Targets (Array of objects)
        sanitizedData.targets = Array.isArray(sanitizedData.targets) ? sanitizedData.targets : [];

        return sanitizedData;
    }

    async loadDashboardData() {
        try {
            this.state.loading = true;
            this.state.error = null;

            const data = await this.orm.call(
                'esg.analytics',
                'get_comprehensive_dashboard_data',
                [this.state.selectedPeriod, this.state.selectedCategory]
            );
<<<<<<< HEAD

            // Sanitize the data before setting it to the state
            this.state.dashboardData = this._sanitizeChartData(data);

            const predictions = await this.orm.call(
                'esg.analytics',
                'get_predictive_analytics',
                []
            );
            this.state.predictions = predictions;

            const alerts = await this.orm.call(
                'esg.analytics',
                'get_esg_alerts',
                []
            );
            this.state.alerts = alerts;

=======
            
            if (data && typeof data === 'object') {
                this.state.dashboardData = data;
            } else {
                console.warn('Invalid dashboard data received:', data);
                this.state.dashboardData = this.getDefaultDashboardData();
            }
            
            // Load predictions
            try {
                const predictions = await this.orm.call(
                    'esg.analytics',
                    'get_predictive_analytics',
                    []
                );
                this.state.predictions = predictions || {};
            } catch (predictionError) {
                console.warn('Failed to load predictions:', predictionError);
                this.state.predictions = {};
            }
            
            // Load alerts
            try {
                const alerts = await this.orm.call(
                    'esg.analytics',
                    'get_esg_alerts',
                    []
                );
                this.state.alerts = alerts || [];
            } catch (alertError) {
                console.warn('Failed to load alerts:', alertError);
                this.state.alerts = [];
            }
            
>>>>>>> 6aaba2893f1578b8d8ba86d87b9022127f133896
        } catch (error) {
            console.error("Error loading ESG dashboard data:", error);
            this.state.error = "Failed to load dashboard data. Please try refreshing the page.";
            this.state.dashboardData = this.getDefaultDashboardData();
        } finally {
            this.state.loading = false;
        }
    }

<<<<<<< HEAD
    initializeCharts() {
        this.createESGScoreChart();
        this.createEmissionChart();
        this.createDiversityChart();
        this.createRiskHeatmap();
        this.createTargetProgressChart();
=======
    getDefaultDashboardData() {
        return {
            period: this.state.selectedPeriod,
            category: this.state.selectedCategory,
            date_range: {
                from: new Date().toISOString().split('T')[0],
                to: new Date().toISOString().split('T')[0]
            },
            overall_score: 0,
            carbon_reduction: 0,
            diversity_score: 0,
            target_progress: 0,
            emissions: { scope1: 0, scope2: 0, scope3: 0, offset: 0 },
            diversity: { male_count: 0, female_count: 0, other_count: 0 },
            risk_assessment: {},
            targets: [],
            esg_scores: []
        };
    }

    async initializeCharts() {
        // Wait a bit for the DOM to be ready
        setTimeout(() => {
            try {
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
            } catch (error) {
                console.error('Error initializing charts:', error);
            }
        }, 100);
>>>>>>> 6aaba2893f1578b8d8ba86d87b9022127f133896
    }

    createESGScoreChart() {
        const ctx = document.getElementById('esg-score-chart');
<<<<<<< HEAD
        if (!ctx) return;

        const data = this.state.dashboardData.esg_scores; // Already sanitized

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
                    title: { display: true, text: 'ESG Performance Trends' },
                    legend: { position: 'top' }
                },
                scales: { y: { beginAtZero: true, max: 100 } }
            }
        });
=======
        if (!ctx) {
            console.warn('ESG score chart canvas not found');
            return;
        }
        
        // Destroy existing chart if it exists
        if (this.state.charts.esgScore) {
            this.state.charts.esgScore.destroy();
        }
        
        const data = this.state.dashboardData?.esg_scores || [];
        
        // Validate data before creating chart
        if (!data || data.length === 0) {
            console.warn('ESG score data is empty or undefined');
            return;
        }
        
        // Ensure all data points have valid values
        const validData = data.filter(d => 
            d && 
            typeof d.month !== 'undefined' && 
            typeof d.environmental !== 'undefined' && 
            typeof d.social !== 'undefined' && 
            typeof d.governance !== 'undefined' && 
            typeof d.overall !== 'undefined'
        );
        
        if (validData.length === 0) {
            console.warn('No valid ESG score data points found');
            return;
        }
        
        try {
            this.state.charts.esgScore = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: validData.map(d => d.month),
                    datasets: [{
                        label: 'Environmental Score',
                        data: validData.map(d => d.environmental),
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Social Score',
                        data: validData.map(d => d.social),
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Governance Score',
                        data: validData.map(d => d.governance),
                        borderColor: '#6f42c1',
                        backgroundColor: 'rgba(111, 66, 193, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Overall Score',
                        data: validData.map(d => d.overall),
                        borderColor: '#fd7e14',
                        backgroundColor: 'rgba(253, 126, 20, 0.1)',
                        tension: 0.4,
                        borderWidth: 3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
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
        } catch (error) {
            console.error('Error creating ESG score chart:', error);
        }
>>>>>>> 6aaba2893f1578b8d8ba86d87b9022127f133896
    }

    createEmissionChart() {
        const ctx = document.getElementById('emission-chart');
<<<<<<< HEAD
        if (!ctx) return;

        const data = this.state.dashboardData.emissions; // Already sanitized

        this.state.charts.emission = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Scope 1', 'Scope 2', 'Scope 3', 'Offset'],
                datasets: [{
                    data: [data.scope1 || 0, data.scope2 || 0, data.scope3 || 0, data.offset || 0],
                    backgroundColor: ['#dc3545', '#fd7e14', '#ffc107', '#28a745']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: { display: true, text: 'Carbon Footprint Breakdown' },
                    legend: { position: 'bottom' }
=======
        if (!ctx) {
            console.warn('Emission chart canvas not found');
            return;
        }
        
        // Destroy existing chart if it exists
        if (this.state.charts.emission) {
            this.state.charts.emission.destroy();
        }
        
        const data = this.state.dashboardData?.emissions || {};
        
        // Validate data before creating chart
        if (!data || Object.keys(data).length === 0) {
            console.warn('Emission data is empty or undefined');
            return;
        }
        
        // Ensure all emission values are valid numbers
        const scope1 = typeof data.scope1 === 'number' ? data.scope1 : 0;
        const scope2 = typeof data.scope2 === 'number' ? data.scope2 : 0;
        const scope3 = typeof data.scope3 === 'number' ? data.scope3 : 0;
        const offset = typeof data.offset === 'number' ? data.offset : 0;
        
        try {
            this.state.charts.emission = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Scope 1', 'Scope 2', 'Scope 3', 'Offset'],
                    datasets: [{
                        data: [scope1, scope2, scope3, offset],
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
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Carbon Footprint Breakdown'
                        },
                        legend: {
                            position: 'bottom'
                        }
                    }
>>>>>>> 6aaba2893f1578b8d8ba86d87b9022127f133896
                }
            });
        } catch (error) {
            console.error('Error creating emission chart:', error);
        }
    }

    createDiversityChart() {
        const ctx = document.getElementById('diversity-chart');
<<<<<<< HEAD
        if (!ctx) return;

        const data = this.state.dashboardData.diversity; // Already sanitized

        this.state.charts.diversity = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Male', 'Female', 'Other'],
                datasets: [{
                    label: 'Overall Workforce',
                    data: [data.male_count || 0, data.female_count || 0, data.other_count || 0],
                    backgroundColor: ['#007bff', '#e83e8c', '#6c757d']
                }, {
                    label: 'Leadership',
                    data: [data.male_leaders || 0, data.female_leaders || 0, data.other_leaders || 0],
                    backgroundColor: ['#0056b3', '#c73e6b', '#545b62']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: { display: true, text: 'Workforce Diversity Metrics' },
                    legend: { position: 'top' }
                },
                scales: { y: { beginAtZero: true } }
            }
        });
=======
        if (!ctx) {
            console.warn('Diversity chart canvas not found');
            return;
        }
        
        // Destroy existing chart if it exists
        if (this.state.charts.diversity) {
            this.state.charts.diversity.destroy();
        }
        
        const data = this.state.dashboardData?.diversity || {};
        
        // Validate data before creating chart
        if (!data || Object.keys(data).length === 0) {
            console.warn('Diversity data is empty or undefined');
            return;
        }
        
        // Ensure all diversity values are valid numbers
        const maleCount = typeof data.male_count === 'number' ? data.male_count : 0;
        const femaleCount = typeof data.female_count === 'number' ? data.female_count : 0;
        const otherCount = typeof data.other_count === 'number' ? data.other_count : 0;
        const maleLeaders = typeof data.male_leaders === 'number' ? data.male_leaders : 0;
        const femaleLeaders = typeof data.female_leaders === 'number' ? data.female_leaders : 0;
        const otherLeaders = typeof data.other_leaders === 'number' ? data.other_leaders : 0;
        
        try {
            this.state.charts.diversity = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Male', 'Female', 'Other'],
                    datasets: [{
                        label: 'Overall Workforce',
                        data: [maleCount, femaleCount, otherCount],
                        backgroundColor: [
                            '#007bff',
                            '#e83e8c',
                            '#6c757d'
                        ]
                    }, {
                        label: 'Leadership',
                        data: [maleLeaders, femaleLeaders, otherLeaders],
                        backgroundColor: [
                            '#0056b3',
                            '#c73e6b',
                            '#545b62'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Workforce Diversity Metrics'
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
        } catch (error) {
            console.error('Error creating diversity chart:', error);
        }
>>>>>>> 6aaba2893f1578b8d8ba86d87b9022127f133896
    }

    createRiskHeatmap() {
        const ctx = document.getElementById('risk-heatmap');
<<<<<<< HEAD
        if (!ctx) return;

        const data = this.state.dashboardData.risk_assessment; // Already sanitized
=======
        if (!ctx) {
            console.warn('Risk heatmap canvas not found');
            return;
        }
        
        // Destroy existing chart if it exists
        if (this.state.charts.riskHeatmap) {
            this.state.charts.riskHeatmap.destroy();
        }
        
        const data = this.state.dashboardData?.risk_assessment || {};
        
        // Validate data before creating chart
        if (!data || Object.keys(data).length === 0) {
            console.warn('Risk assessment data is empty or undefined');
            return;
        }
        
        // Prepare data for bar chart heatmap
>>>>>>> 6aaba2893f1578b8d8ba86d87b9022127f133896
        const categories = ['Environmental', 'Social', 'Governance'];
        const levels = ['High', 'Medium', 'Low'];

        const datasets = levels.map((level, levelIndex) => ({
            label: level,
            data: categories.map(category => {
                const key = `${category.toLowerCase()}_${level.toLowerCase()}`;
                return data[key] || 0;
            }),
            backgroundColor: (context) => {
                const value = context.raw;
                const alpha = Math.min(value / 100, 1);
                const colors = ['#dc3545', '#ffc107', '#28a745'];
                return `rgba(${colors[levelIndex]}, ${alpha})`;
            },
            borderColor: (context) => {
                const colors = ['#dc3545', '#ffc107', '#28a745'];
                return colors[levelIndex];
            },
            borderWidth: 1
        }));
<<<<<<< HEAD

        this.state.charts.riskHeatmap = new Chart(ctx, {
            type: 'bar',
            data: { labels: categories, datasets: datasets },
            options: {
                responsive: true,
                plugins: {
                    title: { display: true, text: 'ESG Risk Assessment Heatmap' },
                    legend: { display: true, position: 'top' }
                },
                scales: {
                    x: { title: { display: true, text: 'ESG Categories' } },
                    y: { title: { display: true, text: 'Risk Level (%)' }, beginAtZero: true, max: 100 }
=======
        
        try {
            this.state.charts.riskHeatmap = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: categories,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
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
>>>>>>> 6aaba2893f1578b8d8ba86d87b9022127f133896
                }
            });
        } catch (error) {
            console.error('Error creating risk heatmap:', error);
        }
    }

    createTargetProgressChart() {
        const ctx = document.getElementById('target-progress-chart');
<<<<<<< HEAD
        if (!ctx) return;

        const data = this.state.dashboardData.targets; // Already sanitized

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
                    title: { display: true, text: 'ESG Target Progress' },
                    legend: { position: 'top' }
                },
                scales: { r: { beginAtZero: true, max: 100, ticks: { stepSize: 20 } } }
            }
        });
=======
        if (!ctx) {
            console.warn('Target progress chart canvas not found');
            return;
        }
        
        // Destroy existing chart if it exists
        if (this.state.charts.targetProgress) {
            this.state.charts.targetProgress.destroy();
        }
        
        const data = this.state.dashboardData?.targets || [];
        
        // Validate data before creating chart
        if (!data || data.length === 0) {
            console.warn('Target progress data is empty or undefined');
            return;
        }
        
        // Ensure all data points have valid values
        const validData = data.filter(d => 
            d && 
            typeof d.name !== 'undefined' && 
            typeof d.progress_percentage !== 'undefined'
        );
        
        if (validData.length === 0) {
            console.warn('No valid target progress data points found');
            return;
        }
        
        try {
            this.state.charts.targetProgress = new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: validData.map(d => d.name),
                    datasets: [{
                        label: 'Progress (%)',
                        data: validData.map(d => d.progress_percentage),
                        backgroundColor: 'rgba(40, 167, 69, 0.2)',
                        borderColor: '#28a745',
                        pointBackgroundColor: '#28a745'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'ESG Target Progress'
                        },
                        legend: {
                            position: 'top'
                        }
                    },
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                stepSize: 20
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error creating target progress chart:', error);
        }
>>>>>>> 6aaba2893f1578b8d8ba86d87b9022127f133896
    }

    startRealTimeUpdates() {
        if (!this.state.realTimeUpdates) return;
<<<<<<< HEAD
        setInterval(async () => {
=======
        
        // Update data every 30 seconds
        this.updateInterval = setInterval(async () => {
>>>>>>> 6aaba2893f1578b8d8ba86d87b9022127f133896
            await this.loadDashboardData();
            this.updateCharts();
        }, 30000);
    }

    updateCharts() {
        Object.values(this.state.charts).forEach(chart => {
<<<<<<< HEAD
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
=======
            if (chart && typeof chart.update === 'function') {
                try {
                    chart.update();
                } catch (error) {
                    console.warn('Error updating chart:', error);
                }
>>>>>>> 6aaba2893f1578b8d8ba86d87b9022127f133896
            }
        });
        this.state.charts = {};
        this.initializeCharts();
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
        } else if (this.updateInterval) {
            clearInterval(this.updateInterval);
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
<<<<<<< HEAD
=======
        // Convert data to CSV format
        if (!data || data.length === 0) {
            return '';
        }
        
>>>>>>> 6aaba2893f1578b8d8ba86d87b9022127f133896
        const headers = Object.keys(data[0] || {});
        const csvRows = [headers.join(',')];
        
        for (const row of data) {
            const values = headers.map(header => row[header]);
            csvRows.push(values.join('\n'));
        }
        
        return csvRows.join('\n');
    }
}

ESGAdvancedDashboard.template = "esg_advanced_dashboard";
ESGAdvancedDashboard.components = {};

registry.category("actions").add("esg_advanced_dashboard", ESGAdvancedDashboard);
