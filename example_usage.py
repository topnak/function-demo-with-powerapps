"""
Example script demonstrating how to call the validateRefund Azure Function.
This can be used for testing the deployed function or as a reference for integration.
"""

import json
import requests

# Update this with your Azure Function URL after deployment
FUNCTION_URL = "https://your-function-app.azurewebsites.net/api/validateRefund"
# Update this with your function key from Azure Portal (or remove if using anonymous auth)
FUNCTION_KEY = "your-function-key-here"


def validate_refund(order_id: str, sku: str, days_since_purchase: int, vip_status: bool):
    """
    Call the validateRefund Azure Function.
    
    Args:
        order_id: Order identifier
        sku: Product SKU
        days_since_purchase: Number of days since purchase
        vip_status: Whether customer is VIP
        
    Returns:
        dict: Response from the function
    """
    headers = {
        "Content-Type": "application/json",
    }
    
    # Add function key to headers if using function-level auth
    if FUNCTION_KEY and FUNCTION_KEY != "your-function-key-here":
        headers["x-functions-key"] = FUNCTION_KEY
    
    payload = {
        "orderId": order_id,
        "sku": sku,
        "daysSincePurchase": days_since_purchase,
        "vipStatus": vip_status
    }
    
    try:
        # For local testing with Azure Functions Core Tools, use:
        # url = "http://localhost:7071/api/validateRefund"
        
        response = requests.post(FUNCTION_URL, json=payload, headers=headers)
        response.raise_for_status()
        
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling function: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None


def main():
    """Run example test cases"""
    
    print("Azure Function validateRefund - Example Usage")
    print("=" * 60)
    
    # Example test cases
    test_cases = [
        {
            "orderId": "ORD-001",
            "sku": "LAPTOP-PRO",
            "daysSincePurchase": 15,
            "vipStatus": False,
            "description": "Non-VIP customer, 15 days old"
        },
        {
            "orderId": "ORD-002",
            "sku": "PHONE-X",
            "daysSincePurchase": 45,
            "vipStatus": True,
            "description": "VIP customer, 45 days old"
        },
        {
            "orderId": "ORD-003",
            "sku": "TABLET-8",
            "daysSincePurchase": 90,
            "vipStatus": False,
            "description": "Non-VIP customer, 90 days old"
        },
    ]
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['description']}")
        print(f"Input: {json.dumps({k: v for k, v in test_case.items() if k != 'description'}, indent=2)}")
        
        result = validate_refund(
            test_case["orderId"],
            test_case["sku"],
            test_case["daysSincePurchase"],
            test_case["vipStatus"]
        )
        
        if result:
            print(f"Result: {json.dumps(result, indent=2)}")
        
        print("-" * 60)


if __name__ == "__main__":
    # Note: This script requires the 'requests' library
    # Install with: pip install requests
    
    try:
        import requests
        main()
    except ImportError:
        print("Error: This script requires the 'requests' library.")
        print("Install it with: pip install requests")
