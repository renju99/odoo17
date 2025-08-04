/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, onMounted } from "@odoo/owl";

class FacilitiesDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        onWillStart(async () => {
            try {
                await this.loadDashboardData();
            } catch (error) {
                console.error("Error in setup:", error);
            }
        });

        onMounted(() => {
            // Ensure layout is not forced before page is fully loaded
            this._ensureLayoutReady();
        });
    }

    async loadDashboardData() {
        try {
            const data = await this.orm.call(
                "facilities.space.booking",
                "get_dashboard_data",
                []
            );
            this.dashboardData = data;
        } catch (error) {
            console.error("Error loading dashboard data:", error);
            this.notification.add(
                "Error loading dashboard data",
                { type: "danger" }
            );
            // Provide fallback data
            this.dashboardData = {
                total_bookings: 0,
                today_bookings: 0,
                week_bookings: 0,
                month_bookings: 0,
                status_breakdown: {
                    confirmed: 0,
                    pending: 0,
                    completed: 0,
                    cancelled: 0
                },
                booking_types: [],
                room_utilization: [],
                recent_bookings: [],
                current_time: new Date().toLocaleString()
            };
        }
    }

    _ensureLayoutReady() {
        // Wait for DOM to be fully ready before any layout operations
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this._performLayoutOperations();
            });
        } else {
            this._performLayoutOperations();
        }
    }

    _performLayoutOperations() {
        // Any layout operations should go here
        // This ensures they happen after the page is fully loaded
        console.log("Facilities dashboard layout ready");
    }
}

FacilitiesDashboard.template = "facilities_management.Dashboard";
FacilitiesDashboard.components = { Layout };

registry.category("actions").add("facilities_dashboard", FacilitiesDashboard);

// Basic utility functions
window.facilitiesUtils = {
    formatCurrency: function(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },

    formatDate: function(date) {
        return new Date(date).toLocaleDateString();
    },

    getSLAStatusClass: function(status) {
        const statusClasses = {
            'on_time': 'o_sla_on_time',
            'warning': 'o_sla_warning',
            'critical': 'o_sla_critical',
            'breached': 'o_sla_breached'
        };
        return statusClasses[status] || 'o_sla_on_time';
    }
};

console.log("Facilities Management JavaScript loaded");