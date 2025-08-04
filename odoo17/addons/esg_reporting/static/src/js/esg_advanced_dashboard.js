/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, useState, onWillStart } from "@odoo/owl";

export class ESGAdvancedDashboard extends Component {
    setup() {
        this.orm = useService("orm");
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
            diversity: { male_count: 0, female_count: 0, other_count: 0, male_leaders: 0, female_leaders: 0, other_leaders: 0 },
            risk_assessment: {},
            targets: [],
            esg_scores: []
        };
    }

    async loadDashboardData() {
        this.state.loading = true;
        this.state.error = null;
        try {
            const data = await this.orm.call(
                'esg.analytics',
                'get_comprehensive_dashboard_data',
                [this.state.selectedPeriod, this.state.selectedCategory]
            );

            if (data && typeof data === 'object') {
                this.state.dashboardData = data;
            } else {
                console.warn('Invalid dashboard data received:', data);
                this.state.dashboardData = this.getDefaultDashboardData();
            }

            const predictions = await this.orm.call('esg.analytics', 'get_predictive_analytics', []);
            this.state.predictions = predictions || {};

            const alerts = await this.orm.call('esg.analytics', 'get_esg_alerts', []);
            this.state.alerts = alerts || [];

        } catch (error) {
            console.error("Error loading ESG dashboard data:", error);
            this.state.error = "Failed to load dashboard data. Please try refreshing the page.";
            this.state.dashboardData = this.getDefaultDashboardData();
            this.state.predictions = {};
            this.state.alerts = [];
        } finally {
            this.state.loading = false;
        }
    }

    initializeCharts() {
        setTimeout(() => {
            try {
                this.createESGScoreChart();
                this.createEmissionChart();
                this.createDiversityChart();
                this.createRiskHeatmap();
                this.createTargetProgressChart();
            } catch (error) {
                console.error('Error initializing charts:', error);
            }
        }, 100);
    }

    createESGScoreChart() {
        const ctx = document.getElementById('esg-score-chart');
        if (!ctx) return;
        if (this.state.charts.esgScore) this.state.charts.esgScore.destroy();

        const data = this.state.dashboardData?.esg_scores || [];
        const validData = data.filter(d => d && d.month && d.environmental !== undefined && d.social !== undefined && d.governance !== undefined && d.overall !== undefined);

        if (validData.length === 0) {
            console.warn('No valid ESG score data to display.');
            return;
        }

        this.state.charts.esgScore = new Chart(ctx, {
            type: 'line',
            data: {
                labels: validData.map(d => d.month),
                datasets: [
                    { label: 'Environmental', data: validData.map(d => d.environmental), borderColor: '#28a745', tension: 0.4 },
                    { label: 'Social', data: validData.map(d => d.social), borderColor: '#007bff', tension: 0.4 },
                    { label: 'Governance', data: validData.map(d => d.governance), borderColor: '#6f42c1', tension: 0.4 },
                    { label: 'Overall', data: validData.map(d => d.overall), borderColor: '#fd7e14', borderWidth: 3, tension: 0.4 }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, max: 100 } } }
        });
    }

    createEmissionChart() {
        const ctx = document.getElementById('emission-chart');
        if (!ctx) return;
        if (this.state.charts.emission) this.state.charts.emission.destroy();

        const data = this.state.dashboardData?.emissions || {};
        this.state.charts.emission = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Scope 1', 'Scope 2', 'Scope 3', 'Offset'],
                datasets: [{
                    data: [data.scope1 || 0, data.scope2 || 0, data.scope3 || 0, data.offset || 0],
                    backgroundColor: ['#dc3545', '#fd7e14', '#ffc107', '#28a745']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    createDiversityChart() {
        const ctx = document.getElementById('diversity-chart');
        if (!ctx) return;
        if (this.state.charts.diversity) this.state.charts.diversity.destroy();

        const data = this.state.dashboardData?.diversity || {};
        this.state.charts.diversity = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Male', 'Female', 'Other'],
                datasets: [
                    { label: 'Overall Workforce', data: [data.male_count || 0, data.female_count || 0, data.other_count || 0], backgroundColor: ['#007bff', '#e83e8c', '#6c757d'] },
                    { label: 'Leadership', data: [data.male_leaders || 0, data.female_leaders || 0, data.other_leaders || 0], backgroundColor: ['#0056b3', '#c73e6b', '#545b62'] }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
        });
    }

    createRiskHeatmap() {
        const ctx = document.getElementById('risk-heatmap');
        if (!ctx) return;
        if (this.state.charts.riskHeatmap) this.state.charts.riskHeatmap.destroy();

        const data = this.state.dashboardData?.risk_assessment || {};
        const categories = ['Environmental', 'Social', 'Governance'];
        const levels = ['High', 'Medium', 'Low'];
        const datasets = levels.map((level, i) => ({
            label: level,
            data: categories.map(cat => data[`${cat.toLowerCase()}_${level.toLowerCase()}`] || 0),
            backgroundColor: ['#dc3545', '#ffc107', '#28a745'][i]
        }));

        this.state.charts.riskHeatmap = new Chart(ctx, {
            type: 'bar',
            data: { labels: categories, datasets },
            options: { responsive: true, maintainAspectRatio: false, scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } } }
        });
    }

    createTargetProgressChart() {
        const ctx = document.getElementById('target-progress-chart');
        if (!ctx) return;
        if (this.state.charts.targetProgress) this.state.charts.targetProgress.destroy();

        const data = this.state.dashboardData?.targets || [];
        const validData = data.filter(d => d && d.name && d.progress_percentage !== undefined);

        if (validData.length === 0) {
            console.warn('No valid target progress data to display.');
            return;
        }

        this.state.charts.targetProgress = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: validData.map(d => d.name),
                datasets: [{
                    label: 'Progress (%)',
                    data: validData.map(d => d.progress_percentage),
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.2)'
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { r: { beginAtZero: true, max: 100 } } }
        });
    }

    startRealTimeUpdates() {
        if (!this.state.realTimeUpdates) return;
        this.updateInterval = setInterval(async () => {
            await this.loadDashboardData();
            this.updateCharts();
        }, 30000);
    }

    updateCharts() {
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
            const reportAction = await this.orm.call(
                'esg.analytics',
                'generate_comprehensive_report',
                [this.state.selectedPeriod, this.state.selectedCategory]
            );
            if (reportAction) {
                this.env.services.action.doAction(reportAction);
            }
        } catch (error) {
            console.error("Error generating report:", error);
        }
    }

    async exportData() {
        try {
            const csvContent = await this.orm.call(
                'esg.analytics',
                'export_dashboard_data',
                [this.state.selectedPeriod, this.state.selectedCategory]
            );
            
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement("a");
            const url = URL.createObjectURL(blob);
            link.setAttribute("href", url);
            link.setAttribute("download", `esg_dashboard_${this.state.selectedPeriod}.csv`);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

        } catch (error) {
            console.error("Error exporting data:", error);
        }
    }
}

ESGAdvancedDashboard.template = "esg_reporting.ESGAdvancedDashboard";
ESGAdvancedDashboard.components = {};

registry.category("actions").add("esg_advanced_dashboard", ESGAdvancedDashboard);
