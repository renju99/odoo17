odoo.define('facilities_management.mobile_workorder', [
    'web.core',
    'web.Widget',
    'web.public.widget',
    'web.FormView',
    'web.FormController'
], function (core, Widget, publicWidget, FormView, FormController) {
    'use strict';

    var _t = core._t;
    var QWeb = core.qweb;

    // Enhanced Mobile Workorder Form Controller
    var MobileWorkorderFormController = FormController.extend({
        events: _.extend({}, FormController.prototype.events, {
            'click .btn-loading': '_onLoadingButtonClick',
            'click .o_boolean_toggle': '_onToggleClick',
            'change input[type="file"]': '_onImageUpload',
        }),

        /**
         * @override
         */
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self._setupMobileEnhancements();
                self._setupImageUpload();
                self._setupRealTimeUpdates();
            });
        },

        /**
         * Setup mobile-specific enhancements
         */
        _setupMobileEnhancements: function () {
            var self = this;
            
            // Add loading states to buttons
            this.$('.btn').on('click', function () {
                var $btn = $(this);
                if (!$btn.hasClass('btn-loading')) {
                    $btn.addClass('btn-loading');
                    setTimeout(function () {
                        $btn.removeClass('btn-loading');
                    }, 2000);
                }
            });

            // Add card hover effects
            this.$('.card').on('mouseenter', function () {
                $(this).addClass('hover');
            }).on('mouseleave', function () {
                $(this).removeClass('hover');
            });

            // Add swipe gestures for mobile
            this._setupSwipeGestures();
        },

        /**
         * Setup image upload functionality
         */
        _setupImageUpload: function () {
            var self = this;
            
            // Handle image upload buttons
            this.$('.btn-outline-warning, .btn-outline-success').on('click', function (e) {
                e.preventDefault();
                var $btn = $(this);
                var fieldName = $btn.closest('.card').find('field[name*="image"]').attr('name');
                
                // Create file input
                var $fileInput = $('<input type="file" accept="image/*" capture="camera" style="display: none;">');
                $fileInput.on('change', function (e) {
                    var file = e.target.files[0];
                    if (file) {
                        self._uploadImage(file, fieldName);
                    }
                });
                
                $fileInput.click();
            });
        },

        /**
         * Upload image to the server
         */
        _uploadImage: function (file, fieldName) {
            var self = this;
            var reader = new FileReader();
            
            reader.onload = function (e) {
                var base64Data = e.target.result.split(',')[1];
                
                // Update the field value
                self.$('field[name="' + fieldName + '"]').val(base64Data);
                
                // Show preview
                var $preview = self.$('field[name="' + fieldName + '"]').closest('.card-body').find('.img-fluid');
                if ($preview.length) {
                    $preview.attr('src', e.target.result);
                }
                
                // Show success message
                self.displayNotification({
                    title: _t('Success'),
                    message: _t('Image uploaded successfully'),
                    type: 'success',
                });
            };
            
            reader.readAsDataURL(file);
        },

        /**
         * Setup swipe gestures for mobile navigation
         */
        _setupSwipeGestures: function () {
            var self = this;
            var startX, startY, endX, endY;
            
            this.$el.on('touchstart', function (e) {
                startX = e.originalEvent.touches[0].clientX;
                startY = e.originalEvent.touches[0].clientY;
            });
            
            this.$el.on('touchend', function (e) {
                endX = e.originalEvent.changedTouches[0].clientX;
                endY = e.originalEvent.changedTouches[0].clientY;
                
                var diffX = startX - endX;
                var diffY = startY - endY;
                
                // Swipe left (next workorder)
                if (diffX > 50 && Math.abs(diffY) < 50) {
                    self._navigateToNextWorkorder();
                }
                // Swipe right (previous workorder)
                else if (diffX < -50 && Math.abs(diffY) < 50) {
                    self._navigateToPreviousWorkorder();
                }
            });
        },

        /**
         * Navigate to next workorder
         */
        _navigateToNextWorkorder: function () {
            // Implementation for navigation
            this.displayNotification({
                title: _t('Navigation'),
                message: _t('Swipe left detected - Next workorder'),
                type: 'info',
            });
        },

        /**
         * Navigate to previous workorder
         */
        _navigateToPreviousWorkorder: function () {
            // Implementation for navigation
            this.displayNotification({
                title: _t('Navigation'),
                message: _t('Swipe right detected - Previous workorder'),
                type: 'info',
            });
        },

        /**
         * Setup real-time updates
         */
        _setupRealTimeUpdates: function () {
            var self = this;
            
            // Update SLA status every minute
            setInterval(function () {
                self._updateSLAStatus();
            }, 60000);
            
            // Update work timing
            setInterval(function () {
                self._updateWorkTiming();
            }, 30000);
        },

        /**
         * Update SLA status
         */
        _updateSLAStatus: function () {
            var self = this;
            this._rpc({
                model: 'maintenance.workorder',
                method: 'read',
                args: [[this.model], ['sla_response_status', 'sla_resolution_status']],
            }).then(function (result) {
                if (result && result[0]) {
                    var data = result[0];
                    self.$('field[name="sla_response_status"]').val(data.sla_response_status);
                    self.$('field[name="sla_resolution_status"]').val(data.sla_resolution_status);
                }
            });
        },

        /**
         * Update work timing
         */
        _updateWorkTiming: function () {
            var self = this;
            this._rpc({
                model: 'maintenance.workorder',
                method: 'read',
                args: [[this.model], ['actual_duration']],
            }).then(function (result) {
                if (result && result[0]) {
                    var data = result[0];
                    self.$('field[name="actual_duration"]').val(data.actual_duration);
                }
            });
        },

        /**
         * Handle loading button clicks
         */
        _onLoadingButtonClick: function (ev) {
            var $btn = $(ev.currentTarget);
            $btn.addClass('loading');
            
            // Remove loading class after action completes
            setTimeout(function () {
                $btn.removeClass('loading');
            }, 2000);
        },

        /**
         * Handle toggle clicks
         */
        _onToggleClick: function (ev) {
            var $toggle = $(ev.currentTarget);
            var fieldName = $toggle.attr('name');
            var value = $toggle.prop('checked');
            
            // Add visual feedback
            $toggle.closest('.card').addClass('updating');
            
            // Update the field
            this._rpc({
                model: 'maintenance.workorder.task',
                method: 'write',
                args: [[this.model], {[fieldName]: value}],
            }).then(function () {
                $toggle.closest('.card').removeClass('updating');
            });
        },

        /**
         * Handle image upload
         */
        _onImageUpload: function (ev) {
            var file = ev.target.files[0];
            if (file) {
                var fieldName = $(ev.currentTarget).attr('name');
                this._uploadImage(file, fieldName);
            }
        },
    });

    // Register the enhanced controller
    core.action_registry.add('mobile_workorder_form', MobileWorkorderFormController);

    // Mobile-specific utilities
    var MobileWorkorderUtils = {
        /**
         * Format duration for display
         */
        formatDuration: function (hours) {
            if (!hours) return '0h 0m';
            
            var h = Math.floor(hours);
            var m = Math.round((hours - h) * 60);
            
            return h + 'h ' + m + 'm';
        },

        /**
         * Get status color class
         */
        getStatusColor: function (status) {
            var colors = {
                'draft': 'info',
                'in_progress': 'warning',
                'completed': 'success',
                'cancelled': 'danger',
                'on_hold': 'secondary'
            };
            return colors[status] || 'secondary';
        },

        /**
         * Get priority color class
         */
        getPriorityColor: function (priority) {
            var colors = {
                '0': 'info',
                '1': 'secondary',
                '2': 'primary',
                '3': 'warning',
                '4': 'danger'
            };
            return colors[priority] || 'secondary';
        },

        /**
         * Get SLA status color class
         */
        getSLAStatusColor: function (status) {
            var colors = {
                'on_time': 'success',
                'at_risk': 'warning',
                'breached': 'danger',
                'completed': 'success'
            };
            return colors[status] || 'secondary';
        }
    };

    // Export utilities for use in templates
    core.bus.on('mobile_workorder_utils', function () {
        return MobileWorkorderUtils;
    });

    return {
        MobileWorkorderFormController: MobileWorkorderFormController,
        MobileWorkorderUtils: MobileWorkorderUtils,
    };
});

odoo.define('facilities_management.mobile_workorders_enhanced_action', [
    'web.core',
    'web.AbstractAction',
    'web.session',
], function (core, AbstractAction, session) {
    'use strict';

    var QWeb = core.qweb;

    var MobileWorkordersEnhancedAction = AbstractAction.extend({
        template: 'facilities_management.MobileWorkordersEnhanced',
        events: {
            'click .js-workorder-item': '_onClickWorkorderItem',
        },
        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.myWorkorders = [];
            this.allWorkorders = [];
            this._mobileFormViewId = null;
        },
        willStart: function () {
            var self = this;
            var uid = session.uid;
            var fields = ['name', 'asset_id', 'building_id', 'status', 'priority', 'sla_response_status', 'sla_resolution_status'];
            var myDomain = ['&', ['status', 'not in', ['completed', 'cancelled']], ['|', ['technician_id.user_id', '=', uid], ['technician_ids.user_id', '=', uid]]];
            var allDomain = [];
            return Promise.all([
                this._rpc({ model: 'maintenance.workorder', method: 'search_read', args: [myDomain, fields], kwargs: { order: 'priority desc, id desc', limit: 100 } }),
                this._rpc({ model: 'maintenance.workorder', method: 'search_read', args: [allDomain, fields], kwargs: { order: 'priority desc, id desc', limit: 100 } }),
                this._rpc({ model: 'ir.model.data', method: 'xmlid_to_res_id', args: ['facilities_management.view_workorder_mobile_enhanced_form'], kwargs: { raise_if_not_found: false } }),
            ]).then(function (results) {
                self.myWorkorders = results[0] || [];
                self.allWorkorders = results[1] || [];
                self._mobileFormViewId = results[2] || false;
            });
        },
        start: function () {
            this.$el.html(QWeb.render('facilities_management.MobileWorkordersEnhanced', {
                myWorkorders: this.myWorkorders,
                allWorkorders: this.allWorkorders,
            }));
            return this._super.apply(this, arguments);
        },
        _onClickWorkorderItem: function (ev) {
            var workorderId = parseInt(ev.currentTarget.getAttribute('data-id'));
            if (!workorderId) return;
            var action = {
                type: 'ir.actions.act_window',
                name: 'Work Order',
                res_model: 'maintenance.workorder',
                res_id: workorderId,
                target: 'current',
                views: this._mobileFormViewId ? [[this._mobileFormViewId, 'form']] : [[false, 'form']],
                view_mode: 'form',
                context: {},
            };
            this.do_action(action);
        },
    });

    core.action_registry.add('mobile_workorders_enhanced', MobileWorkordersEnhancedAction);

    return {
        MobileWorkordersEnhancedAction: MobileWorkordersEnhancedAction,
    };
});