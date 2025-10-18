import logging
import json
import azure.functions as func


def calculate_refund_percentage(days_since_purchase: int, is_vip: bool) -> tuple[int, str, str]:
    """
    Calculate refund percentage based on business rules.
    
    Args:
        days_since_purchase: Number of days since purchase
        is_vip: Whether customer has VIP status
        
    Returns:
        Tuple of (refund_percentage, reason_code, message)
    """
    # Base refund percentage based on days since purchase
    if days_since_purchase <= 30:
        base_percentage = 100
        reason_code = "FULL_REFUND"
        message = "Full refund eligible (within 30 days)"
    elif days_since_purchase <= 60:
        base_percentage = 70
        reason_code = "PARTIAL_REFUND"
        message = "Partial refund eligible (31-60 days)"
    else:
        base_percentage = 0
        reason_code = "NO_REFUND"
        message = "No refund eligible (over 60 days)"
    
    # Apply VIP bonus
    if is_vip:
        base_percentage = min(base_percentage + 10, 100)  # Cap at 100%
        if base_percentage > 0:
            message += " + VIP bonus"
            reason_code += "_VIP"
    
    return base_percentage, reason_code, message


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP trigger for validating refund requests.
    
    Expects JSON payload with:
    - orderId: string
    - sku: string
    - daysSincePurchase: integer
    - vipStatus: boolean
    
    Returns JSON response with:
    - refundAmount: integer (percentage)
    - reasonCode: string
    - message: string
    """
    logging.info('validateRefund function processing a request.')

    try:
        # Parse request body
        req_body = req.get_json()
        if req_body is None:
            return func.HttpResponse(
                json.dumps({
                    "error": "Request body is empty or invalid JSON"
                }),
                status_code=400,
                mimetype="application/json"
            )
    except ValueError:
        return func.HttpResponse(
            json.dumps({
                "error": "Invalid JSON payload"
            }),
            status_code=400,
            mimetype="application/json"
        )

    # Validate required fields
    required_fields = ['orderId', 'sku', 'daysSincePurchase', 'vipStatus']
    missing_fields = [field for field in required_fields if field not in req_body]
    
    if missing_fields:
        return func.HttpResponse(
            json.dumps({
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }),
            status_code=400,
            mimetype="application/json"
        )

    # Extract values
    order_id = req_body['orderId']
    sku = req_body['sku']
    days_since_purchase = req_body['daysSincePurchase']
    vip_status = req_body['vipStatus']

    # Validate data types
    if not isinstance(days_since_purchase, int) or days_since_purchase < 0:
        return func.HttpResponse(
            json.dumps({
                "error": "daysSincePurchase must be a non-negative integer"
            }),
            status_code=400,
            mimetype="application/json"
        )

    if not isinstance(vip_status, bool):
        return func.HttpResponse(
            json.dumps({
                "error": "vipStatus must be a boolean"
            }),
            status_code=400,
            mimetype="application/json"
        )

    # Calculate refund
    refund_percentage, reason_code, message = calculate_refund_percentage(
        days_since_purchase, vip_status
    )

    # Prepare response
    response = {
        "orderId": order_id,
        "sku": sku,
        "refundAmount": refund_percentage,
        "reasonCode": reason_code,
        "message": message
    }

    logging.info(f'Refund calculated for order {order_id}: {refund_percentage}%')

    return func.HttpResponse(
        json.dumps(response),
        status_code=200,
        mimetype="application/json"
    )
