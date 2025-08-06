/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

/**
 * Mobile Asset Scanner Component
 */
class MobileScannerComponent extends Component {
    static template = "facilities_management.MobileScannerTemplate";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.dialog = useService("dialog");

        this.state = useState({
            scanType: 'barcode',
            isScanning: false,
            scanResults: [],
            flashEnabled: false,
            cameraSupported: false
        });

        this.scannerRef = useRef("scanner");
        this.videoRef = useRef("video");
        this.scanner = null;
        this.cameraStream = null;

        onMounted(() => {
            this._checkCameraSupport();
            this._initScanner();
        });

        onWillUnmount(() => {
            this._stopScanning();
        });
    }

    _checkCameraSupport() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.state.cameraSupported = false;
            return false;
        }
        this.state.cameraSupported = true;
        return true;
    }

    _initScanner() {
        // Initialize scanner library (e.g., QuaggaJS for barcode, jsQR for QR codes)
        if (typeof Quagga !== 'undefined' && this.scannerRef.el) {
            Quagga.init({
                inputStream: {
                    name: "Live",
                    type: "LiveStream",
                    target: this.scannerRef.el,
                    constraints: {
                        width: { min: 640 },
                        height: { min: 480 },
                        facingMode: "environment"
                    }
                },
                locator: {
                    patchSize: "medium",
                    halfSample: true
                },
                numOfWorkers: 2,
                frequency: 10,
                decoder: {
                    readers: [
                        "code_128_reader",
                        "ean_reader",
                        "ean_8_reader",
                        "code_39_reader",
                        "code_39_vin_reader",
                        "codabar_reader",
                        "upc_reader",
                        "upc_e_reader",
                        "i2of5_reader"
                    ]
                },
                locate: true
            }, (err) => {
                if (err) {
                    console.error('Scanner initialization failed:', err);
                } else {
                    Quagga.start();
                }
            });

            Quagga.onDetected(this._onBarcodeDetected.bind(this));
        }
    }

    onScanClick() {
        if (this.state.isScanning) {
            this._stopScanning();
        } else {
            this._startScanning();
        }
    }

    _startScanning() {
        this.state.isScanning = true;

        if (this.state.scanType === 'camera') {
            this._startCamera();
        } else if (this.state.scanType === 'qr') {
            this._startQRScanner();
        }
    }

    _stopScanning() {
        this.state.isScanning = false;

        if (this.cameraStream) {
            this.cameraStream.getTracks().forEach(track => track.stop());
            this.cameraStream = null;
        }

        if (typeof Quagga !== 'undefined') {
            Quagga.stop();
        }
    }

    _startCamera() {
        navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: 'environment',
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        }).then((stream) => {
            this.cameraStream = stream;
            if (this.videoRef.el) {
                this.videoRef.el.srcObject = stream;
                this.videoRef.el.play();
            }
        }).catch((error) => {
            console.error('Camera access failed:', error);
            this.notification.add(_t('Camera access failed'), { type: 'danger' });
        });
    }

    _startQRScanner() {
        const video = this.videoRef.el;
        
        // Use jsQR library for QR code scanning
        if (typeof jsQR !== 'undefined' && video) {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            
            const scanQR = () => {
                if (video.readyState === video.HAVE_ENOUGH_DATA) {
                    canvas.height = video.videoHeight;
                    canvas.width = video.videoWidth;
                    context.drawImage(video, 0, 0, canvas.width, canvas.height);
                    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
                    const code = jsQR(imageData.data, imageData.width, imageData.height);
                    
                    if (code) {
                        this._onQRCodeDetected(code.data);
                        return;
                    }
                }
                if (this.state.isScanning) {
                    requestAnimationFrame(scanQR);
                }
            };
            scanQR();
        }
    }

    async _onBarcodeDetected(result) {
        if (this.state.isScanning) {
            await this._processScanResult(result.codeResult.code, 'barcode');
        }
    }

    async _onQRCodeDetected(data) {
        if (this.state.isScanning) {
            await this._processScanResult(data, 'qr');
        }
    }

    async _processScanResult(code, type) {
        this._stopScanning();
        
        const location = await this._getCurrentLocation();
        const scanResult = {
            code: code,
            type: type,
            timestamp: new Date(),
            location: location
        };

        this.state.scanResults.unshift(scanResult);
        this._lookupAsset(code);
    }

    _getCurrentLocation() {
        if (navigator.geolocation) {
            return new Promise((resolve) => {
                navigator.geolocation.getCurrentPosition((position) => {
                    resolve({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    });
                }, () => {
                    resolve(null);
                });
            });
        }
        return Promise.resolve(null);
    }

    async _lookupAsset(code) {
        try {
            const assets = await this.orm.searchRead(
                'facilities.asset',
                [['asset_code', '=', code]],
                ['name', 'asset_code', 'state', 'location', 'asset_category_id']
            );
            
            if (assets.length > 0) {
                this._showAssetInfo(assets[0]);
            } else {
                this._showAssetNotFound(code);
            }
        } catch (error) {
            console.error('Failed to lookup asset:', error);
            this.notification.add(_t('Failed to lookup asset'), { type: 'danger' });
        }
    }

    _showAssetInfo(asset) {
        this.dialog.add(ConfirmationDialog, {
            title: _t('Asset Found'),
            body: _t('Asset: %(name)s (%(code)s)\nState: %(state)s\nLocation: %(location)s', {
                name: asset.name,
                code: asset.asset_code,
                state: asset.state,
                location: asset.location || _t('Unknown')
            }),
            confirm: () => this._updateAssetLocation(asset),
            confirmLabel: _t('Update Location'),
            cancel: () => {},
            cancelLabel: _t('Close'),
        });
    }

    _showAssetNotFound(code) {
        this.dialog.add(ConfirmationDialog, {
            title: _t('Asset Not Found'),
            body: _t('No asset found with code: %(code)s', { code }),
            confirm: () => this._createNewAsset(code),
            confirmLabel: _t('Create New Asset'),
            cancel: () => {},
            cancelLabel: _t('Close'),
        });
    }

    async _updateAssetLocation(asset) {
        try {
            const location = this._getCurrentLocation();
            
            await this.orm.write('facilities.asset', [asset.id], {
                last_scan_location: location ? `${location.latitude}, ${location.longitude}` : 'Unknown',
                last_scan_time: new Date().toISOString()
            });
            
            this.notification.add(_t('Asset location updated successfully'), { type: 'success' });
        } catch (error) {
            console.error('Failed to update asset location:', error);
            this.notification.add(_t('Failed to update asset location'), { type: 'danger' });
        }
    }

    _viewAssetDetails(asset) {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'facilities.asset',
            res_id: asset.id,
            views: [[false, 'form']],
            target: 'current'
        });
    }

    _createNewAsset(code) {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'facilities.asset',
            views: [[false, 'form']],
            target: 'current',
            context: {
                'default_asset_code': code
            }
        });
    }

    onManualEntry() {
        // For manual entry, we'll use a simple prompt for now
        // In a full implementation, you'd want to create a proper dialog component
        const code = prompt(_t('Enter asset code:'));
        if (code) {
            this._lookupAsset(code);
        }
    }

    onCameraToggle() {
        if (this.cameraStream) {
            this._stopCamera();
        } else {
            this._startCamera();
        }
    }

    _stopCamera() {
        if (this.cameraStream) {
            this.cameraStream.getTracks().forEach(track => track.stop());
            this.cameraStream = null;
        }
    }

    onFlashToggle() {
        this.state.flashEnabled = !this.state.flashEnabled;
        
        if (this.cameraStream) {
            const track = this.cameraStream.getVideoTracks()[0];
            if (track && track.getCapabilities) {
                const capabilities = track.getCapabilities();
                if (capabilities.torch) {
                    track.applyConstraints({
                        advanced: [{ torch: this.state.flashEnabled }]
                    });
                }
            }
        }
    }

    onScanTypeChange(ev) {
        this.state.scanType = ev.target.value;
    }

    onScanResultClick(ev) {
        const code = ev.target.dataset.code;
        this._lookupAsset(code);
    }

    onActionButtonClick(ev) {
        const action = ev.target.dataset.action;
        const assetId = parseInt(ev.target.dataset.assetId);
        
        switch (action) {
            case 'maintenance':
                this._createMaintenanceRequest(assetId);
                break;
            case 'inspection':
                this._createInspection(assetId);
                break;
            case 'sensor_reading':
                this._recordSensorReading(assetId);
                break;
        }
    }

    _createMaintenanceRequest(assetId) {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'maintenance.request',
            views: [[false, 'form']],
            target: 'current',
            context: {
                'default_equipment_id': assetId
            }
        });
    }

    _createInspection(assetId) {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'facilities.asset.scan.wizard',
            views: [[false, 'form']],
            target: 'current',
            context: {
                'default_asset_id': assetId,
                'default_action_type': 'inspection'
            }
        });
    }

    _recordSensorReading(assetId) {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'facilities.asset.scan.wizard',
            views: [[false, 'form']],
            target: 'current',
            context: {
                'default_asset_id': assetId,
                'default_action_type': 'sensor_reading'
            }
        });
    }
}

/**
 * Offline Scanner Component
 */
class OfflineScannerComponent extends Component {
    static template = "facilities_management.OfflineScannerTemplate";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");

        this.state = useState({
            offlineScans: [],
            isOnline: navigator.onLine
        });

        onMounted(() => {
            this._loadOfflineScans();
            this._setupOnlineOfflineHandlers();
        });
    }

    _setupOnlineOfflineHandlers() {
        window.addEventListener('online', () => {
            this.state.isOnline = true;
            this._syncOfflineData();
        });
        
        window.addEventListener('offline', () => {
            this.state.isOnline = false;
        });
    }

    _loadOfflineScans() {
        const scans = localStorage.getItem('offline_scans');
        if (scans) {
            this.state.offlineScans = JSON.parse(scans);
        }
    }

    _saveOfflineScans() {
        localStorage.setItem('offline_scans', JSON.stringify(this.state.offlineScans));
    }

    _addOfflineScan(scanData) {
        this.state.offlineScans.push({
            ...scanData,
            timestamp: new Date().toISOString(),
            synced: false
        });
        this._saveOfflineScans();
    }

    async _syncOfflineData() {
        if (!this.state.isOnline || this.state.offlineScans.length === 0) {
            return;
        }

        const unsyncedScans = this.state.offlineScans.filter(scan => !scan.synced);
        
        for (const scan of unsyncedScans) {
            try {
                await this.orm.create('facilities.asset.scan.wizard', {
                    asset_id: scan.asset_id,
                    scan_type: scan.scan_type,
                    scanned_code: scan.code,
                    scan_location: scan.location,
                    action_type: scan.action_type
                });
                
                scan.synced = true;
                this._saveOfflineScans();
            } catch (error) {
                console.error('Failed to sync scan:', error);
                this.notification.add(_t('Failed to sync scan'), { type: 'danger' });
            }
        }
    }

    onSyncClick() {
        this._syncOfflineData();
    }

    onOfflineScan() {
        // Simulate offline scan
        const scanData = {
            code: 'OFFLINE_' + Date.now(),
            asset_id: 1,
            scan_type: 'manual',
            location: 'Offline Location',
            action_type: 'location_update'
        };
        this._addOfflineScan(scanData);
    }
}

// Register components
registry.category('actions').add('mobile_scanner', MobileScannerComponent);
registry.category('actions').add('offline_scanner', OfflineScannerComponent);

export {
    MobileScannerComponent,
    OfflineScannerComponent
};