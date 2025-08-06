/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

/**
 * IoT Monitoring Dashboard Widget
 */
export class IoTMonitoringWidget extends Component {
    static template = "facilities_management.IoTMonitoringWidget";
    
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.notification = useService("notification");
        this.bus = useService("bus_service");
        
        this.state = useState({
            sensors: [],
            alerts: [],
            filters: {
                status: 'all',
                sensor_type: 'all',
                asset_id: false
            },
            connectionStatus: 'connected'
        });
        
        this.refreshInterval = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        
        onWillStart(async () => {
            await this._loadSensorData();
            this._setupBusListeners();
        });
        
        onMounted(() => {
            this._startAutoRefresh();
        });
        
        onWillUnmount(() => {
            if (this.refreshInterval) {
                clearInterval(this.refreshInterval);
            }
            this._removeBusListeners();
        });
    }

    _setupBusListeners() {
        // Listen for real-time sensor updates
        this.bus.addEventListener('notification', (ev) => {
            const notifications = ev.detail;
            for (const notif of notifications) {
                if (notif.type === 'sensor_update') {
                    this._handleSensorUpdate(notif.payload);
                } else if (notif.type === 'sensor_alert') {
                    this._handleSensorAlert(notif.payload);
                }
            }
        });

        // Listen for connection status changes
        this.bus.addEventListener('connect', () => {
            this.state.connectionStatus = 'connected';
            this.reconnectAttempts = 0;
            this.notification.add(_t('Connection restored'), { type: 'success' });
        });

        this.bus.addEventListener('disconnect', () => {
            this.state.connectionStatus = 'disconnected';
            this._handleDisconnection();
        });

        this.bus.addEventListener('reconnecting', () => {
            this.state.connectionStatus = 'reconnecting';
        });
    }

    _removeBusListeners() {
        // Bus service handles cleanup automatically in Odoo 17
        // No manual cleanup needed
    }

    _handleSensorUpdate(data) {
        const sensorIndex = this.state.sensors.findIndex(s => s.id === data.sensor_id);
        if (sensorIndex !== -1) {
            this.state.sensors[sensorIndex] = {
                ...this.state.sensors[sensorIndex],
                current_value: data.current_value,
                status: data.status,
                last_reading_time: data.timestamp
            };
        }
    }

    _handleSensorAlert(data) {
        // Add or update alert in the alerts list
        const alertIndex = this.state.alerts.findIndex(a => a.id === data.sensor_id);
        const alertData = {
            id: data.sensor_id,
            name: data.sensor_name,
            sensor_type: data.sensor_type || 'unknown',
            current_value: data.current_value,
            unit: data.unit,
            status: data.status,
            asset_id: [data.asset_id, data.asset_name],
            last_alert_time: data.timestamp
        };

        if (alertIndex !== -1) {
            this.state.alerts[alertIndex] = alertData;
        } else {
            this.state.alerts.push(alertData);
        }

        // Show notification
        this.notification.add(
            _t('Sensor Alert: %s - %s %s', data.sensor_name, data.current_value, data.unit),
            { type: data.status === 'critical' ? 'danger' : 'warning' }
        );

        // Play alert sound if available
        this._playAlertSound();
    }

    _handleDisconnection() {
        this.reconnectAttempts++;
        
        if (this.reconnectAttempts <= this.maxReconnectAttempts) {
            this.notification.add(
                _t('Connection lost. Attempting to reconnect... (%s/%s)', this.reconnectAttempts, this.maxReconnectAttempts),
                { type: 'warning' }
            );
            
            // Attempt to reconnect with exponential backoff
            const backoffTime = Math.min(1000 * Math.pow(2, this.reconnectAttempts - 1), 30000);
            setTimeout(() => {
                this._attemptReconnection();
            }, backoffTime);
        } else {
            this.notification.add(
                _t('Connection failed after %s attempts. Please refresh the page.', this.maxReconnectAttempts),
                { type: 'danger', sticky: true }
            );
        }
    }

    _attemptReconnection() {
        try {
            // Force a data refresh to test connection
            this._loadSensorData().then(() => {
                this.state.connectionStatus = 'connected';
                this.reconnectAttempts = 0;
                this.notification.add(_t('Connection restored'), { type: 'success' });
            }).catch(() => {
                // Connection still failed, will be handled by the next disconnect event
            });
        } catch (error) {
            console.error('Reconnection attempt failed:', error);
        }
    }

    _playAlertSound() {
        // Create audio element if it doesn't exist
        if (!this.alertSound) {
            this.alertSound = new Audio('/facilities_management/static/src/sounds/alert.mp3');
            this.alertSound.volume = 0.5; // Set volume to 50%
        }
        
        // Play alert sound with error handling
        this.alertSound.play().catch(error => {
            console.log('Could not play alert sound:', error);
        });
    }

    async _loadSensorData() {
        try {
            const sensors = await this.rpc("/web/dataset/call_kw", {
                model: 'facilities.asset.sensor',
                method: 'search_read',
                args: [],
                kwargs: {
                    domain: [['active', '=', true]],
                    fields: ['name', 'sensor_type', 'current_value', 'status', 'asset_id', 'unit', 'last_reading_time']
                }
            });
            this.state.sensors = sensors;
            await this._loadAlerts();
            this.state.connectionStatus = 'connected';
        } catch (error) {
            console.error('Error loading sensor data:', error);
            this.state.connectionStatus = 'error';
            this.notification.add(_t('Error loading sensor data'), { type: 'danger' });
            throw error; // Re-throw for reconnection logic
        }
    }

    async _loadAlerts() {
        try {
            const alerts = await this.rpc("/web/dataset/call_kw", {
                model: 'facilities.asset.sensor',
                method: 'search_read',
                args: [],
                kwargs: {
                    domain: [['status', 'in', ['warning', 'critical']]],
                    fields: ['name', 'sensor_type', 'current_value', 'status', 'asset_id', 'unit', 'last_alert_time']
                }
            });
            this.state.alerts = alerts;
        } catch (error) {
            console.error('Error loading alerts:', error);
        }
    }

    get filteredSensors() {
        let sensors = this.state.sensors;
        if (this.state.filters.status !== 'all') {
            sensors = sensors.filter(s => s.status === this.state.filters.status);
        }
        if (this.state.filters.sensor_type !== 'all') {
            sensors = sensors.filter(s => s.sensor_type === this.state.filters.sensor_type);
        }
        if (this.state.filters.asset_id) {
            sensors = sensors.filter(s => s.asset_id[0] === this.state.filters.asset_id);
        }
        return sensors;
    }

    get filteredAlerts() {
        return this.state.alerts.filter(alert => {
            if (this.state.filters.asset_id && alert.asset_id[0] !== this.state.filters.asset_id) {
                return false;
            }
            return true;
        });
    }

    get connectionStatusText() {
        switch (this.state.connectionStatus) {
            case 'connected':
                return _t('Connected');
            case 'disconnected':
                return _t('Disconnected');
            case 'reconnecting':
                return _t('Reconnecting...');
            case 'error':
                return _t('Connection Error');
            default:
                return _t('Unknown');
        }
    }

    get connectionStatusClass() {
        switch (this.state.connectionStatus) {
            case 'connected':
                return 'text-success';
            case 'disconnected':
            case 'error':
                return 'text-danger';
            case 'reconnecting':
                return 'text-warning';
            default:
                return 'text-muted';
        }
    }

    _startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            if (this.state.connectionStatus === 'connected') {
                this._loadSensorData().catch(() => {
                    // Error will be handled by _loadSensorData
                });
            }
        }, 30000); // Refresh every 30 seconds
    }

    onSensorClick(ev) {
        const sensorId = parseInt(ev.currentTarget.dataset.sensorId);
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'facilities.asset.sensor',
            res_id: sensorId,
            views: [[false, 'form']],
            target: 'current'
        });
    }

    onAlertClick(ev) {
        const sensorId = parseInt(ev.currentTarget.dataset.sensorId);
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'facilities.asset.sensor',
            res_id: sensorId,
            views: [[false, 'form']],
            target: 'current'
        });
    }

    onRefreshSensors(ev) {
        ev.preventDefault();
        this._loadSensorData();
    }

    onFilterChange(ev) {
        const filterType = ev.currentTarget.dataset.filter;
        const value = ev.currentTarget.value;
        this.state.filters[filterType] = value;
    }
}

/**
 * Real-time Sensor Chart Widget
 */
export class SensorChartWidget extends Component {
    static template = "facilities_management.SensorChartWidget";
    static props = ["sensorId"];
    
    setup() {
        this.rpc = useService("rpc");
        this.state = useState({
            chartData: [],
            chartType: 'line',
            timeRange: '24h'
        });
        
        onWillStart(async () => {
            await this._loadChartData();
        });
        
        onMounted(() => {
            this._initChart();
        });
    }

    async _loadChartData() {
        try {
            const data = await this.rpc("/web/dataset/call_kw", {
                model: 'facilities.asset.sensor.data',
                method: 'search_read',
                args: [],
                kwargs: {
                    domain: [['sensor_id', '=', this.props.sensorId]],
                    fields: ['reading_time', 'value', 'status'],
                    order: 'reading_time desc',
                    limit: 100
                }
            });
            this.state.chartData = data.reverse();
            this._updateChart();
        } catch (error) {
            console.error('Error loading chart data:', error);
        }
    }

    _initChart() {
        // Initialize chart library (Chart.js or similar)
        if (typeof Chart !== 'undefined') {
            const canvas = this.el.querySelector('.sensor-chart');
            if (!canvas) {
                console.warn('Sensor chart canvas not found');
                return;
            }
            
            const ctx = canvas.getContext('2d');
            if (!ctx) {
                console.warn('Could not get 2D context for sensor chart');
                return;
            }
            
            // Validate chart data before creating
            const chartData = this.state.chartData || [];
            const validData = chartData.filter(d => 
                d && 
                typeof d.reading_time !== 'undefined' && 
                typeof d.value !== 'undefined'
            );
            
            try {
                this.chart = new Chart(ctx, {
                    type: this.state.chartType,
                    data: {
                        labels: validData.map(d => d.reading_time),
                        datasets: [{
                            label: 'Sensor Value',
                            data: validData.map(d => d.value),
                            borderColor: 'rgb(75, 192, 192)',
                            tension: 0.1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            } catch (error) {
                console.error('Error initializing Chart.js:', error);
                // Fallback: show data in a simple format
                this._showChartFallback(validData);
            }
        } else {
            console.warn('Chart.js is not loaded. Chart functionality will be disabled.');
            // Fallback: show data in a simple format
            const chartData = this.state.chartData || [];
            const validData = chartData.filter(d => 
                d && 
                typeof d.reading_time !== 'undefined' && 
                typeof d.value !== 'undefined'
            );
            this._showChartFallback(validData);
        }
    }

    _showChartFallback(data) {
        // Simple fallback when Chart.js is not available
        const canvas = this.el.querySelector('.sensor-chart');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            if (ctx) {
                // Clear canvas
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                // Draw a simple text representation
                ctx.fillStyle = '#333';
                ctx.font = '12px Arial';
                ctx.textAlign = 'center';
                
                if (data.length === 0) {
                    ctx.fillText('No data available', canvas.width / 2, canvas.height / 2);
                } else {
                    ctx.fillText(`${data.length} data points available`, canvas.width / 2, canvas.height / 2);
                    ctx.fillText('Chart.js required for visualization', canvas.width / 2, canvas.height / 2 + 20);
                }
            }
        }
    }

    _updateChart() {
        if (this.chart && typeof Chart !== 'undefined') {
            const chartData = this.state.chartData || [];
            
            // Validate data before updating chart
            const validData = chartData.filter(d => 
                d && 
                typeof d.reading_time !== 'undefined' && 
                typeof d.value !== 'undefined'
            );
            
            if (validData.length === 0) {
                console.warn('No valid chart data available for update');
                return;
            }
            
            try {
                const labels = validData.map(d => d.reading_time);
                const values = validData.map(d => d.value);
                
                this.chart.data.labels = labels;
                this.chart.data.datasets[0].data = values;
                this.chart.update();
            } catch (error) {
                console.error('Error updating Chart.js:', error);
                this._showChartFallback(validData);
            }
        } else if (typeof Chart === 'undefined') {
            // Chart.js not available, update fallback
            const chartData = this.state.chartData || [];
            const validData = chartData.filter(d => 
                d && 
                typeof d.reading_time !== 'undefined' && 
                typeof d.value !== 'undefined'
            );
            this._showChartFallback(validData);
        }
    }

    onChartControlClick(ev) {
        const control = ev.currentTarget.dataset.control;
        if (control === 'refresh') {
            this._loadChartData();
        } else if (control === 'chart-type') {
            this.state.chartType = this.state.chartType === 'line' ? 'bar' : 'line';
            this._initChart();
        }
    }
}

/**
 * IoT Alert Notification Widget
 */
export class IoTAlertWidget extends Component {
    static template = "facilities_management.IoTAlertWidget";
    
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.notification = useService("notification");
        
        this.state = useState({
            alerts: []
        });
        
        this.alertSound = null;
        
        onWillStart(async () => {
            await this._loadAlerts();
        });
        
        onMounted(() => {
            this.alertSound = new Audio('/facilities_management/static/src/sounds/alert.mp3');
            this._startAlertPolling();
        });
    }

    async _loadAlerts() {
        try {
            const alerts = await this.rpc("/web/dataset/call_kw", {
                model: 'facilities.asset.sensor',
                method: 'search_read',
                args: [],
                kwargs: {
                    domain: [['status', 'in', ['warning', 'critical']], ['alert_enabled', '=', true]],
                    fields: ['name', 'sensor_type', 'current_value', 'status', 'asset_id', 'unit', 'last_alert_time']
                }
            });
            
            const newAlerts = alerts.filter(alert => 
                !this.state.alerts.some(existing => existing.id === alert.id)
            );
            
            if (newAlerts.length > 0) {
                this._playAlertSound();
                this._showNotification(newAlerts);
            }
            
            this.state.alerts = alerts;
        } catch (error) {
            console.error('Error loading alerts:', error);
        }
    }

    _playAlertSound() {
        if (this.alertSound) {
            this.alertSound.play().catch(error => {
                console.log('Could not play alert sound:', error);
            });
        }
    }

    _showNotification(alerts) {
        if ('Notification' in window && Notification.permission === 'granted') {
            alerts.forEach(alert => {
                new Notification('IoT Alert', {
                    body: `${alert.name}: ${alert.current_value} ${alert.unit} (${alert.status})`,
                    icon: '/facilities_management/static/src/img/alert-icon.png'
                });
            });
        }
    }

    _startAlertPolling() {
        setInterval(() => {
            this._loadAlerts();
        }, 10000); // Check every 10 seconds
    }

    onAlertClick(ev) {
        const sensorId = parseInt(ev.currentTarget.dataset.sensorId);
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'facilities.asset.sensor',
            res_id: sensorId,
            views: [[false, 'form']],
            target: 'current'
        });
    }

    onDismissAlert(ev) {
        ev.stopPropagation();
        const alertId = parseInt(ev.currentTarget.dataset.alertId);
        this.state.alerts = this.state.alerts.filter(alert => alert.id !== alertId);
    }
}

// Register components
registry.category("actions").add("iot_monitoring_dashboard", IoTMonitoringWidget);
registry.category("actions").add("sensor_chart", SensorChartWidget);
registry.category("actions").add("iot_alert_widget", IoTAlertWidget);