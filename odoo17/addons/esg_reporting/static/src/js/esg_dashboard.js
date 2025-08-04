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
            
            // Initialize default data structure
            const dashboardData = {
                analytics: {},
                initiatives: [],
                genderParity: {},
                payGap: {}
            };
            
            // Fetch analytics data for dashboard
            try {
                const analyticsData = await this.orm.searchRead(
                    "esg.analytics",
                    [["state", "=", "completed"]],
                    ["total_emissions", "total_offset", "net_emissions", "overall_score", "date_from", "date_to"],
                    { limit: 1, order: "date_to desc" }
                );
                
                if (analyticsData && analyticsData.length > 0) {
                    dashboardData.analytics = analyticsData[0];
                }
            } catch (analyticsError) {
                console.warn('Failed to load analytics data:', analyticsError);
                // Use default analytics data
                dashboardData.analytics = {
                    total_emissions: 0,
                    total_offset: 0,
                    net_emissions: 0,
                    overall_score: 0
                };
            }
            
            // Fetch recent initiatives
            try {
                const initiatives = await this.orm.searchRead(
                    "esg.initiative",
                    [["state", "in", ["draft", "in_progress"]]],
                    ["name", "category", "progress", "budget", "impact_score"],
                    { limit: 5, order: "create_date desc" }
                );
                
                if (initiatives && Array.isArray(initiatives)) {
                    dashboardData.initiatives = initiatives;
                }
            } catch (initiativeError) {
                console.warn('Failed to load initiatives data:', initiativeError);
                dashboardData.initiatives = [];
            }
            
            // Fetch gender parity data
            try {
                const genderData = await this.orm.searchRead(
                    "esg.gender.parity",
                    [["state", "=", "completed"]],
                    ["male_count", "female_count", "other_count", "diversity_score", "leadership_ratio"],
                    { limit: 1, order: "create_date desc" }
                );
                
                if (genderData && genderData.length > 0) {
                    dashboardData.genderParity = genderData[0];
                }
            } catch (genderError) {
                console.warn('Failed to load gender parity data:', genderError);
                // Use default gender parity data
                dashboardData.genderParity = {
                    male_count: 0,
                    female_count: 0,
                    other_count: 0,
                    diversity_score: 0,
                    leadership_ratio: 0
                };
            }
            
            // Fetch pay gap data
            try {
                const payGapData = await this.orm.searchRead(
                    "esg.pay.gap",
                    [["state", "=", "completed"]],
                    ["mean_pay_gap", "median_pay_gap", "leadership_pay_gap", "pay_gap_category"],
                    { limit: 1, order: "create_date desc" }
                );
                
                if (payGapData && payGapData.length > 0) {
                    dashboardData.payGap = payGapData[0];
                }
            } catch (payGapError) {
                console.warn('Failed to load pay gap data:', payGapError);
                // Use default pay gap data
                dashboardData.payGap = {
                    mean_pay_gap: 0,
                    median_pay_gap: 0,
                    leadership_pay_gap: 0,
                    pay_gap_category: 'excellent'
                };
            }
            
            this.state.dashboardData = dashboardData;
            
        } catch (error) {
            console.error("Error loading ESG dashboard data:", error);
            this.state.error = "Failed to load dashboard data. Please try refreshing the page.";
            
            // Set default data structure
            this.state.dashboardData = {
                analytics: {
                    total_emissions: 0,
                    total_offset: 0,
                    net_emissions: 0,
                    overall_score: 0
                },
                initiatives: [],
                genderParity: {
                    male_count: 0,
                    female_count: 0,
                    other_count: 0,
                    diversity_score: 0,
                    leadership_ratio: 0
                },
                payGap: {
                    mean_pay_gap: 0,
                    median_pay_gap: 0,
                    leadership_pay_gap: 0,
                    pay_gap_category: 'excellent'
                }
            };
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