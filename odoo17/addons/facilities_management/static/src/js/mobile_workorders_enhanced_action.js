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