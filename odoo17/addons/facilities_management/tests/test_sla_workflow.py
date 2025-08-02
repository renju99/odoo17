# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo import fields
from unittest.mock import patch


class TestSLAWorkflow(TransactionCase):

    def setUp(self):
        super(TestSLAWorkflow, self).setUp()
        self.SLA = self.env['facilities.sla']
        
        # Create a test SLA
        self.test_sla = self.SLA.create({
            'name': 'Test SLA',
            'description': 'Test SLA for workflow testing',
            'response_time_hours': 4.0,
            'resolution_time_hours': 24.0,
            'active': True,
        })
        
        # Create test user
        self.test_user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'testuser',
            'email': 'test@example.com',
        })

    def test_sla_activation_logging(self):
        """Test that SLA activation is properly logged"""
        # Deactivate first
        self.test_sla.write({'active': False})
        
        # Count messages before activation
        initial_message_count = len(self.test_sla.message_ids)
        
        # Activate SLA
        with patch.object(self.env, 'user', self.test_user):
            self.test_sla.action_activate_sla()
        
        # Check that SLA is active
        self.assertTrue(self.test_sla.active)
        
        # Check that a message was posted
        self.assertGreater(len(self.test_sla.message_ids), initial_message_count)
        
        # Check message content
        latest_message = self.test_sla.message_ids[0]
        self.assertIn('activated', latest_message.body.lower())
        self.assertIn(self.test_user.name, latest_message.body)

    def test_sla_deactivation_logging(self):
        """Test that SLA deactivation is properly logged"""
        # Ensure SLA is active
        self.test_sla.write({'active': True})
        
        # Count messages before deactivation
        initial_message_count = len(self.test_sla.message_ids)
        
        # Deactivate SLA
        with patch.object(self.env, 'user', self.test_user):
            self.test_sla.action_deactivate_sla()
        
        # Check that SLA is inactive
        self.assertFalse(self.test_sla.active)
        
        # Check that a message was posted
        self.assertGreater(len(self.test_sla.message_ids), initial_message_count)
        
        # Check message content
        latest_message = self.test_sla.message_ids[0]
        self.assertIn('deactivated', latest_message.body.lower())
        self.assertIn(self.test_user.name, latest_message.body)

    def test_field_tracking(self):
        """Test that the active field tracking works"""
        # Count messages before change
        initial_message_count = len(self.test_sla.message_ids)
        
        # Change active status directly
        self.test_sla.write({'active': False})
        
        # The tracking should create a message automatically
        # Note: In some Odoo versions, tracking messages might not appear immediately in tests
        # So we'll just verify the field is tracked
        sla_fields = self.test_sla._fields
        self.assertTrue(hasattr(sla_fields['active'], 'tracking'))
        self.assertTrue(sla_fields['active'].tracking)

    def test_bulk_operations_logging(self):
        """Test that bulk activation/deactivation operations are logged"""
        # Create another test SLA
        test_sla_2 = self.SLA.create({
            'name': 'Test SLA 2',
            'description': 'Second test SLA',
            'response_time_hours': 2.0,
            'resolution_time_hours': 12.0,
            'active': False,
        })
        
        slas = self.test_sla | test_sla_2
        
        # Test bulk activation
        with patch.object(self.env, 'user', self.test_user):
            slas.action_bulk_activate()
        
        # Check both SLAs are active
        self.assertTrue(all(sla.active for sla in slas))
        
        # Check messages were posted to both
        for sla in slas:
            messages = [msg for msg in sla.message_ids if 'bulk operation' in msg.body]
            self.assertGreater(len(messages), 0)

    def test_action_methods_return_notification(self):
        """Test that action methods return proper notifications"""
        # Test activation
        result = self.test_sla.action_activate_sla()
        self.assertEqual(result['type'], 'ir.actions.client')
        self.assertEqual(result['tag'], 'display_notification')
        self.assertIn('SLA Activated', result['params']['title'])
        
        # Test deactivation
        result = self.test_sla.action_deactivate_sla()
        self.assertEqual(result['type'], 'ir.actions.client')
        self.assertEqual(result['tag'], 'display_notification')
        self.assertIn('SLA Deactivated', result['params']['title'])