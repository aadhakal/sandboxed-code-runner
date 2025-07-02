# Sandboxed Code Runner

A secure Python code execution service using Flask and nsjail for safe sandboxing. Executes arbitrary Python code in isolated containers with strict resource limits.

## Quick Start

**Run locally:**
```bash
docker build -t sandboxed-code-runner .
docker run -p 8080:8080 sandboxed-code-runner
```

**Deploy to Cloud Run:**
```bash
gcloud run deploy sandboxed-code-runner --source . --platform managed --allow-unauthenticated --region us-central1
```

## 📋 API Reference

### Execute Python Code
**Endpoint:** `POST /execute`

**Request:**
```json
{
  "script": "def main():\n    return {'result': 42}"
}
```

**Response:**
```json
{
  "result": {"result": 42},
  "stdout": ""
}
```

### Health Check
**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy"
}
```

## Example Requests

Replace `https://sandboxed-code-runner-123456789-uc.a.run.app` with your actual Cloud Run URL:

### Basic Example
```bash
curl -X POST https://sandboxed-code-runner-123456789-uc.a.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    return {\"message\": \"Hello from Cloud Run!\", \"value\": 42}"}'
```

### NumPy Example
```bash
curl -X POST https://sandboxed-code-runner-123456789-uc.a.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "import numpy as np\n\ndef main():\n    arr = np.array([1,2,3,4,5])\n    return {\"mean\": float(np.mean(arr)), \"sum\": int(np.sum(arr)), \"std\": float(np.std(arr))}"}'
```

### Pandas Example
```bash
curl -X POST https://sandboxed-code-runner-123456789-uc.a.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "import pandas as pd\n\ndef main():\n    df = pd.DataFrame({\"name\": [\"Alice\", \"Bob\", \"Charlie\"], \"age\": [25, 30, 35]})\n    return {\"shape\": list(df.shape), \"mean_age\": float(df.age.mean()), \"names\": df.name.tolist()}"}'
```

### Stdout Capture Example
```bash
curl -X POST https://sandboxed-code-runner-123456789-uc.a.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    print(\"Starting calculation...\")\n    result = sum(range(100))\n    print(f\"Sum of 0-99: {result}\")\n    print(\"Calculation complete!\")\n    return {\"sum\": result, \"count\": 100}"}'
```

## 🔒 Security Features

- **nsjail Sandboxing**: Complete process isolation with restricted system access
- **Resource Limits**: 30-second timeout, 300MB memory, 10MB file size limits  
- **Network Isolation**: No external network access from executed code
- **Filesystem Restrictions**: Read-only access to system files, limited write access
- **Input Validation**: Script size limits (50KB), required main() function

## 📚 Supported Libraries

- **Data Science**: numpy, pandas, scipy, scikit-learn
- **Visualization**: matplotlib, seaborn  
- **Web**: requests (limited due to network isolation)
- **Standard Library**: All Python 3.11 standard library modules

## ⚙️ Configuration

### Resource Limits
- **Execution Time**: 30 seconds maximum
- **Memory**: 300MB limit
- **File Size**: 10MB output limit  
- **Script Size**: 50KB input limit

### Requirements
- Script must contain `def main():` function
- Function must return JSON-serializable data
- No persistent state between requests

## Deployment

### Local Development
```bash
# Build and run
docker build -t sandboxed-code-runner .
docker run -p 8080:8080 sandboxed-code-runner

# Test
curl http://localhost:8080/health
```

### Google Cloud Run
```bash
# Deploy from source
gcloud run deploy sandboxed-code-runner \
  --source . \
  --platform managed \
  --allow-unauthenticated \
  --region us-central1

# Deploy from GitHub
gcloud run deploy sandboxed-code-runner \
  --source https://github.com/USERNAME/REPO \
  --platform managed \
  --allow-unauthenticated \
  --region us-central1
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
# Test locally
python3 test_service.py http://localhost:8080

# Test Cloud Run deployment
python3 test_service.py https://YOUR-CLOUD-RUN-URL
```

## 🏥 Health Monitoring

```bash
# Health check
curl https://your-cloud-run-url/health

# View logs
gcloud run services logs read sandboxed-code-runner --region=us-central1
```

##  Troubleshooting

### Common Issues

- **"Script must contain a 'main()' function"**: Ensure your script defines `def main():` exactly
- **"Script execution timed out"**: Optimize code or reduce complexity (30s limit)
- **"Invalid script size"**: Keep scripts under 50KB
- **Library import errors**: Use only included libraries

## Example Responses

**Success:**
```json
{
  "result": {"calculation": 4950, "message": "success"},
  "stdout": "Processing data...\nCalculation complete!\n"
}
```

**Error:**
```json
{
  "error": "Script execution timed out (30s limit)"
}
```

## 🎯 Architecture

```
User Request → Flask API → Input Validation → nsjail Sandbox → Python Execution → JSON Response
```

## 📝 License

This project is provided for educational and demonstration purposes.

---

**Replace the example Cloud Run URL with your actual deployment URL for testing.**
