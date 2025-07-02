# Sandboxed Code Runner

Secure Python code execution service using Flask and nsjail for safe sandboxing.

##  Quick Start

```bash
docker build -t sandboxed-code-runner .
docker run -p 8080:8080 sandboxed-code-runner
```

## 🧪 Live Testing

**Service URL**: `https://sandboxed-code-runner-havmgtbytq-uc.a.run.app`

### Automated Test Suite
```bash
python3 testscripts.py https://sandboxed-code-runner-havmgtbytq-uc.a.run.app
```

**Expected Output:**
```
Testing Sandboxed Code Runner at https://sandboxed-code-runner-havmgtbytq-uc.a.run.app
============================================================
1. Health Check ✅ PASSED
2. Basic Python Execution ✅ PASSED  
3. NumPy Integration ✅ PASSED
4. Pandas Integration ✅ PASSED
5. Stdout Capture ✅ PASSED
6. Error Handling - No main() Function ✅ PASSED
7. Error Handling - Runtime Error ✅ PASSED
8. JSON Response Validation ✅ PASSED
9. SciPy Integration ✅ PASSED
10. Input Validation - Large Script ✅ PASSED
11. Execution Speed ✅ PASSED
12. Multiple Library Imports ✅ PASSED
============================================================
TEST RESULTS: 12/12 tests passed
ALL TESTS PASSED! Service is working correctly.
```

### Manual Tests

**Health Check:**
```bash
curl https://sandboxed-code-runner-havmgtbytq-uc.a.run.app/health
# Expected: {"status":"healthy"}
```

**Basic Execution:**
```bash
curl -X POST https://sandboxed-code-runner-havmgtbytq-uc.a.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    return {\"message\": \"Hello World\", \"value\": 42}"}'
# Expected: {"result":{"message":"Hello World","value":42},"stdout":""}
```

**NumPy Test:**
```bash
curl -X POST https://sandboxed-code-runner-havmgtbytq-uc.a.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "import numpy as np\n\ndef main():\n    arr = np.array([1,2,3,4,5])\n    return {\"mean\": float(np.mean(arr)), \"sum\": int(np.sum(arr))}"}'
# Expected: {"result":{"mean":3.0,"sum":15},"stdout":""}
```

**Pandas Test:**
```bash
curl -X POST https://sandboxed-code-runner-havmgtbytq-uc.a.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "import pandas as pd\n\ndef main():\n    df = pd.DataFrame({\"x\": [1,2,3]})\n    return {\"sum\": int(df.x.sum())}"}'
# Expected: {"result":{"sum":6},"stdout":""}
```

**Stdout Capture:**
```bash
curl -X POST https://sandboxed-code-runner-havmgtbytq-uc.a.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    print(\"Processing...\")\n    result = 2 + 2\n    print(f\"Result: {result}\")\n    return {\"calculation\": result}"}'
# Expected: {"result":{"calculation":4},"stdout":"Processing...\nResult: 4\n"}
```

**Error Handling:**
```bash
curl -X POST https://sandboxed-code-runner-havmgtbytq-uc.a.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def not_main():\n    return 42"}'
# Expected: {"error":"Script must contain a 'main()' function"}
```

##  API

**POST /execute**
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

## ✅ Requirements Met

- ✅ **Flask + nsjail**: Secure sandboxed execution
- ✅ **Single docker run**: Simple local deployment
- ✅ **Input validation**: Script size and main() function checks
- ✅ **Safe execution**: 30s timeout, 300MB memory limit, network isolation
- ✅ **Library support**: numpy, pandas, scipy, matplotlib
- ✅ **Cloud Run deployment**: Live service with examples above

## Security

- nsjail process isolation
- 30s execution timeout
- 300MB memory limit
- Network isolation
- Input validation

## Libraries

numpy, pandas, scipy, matplotlib, requests

---
