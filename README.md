# Azure Function Demo with PowerApps

This repository contains an Azure Function with an HTTP trigger for validating refund requests, designed to integrate with PowerApps.

## Function: validateRefund

An HTTP-triggered Azure Function that calculates refund percentages based on business rules.

### Business Rules

The function calculates refund percentages based on the following criteria:

- **Days Since Purchase:**
  - ≤ 30 days: 100% refund
  - 31-60 days: 70% refund
  - \> 60 days: 0% refund

- **VIP Status:**
  - VIP customers receive an additional 10% bonus (capped at 100%)

### Request Format

**Endpoint:** `POST /api/validateRefund`

**Request Body (JSON):**
```json
{
  "orderId": "ORD-12345",
  "sku": "PROD-001",
  "daysSincePurchase": 45,
  "vipStatus": true
}
```

**Fields:**
- `orderId` (string, required): Unique order identifier
- `sku` (string, required): Product SKU
- `daysSincePurchase` (integer, required): Number of days since purchase (≥ 0)
- `vipStatus` (boolean, required): Customer VIP status

### Response Format

**Success Response (200 OK):**
```json
{
  "orderId": "ORD-12345",
  "sku": "PROD-001",
  "refundAmount": 80,
  "reasonCode": "PARTIAL_REFUND_VIP",
  "message": "Partial refund eligible (31-60 days) + VIP bonus"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Missing required fields: daysSincePurchase, vipStatus"
}
```

### Reason Codes

- `FULL_REFUND`: Full refund for non-VIP customers
- `FULL_REFUND_VIP`: Full refund for VIP customers
- `PARTIAL_REFUND`: Partial refund for non-VIP customers
- `PARTIAL_REFUND_VIP`: Partial refund for VIP customers
- `NO_REFUND`: No refund for non-VIP customers
- `NO_REFUND_VIP`: VIP bonus only (10%)

## Local Development

### Prerequisites

- Python 3.12+
- Azure Functions Core Tools (optional, for local testing)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/topnak/function-demo-with-powerapps.git
   cd function-demo-with-powerapps
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run tests:
   ```bash
   python -m pytest tests/ -v --cov=validateRefund
   ```

### Running Locally

If you have Azure Functions Core Tools installed:

```bash
func start
```

Then test with curl:
```bash
curl -X POST http://localhost:7071/api/validateRefund \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "ORD-12345",
    "sku": "PROD-001",
    "daysSincePurchase": 15,
    "vipStatus": false
  }'
```

## Testing

The project includes comprehensive unit tests covering:

- Refund percentage calculation for all day ranges
- VIP bonus application
- Edge cases (day 0, boundaries)
- Input validation
- Error handling

Run tests with coverage:
```bash
python -m pytest tests/ -v --cov=validateRefund --cov-report=term-missing
```

## Deployment to Azure

### Using GitHub Actions

The repository includes a GitHub Actions workflow (`.github/workflows/deploy-azure-function.yml`) that automatically:

1. Runs tests on every push to `main`
2. Deploys to Azure Functions

### Setup Steps:

1. **Create an Azure Function App:**
   - Go to Azure Portal
   - Create a new Function App (Python 3.12 runtime)
   - Note the function app name

2. **Get Publish Profile:**
   - In Azure Portal, go to your Function App
   - Click "Get publish profile" and download the file

3. **Configure GitHub Secrets:**
   - Go to your GitHub repository settings
   - Navigate to Secrets and Variables → Actions
   - Add a new secret: `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
   - Paste the contents of the publish profile file

4. **Update Workflow:**
   - Edit `.github/workflows/deploy-azure-function.yml`
   - Set `AZURE_FUNCTIONAPP_NAME` to your function app name

5. **Deploy:**
   - Push to `main` branch or manually trigger the workflow
   - The function will be built, tested, and deployed automatically

### Manual Deployment

Using Azure Functions Core Tools:

```bash
func azure functionapp publish <your-function-app-name>
```

## Integration with PowerApps

To use this function in PowerApps:

1. Get the function URL from Azure Portal (include the function key)
2. In PowerApps, add a custom connector or use the HTTP connector
3. Configure the POST request with the required JSON payload
4. Parse the response to display refund information

Example PowerApps formula:
```
Set(refundResult, 
  ParseJSON(
    HTTPPost(
      "https://<your-function-app>.azurewebsites.net/api/validateRefund?code=<function-key>",
      JSON({
        orderId: OrderIdInput.Text,
        sku: SKUInput.Text,
        daysSincePurchase: DaysInput.Value,
        vipStatus: VIPToggle.Value
      })
    )
  )
);
```

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── deploy-azure-function.yml  # GitHub Actions deployment workflow
├── validateRefund/
│   ├── __init__.py                   # Main function implementation
│   └── function.json                 # Function binding configuration
├── tests/
│   └── test_validate_refund.py       # Unit tests
├── host.json                         # Function app configuration
├── requirements.txt                  # Python dependencies
├── local.settings.json               # Local development settings
└── README.md                         # This file
```

## License

MIT
