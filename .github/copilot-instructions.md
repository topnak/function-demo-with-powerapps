# Copilot Instructions for function-demo-with-powerapps

## Project Overview

This repository contains an Azure Function with an HTTP trigger (`validateRefund`) designed to validate refund requests and integrate with PowerApps. The function calculates refund percentages based on business rules considering days since purchase and VIP status.

## Technology Stack

- **Language**: Python 3.12+
- **Framework**: Azure Functions (Python)
- **Testing**: pytest with coverage reporting
- **Deployment**: GitHub Actions to Azure Functions
- **Key Dependencies**: 
  - `azure-functions` - Azure Functions runtime
  - `pytest` - Testing framework
  - `pytest-cov` - Coverage reporting

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── deploy-azure-function.yml  # CI/CD pipeline
├── validateRefund/
│   ├── __init__.py                   # Main function implementation
│   └── function.json                 # Function binding configuration
├── tests/
│   └── test_validate_refund.py       # Unit tests
├── host.json                         # Function app configuration
├── requirements.txt                  # Python dependencies
└── README.md                         # Documentation
```

## How to Build and Test

### Initial Setup
```bash
# Install dependencies
pip install -r requirements.txt
```

### Running Tests
```bash
# Run all tests with coverage
python -m pytest tests/ -v --cov=validateRefund --cov-report=term-missing

# Run specific test class
python -m pytest tests/test_validate_refund.py::TestCalculateRefundPercentage -v

# Run specific test
python -m pytest tests/test_validate_refund.py::TestCalculateRefundPercentage::test_vip_bonus_31_to_60_days -v
```

### Local Development
```bash
# If Azure Functions Core Tools is installed
func start

# Test the endpoint
curl -X POST http://localhost:7071/api/validateRefund \
  -H "Content-Type: application/json" \
  -d '{"orderId": "ORD-12345", "sku": "PROD-001", "daysSincePurchase": 15, "vipStatus": false}'
```

## Business Logic

### Refund Calculation Rules
The `calculate_refund_percentage` function implements these rules:
- **Days ≤ 30**: 100% refund (FULL_REFUND)
- **Days 31-60**: 70% refund (PARTIAL_REFUND)
- **Days > 60**: 0% refund (NO_REFUND)
- **VIP Bonus**: +10% (capped at 100%), appends "_VIP" to reason code

### API Contract
**Request**: POST `/api/validateRefund`
```json
{
  "orderId": "string (required)",
  "sku": "string (required)",
  "daysSincePurchase": "integer >= 0 (required)",
  "vipStatus": "boolean (required)"
}
```

**Response**: 200 OK
```json
{
  "orderId": "string",
  "sku": "string",
  "refundAmount": "integer (0-100)",
  "reasonCode": "string",
  "message": "string"
}
```

**Error Response**: 400 Bad Request
```json
{
  "error": "string"
}
```

## Coding Conventions

### Python Style
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return types
- Write docstrings for all functions using Google-style format
- Keep functions focused and single-purpose

### Testing Standards
- Write unit tests for all new functions
- Maintain test coverage above 95%
- Test both success and error cases
- Include edge case tests (boundaries, zero values, etc.)
- Use descriptive test names that explain what is being tested
- Follow the existing test structure in `test_validate_refund.py`

### Error Handling
- Return appropriate HTTP status codes (200 for success, 400 for client errors)
- Provide clear error messages in JSON format
- Validate all input data types and ranges
- Log important events and errors using the `logging` module

## Azure Functions Specific Guidelines

### Function Structure
- Keep the main function handler in `__init__.py`
- Use `function.json` for binding configuration (already configured)
- Return `func.HttpResponse` objects with proper status codes and JSON content
- Set `mimetype="application/json"` for JSON responses

### Logging
```python
import logging
logging.info('Informational message')
logging.error('Error message')
```

### Request Handling
```python
# Parse JSON body
req_body = req.get_json()

# Return JSON response
return func.HttpResponse(
    json.dumps(response_data),
    status_code=200,
    mimetype="application/json"
)
```

## Deployment

### CI/CD Pipeline
The repository uses GitHub Actions for automated deployment:
1. **Build & Test**: Runs on every push to `main`
   - Installs dependencies
   - Runs pytest with coverage
   - Uploads test results
2. **Deploy**: Deploys to Azure Functions after successful tests
   - Requires `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` secret
   - Set `AZURE_FUNCTIONAPP_NAME` in workflow file

### Manual Deployment
```bash
func azure functionapp publish <your-function-app-name>
```

## Common Tasks

### Adding a New Function
1. Create new directory under root (e.g., `newFunction/`)
2. Add `__init__.py` with the function handler
3. Add `function.json` with binding configuration
4. Write comprehensive unit tests
5. Update README.md with function documentation
6. Ensure tests pass before committing

### Modifying Business Logic
1. Update the logic in `validateRefund/__init__.py`
2. Add/update corresponding tests in `tests/test_validate_refund.py`
3. Run tests to ensure coverage remains high
4. Update README.md if API contract changes

### Updating Dependencies
1. Modify `requirements.txt`
2. Run `pip install -r requirements.txt`
3. Run all tests to ensure compatibility
4. Update documentation if needed

## Important Notes

- **Never commit secrets**: Use GitHub Secrets for sensitive data
- **Maintain test coverage**: Aim for >95% coverage on all code
- **Type safety**: Always validate input data types and ranges
- **JSON responses**: All responses must be valid JSON with appropriate mimetype
- **Error messages**: Provide clear, actionable error messages
- **Business rules**: Do not modify refund calculation rules without proper review
- **API compatibility**: Maintain backward compatibility for PowerApps integration

## When Making Changes

1. Run tests before and after changes: `python -m pytest tests/ -v --cov=validateRefund`
2. Ensure all tests pass and coverage remains high
3. Update documentation if adding new features or changing behavior
4. Follow existing code patterns and conventions
5. Test locally if possible using Azure Functions Core Tools
6. Review the README.md for context before making significant changes
