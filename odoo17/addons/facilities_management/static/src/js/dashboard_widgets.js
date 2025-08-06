/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, onMounted } from "@odoo/owl";

class FacilitiesDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.isLayoutReady = false;
        
        onWillStart(async () => {
            try {
                await this.loadDashboardData();
            } catch (error) {
                console.error("Error in setup:", error);
            }
        });

        onMounted(() => {
            // Use multiple strategies to ensure proper timing
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
        // Strategy 1: Check if document is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this._waitForStylesheets();
            });
        } else {
            this._waitForStylesheets();
        }
    }

    _waitForStylesheets() {
        // Strategy 2: Wait for stylesheets to load
        const stylesheets = Array.from(document.styleSheets);
        const unloadedStylesheets = stylesheets.filter(sheet => {
            try {
                return sheet.href && !sheet.href.startsWith('data:') && sheet.cssRules.length === 0;
            } catch (e) {
                return false;
            }
        });

        if (unloadedStylesheets.length === 0) {
            // All stylesheets loaded, proceed
            this._performLayoutOperations();
        } else {
            // Wait for remaining stylesheets
            let loadedCount = 0;
            const totalStylesheets = unloadedStylesheets.length;
            
            unloadedStylesheets.forEach(sheet => {
                const link = document.querySelector(`link[href="${sheet.href}"]`);
                if (link) {
                    link.addEventListener('load', () => {
                        loadedCount++;
                        if (loadedCount === totalStylesheets) {
                            this._performLayoutOperations();
                        }
                    });
                }
            });
            
            // Fallback: proceed after a reasonable timeout
            setTimeout(() => {
                if (!this.isLayoutReady) {
                    this._performLayoutOperations();
                }
            }, 2000);
        }
    }

    _performLayoutOperations() {
        // Prevent multiple executions
        if (this.isLayoutReady) {
            return;
        }
        
        // Ensure element exists before performing operations
        if (!this.el) {
            console.warn('Dashboard element not found, retrying...');
            setTimeout(() => {
                this._performLayoutOperations();
            }, 100);
            return;
        }
        
        console.log("Facilities dashboard layout ready");
        
        // Use requestAnimationFrame for final layout operations
        requestAnimationFrame(() => {
            // Add loaded class to show the dashboard
            this.el.classList.add('loaded');
            
            // Mark as ready
            this.isLayoutReady = true;
            
            // Trigger any necessary layout updates
            if (this.el.offsetHeight) {
                // Force a reflow to ensure proper layout
                this.el.offsetHeight;
            }
            
            console.log("Facilities Management JavaScript loaded");
        });
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