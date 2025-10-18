import json
import unittest
from unittest.mock import Mock
import azure.functions as func
import sys
import os

# Add parent directory to path to import the function
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from validateRefund import main, calculate_refund_percentage


class TestCalculateRefundPercentage(unittest.TestCase):
    """Test cases for calculate_refund_percentage function"""

    def test_full_refund_within_30_days(self):
        """Test full refund for purchases within 30 days"""
        percentage, code, message = calculate_refund_percentage(30, False)
        self.assertEqual(percentage, 100)
        self.assertEqual(code, "FULL_REFUND")
        self.assertIn("within 30 days", message)

    def test_full_refund_day_1(self):
        """Test full refund for purchase 1 day ago"""
        percentage, code, message = calculate_refund_percentage(1, False)
        self.assertEqual(percentage, 100)
        self.assertEqual(code, "FULL_REFUND")

    def test_partial_refund_31_days(self):
        """Test partial refund at exactly 31 days"""
        percentage, code, message = calculate_refund_percentage(31, False)
        self.assertEqual(percentage, 70)
        self.assertEqual(code, "PARTIAL_REFUND")
        self.assertIn("31-60 days", message)

    def test_partial_refund_60_days(self):
        """Test partial refund at exactly 60 days"""
        percentage, code, message = calculate_refund_percentage(60, False)
        self.assertEqual(percentage, 70)
        self.assertEqual(code, "PARTIAL_REFUND")

    def test_no_refund_after_60_days(self):
        """Test no refund for purchases over 60 days"""
        percentage, code, message = calculate_refund_percentage(61, False)
        self.assertEqual(percentage, 0)
        self.assertEqual(code, "NO_REFUND")
        self.assertIn("over 60 days", message)

    def test_no_refund_90_days(self):
        """Test no refund at 90 days"""
        percentage, code, message = calculate_refund_percentage(90, False)
        self.assertEqual(percentage, 0)
        self.assertEqual(code, "NO_REFUND")

    def test_vip_bonus_within_30_days(self):
        """Test VIP bonus doesn't exceed 100% for full refund"""
        percentage, code, message = calculate_refund_percentage(30, True)
        self.assertEqual(percentage, 100)  # Capped at 100%
        self.assertEqual(code, "FULL_REFUND_VIP")
        self.assertIn("VIP bonus", message)

    def test_vip_bonus_31_to_60_days(self):
        """Test VIP bonus adds 10% for partial refund"""
        percentage, code, message = calculate_refund_percentage(45, True)
        self.assertEqual(percentage, 80)  # 70% + 10% VIP bonus
        self.assertEqual(code, "PARTIAL_REFUND_VIP")
        self.assertIn("VIP bonus", message)

    def test_vip_bonus_after_60_days(self):
        """Test VIP bonus on no-refund period"""
        percentage, code, message = calculate_refund_percentage(61, True)
        self.assertEqual(percentage, 10)  # 0% + 10% VIP bonus
        self.assertEqual(code, "NO_REFUND_VIP")
        self.assertIn("VIP bonus", message)

    def test_edge_case_day_0(self):
        """Test refund on day 0 (same day purchase)"""
        percentage, code, message = calculate_refund_percentage(0, False)
        self.assertEqual(percentage, 100)
        self.assertEqual(code, "FULL_REFUND")


class TestValidateRefundFunction(unittest.TestCase):
    """Test cases for the main Azure Function"""

    def test_valid_request_non_vip_within_30_days(self):
        """Test valid request for non-VIP customer within 30 days"""
        # Construct a mock HTTP request
        req_body = {
            "orderId": "ORD-12345",
            "sku": "PROD-001",
            "daysSincePurchase": 15,
            "vipStatus": False
        }
        req = func.HttpRequest(
            method='POST',
            body=json.dumps(req_body).encode('utf-8'),
            url='/api/validateRefund'
        )

        # Call the function
        response = main(req)

        # Validate response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.get_body())
        self.assertEqual(response_data['orderId'], "ORD-12345")
        self.assertEqual(response_data['sku'], "PROD-001")
        self.assertEqual(response_data['refundAmount'], 100)
        self.assertEqual(response_data['reasonCode'], "FULL_REFUND")

    def test_valid_request_vip_31_to_60_days(self):
        """Test valid request for VIP customer between 31-60 days"""
        req_body = {
            "orderId": "ORD-67890",
            "sku": "PROD-002",
            "daysSincePurchase": 45,
            "vipStatus": True
        }
        req = func.HttpRequest(
            method='POST',
            body=json.dumps(req_body).encode('utf-8'),
            url='/api/validateRefund'
        )

        response = main(req)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.get_body())
        self.assertEqual(response_data['refundAmount'], 80)  # 70% + 10% VIP
        self.assertEqual(response_data['reasonCode'], "PARTIAL_REFUND_VIP")

    def test_valid_request_non_vip_over_60_days(self):
        """Test valid request for non-VIP customer over 60 days"""
        req_body = {
            "orderId": "ORD-11111",
            "sku": "PROD-003",
            "daysSincePurchase": 90,
            "vipStatus": False
        }
        req = func.HttpRequest(
            method='POST',
            body=json.dumps(req_body).encode('utf-8'),
            url='/api/validateRefund'
        )

        response = main(req)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.get_body())
        self.assertEqual(response_data['refundAmount'], 0)
        self.assertEqual(response_data['reasonCode'], "NO_REFUND")

    def test_invalid_json(self):
        """Test request with invalid JSON"""
        req = func.HttpRequest(
            method='POST',
            body=b'invalid json',
            url='/api/validateRefund'
        )

        response = main(req)

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.get_body())
        self.assertIn('error', response_data)

    def test_missing_required_fields(self):
        """Test request with missing required fields"""
        req_body = {
            "orderId": "ORD-12345",
            "sku": "PROD-001"
            # Missing daysSincePurchase and vipStatus
        }
        req = func.HttpRequest(
            method='POST',
            body=json.dumps(req_body).encode('utf-8'),
            url='/api/validateRefund'
        )

        response = main(req)

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.get_body())
        self.assertIn('error', response_data)
        self.assertIn('Missing required fields', response_data['error'])

    def test_invalid_days_since_purchase_type(self):
        """Test request with invalid daysSincePurchase type"""
        req_body = {
            "orderId": "ORD-12345",
            "sku": "PROD-001",
            "daysSincePurchase": "invalid",
            "vipStatus": False
        }
        req = func.HttpRequest(
            method='POST',
            body=json.dumps(req_body).encode('utf-8'),
            url='/api/validateRefund'
        )

        response = main(req)

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.get_body())
        self.assertIn('error', response_data)

    def test_negative_days_since_purchase(self):
        """Test request with negative daysSincePurchase"""
        req_body = {
            "orderId": "ORD-12345",
            "sku": "PROD-001",
            "daysSincePurchase": -5,
            "vipStatus": False
        }
        req = func.HttpRequest(
            method='POST',
            body=json.dumps(req_body).encode('utf-8'),
            url='/api/validateRefund'
        )

        response = main(req)

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.get_body())
        self.assertIn('error', response_data)

    def test_invalid_vip_status_type(self):
        """Test request with invalid vipStatus type"""
        req_body = {
            "orderId": "ORD-12345",
            "sku": "PROD-001",
            "daysSincePurchase": 15,
            "vipStatus": "yes"
        }
        req = func.HttpRequest(
            method='POST',
            body=json.dumps(req_body).encode('utf-8'),
            url='/api/validateRefund'
        )

        response = main(req)

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.get_body())
        self.assertIn('error', response_data)


if __name__ == '__main__':
    unittest.main()
