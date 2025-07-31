/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, useState } from "@odoo/owl";

export class ESGDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            dashboardData: null,
            loading: true,
            error: null
        });
        
        onMounted(() => {
            this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            this.state.loading = true;
            this.state.error = null;
            
            // Fetch analytics data for dashboard
            const analyticsData = await this.orm.searchRead(
                "esg.analytics",
                [["state", "=", "validated"]],
                ["total_emissions", "total_offsets", "net_emissions", "overall_score", "period_start", "period_end"],
                { limit: 1, order: "period_end desc" }
            );
            
            // Fetch recent initiatives
            const initiatives = await this.orm.searchRead(
                "esg.initiative",
                [["state", "in", ["draft", "in_progress"]]],
                ["name", "category", "progress", "budget", "impact_score"],
                { limit: 5, order: "create_date desc" }
            );
            
            // Fetch gender parity data
            const genderData = await this.orm.searchRead(
                "esg.gender.parity",
                [["state", "=", "validated"]],
                ["male_count", "female_count", "other_count", "diversity_score", "leadership_ratio"],
                { limit: 1, order: "create_date desc" }
            );
            
            // Fetch pay gap data
            const payGapData = await this.orm.searchRead(
                "esg.pay.gap",
                [["state", "=", "validated"]],
                ["mean_pay_gap", "median_pay_gap", "leadership_pay_gap", "pay_gap_category"],
                { limit: 1, order: "create_date desc" }
            );
            
            this.state.dashboardData = {
                analytics: analyticsData[0] || {},
                initiatives: initiatives,
                genderParity: genderData[0] || {},
                payGap: payGapData[0] || {}
            };
            
        } catch (error) {
            console.error("Error loading ESG dashboard data:", error);
            this.state.error = "Failed to load dashboard data";
        } finally {
            this.state.loading = false;
        }
    }

    getESGScoreColor(score) {
        if (score >= 80) return "text-success";
        if (score >= 60) return "text-warning";
        return "text-danger";
    }

    getPayGapCategoryColor(category) {
        switch (category) {
            case "excellent": return "text-success";
            case "good": return "text-info";
            case "fair": return "text-warning";
            case "poor": return "text-danger";
            default: return "text-muted";
        }
    }
}

ESGDashboard.template = "esg_dashboard";
ESGDashboard.components = {};

// Register the component
registry.category("actions").add("esg_dashboard", ESGDashboard);