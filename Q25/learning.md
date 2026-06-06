# Deploying a FastAPI POST Endpoint on Vercel (TDS Assignment Notes)

## Assignment Goal

Deploy a serverless FastAPI endpoint on Vercel that:

* Accepts POST requests
* Reads telemetry data from a JSON file
* Calculates:

  * avg_latency
  * p95_latency
  * avg_uptime
  * breaches
* Supports CORS from any origin
* Returns results in the format expected by the grader

---

# 1. Understanding Serverless

Traditional hosting:

```text
Machine runs 24/7
```

Serverless hosting:

```text
Function runs only when called
```

Examples:

* Contact form
* API endpoint
* Webhook
* Image processing
* Small dashboards

Vercel automatically:

* Creates temporary instances
* Scales automatically
* Stops instances after requests finish

---

# 2. Required Project Structure

Final structure:

```text
Q25/
├── api/
│   └── index.py
├── q-vercel-latency.json
├── requirements.txt
└── vercel.json
```

---

# 3. Creating a Clean Python Environment in WSL

Deactivate any broken environment:

```bash
deactivate
```

Check system Python:

```bash
which python3
which pip
```

Create project venv:

```bash
cd ~/TDS/GA0/Q25

python3 -m venv .venv
```

Activate:

```bash
source .venv/bin/activate
```

Verify:

```bash
which python
which pip
```

Expected:

```text
.../Q25/.venv/bin/python
.../Q25/.venv/bin/pip
```

---

# 4. Installing Dependencies

Install packages:

```bash
pip install fastapi numpy
```

Verify:

```bash
pip list | grep -E "fastapi|numpy"
```

---

# 5. requirements.txt

Create:

```text
fastapi
numpy
```

Vercel installs these automatically during deployment.

---

# 6. vercel.json

Create:

```json
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

Purpose:

```text
All incoming requests
→ api/index.py
```

---

# 7. Reading JSON Data

File:

```text
q-vercel-latency.json
```

Load it:

```python
DATA_FILE = Path(__file__).parent.parent / "q-vercel-latency.json"

with open(DATA_FILE, "r") as f:
    telemetry = json.load(f)
```

Why?

```python
__file__
```

works reliably both locally and on Vercel.

---

# 8. Metrics Required

Input:

```json
{
  "regions": ["apac", "emea"],
  "threshold_ms": 155
}
```

For each region:

### Average latency

```python
sum(latencies) / len(latencies)
```

---

### 95th percentile

```python
np.percentile(latencies, 95)
```

---

### Average uptime

```python
sum(uptimes) / len(uptimes)
```

---

### Breaches

Count values above threshold:

```python
sum(
    1 for x in latencies
    if x > threshold
)
```

---

# 9. Git Setup

Problem encountered:

```text
Author identity unknown
```

Fix:

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

Check:

```bash
git config --global --list
```

---

# 10. GitHub Email Privacy Error

Error:

```text
GH007: Your push would publish a private email address
```

Fix:

GitHub →

Settings →

Emails →

Enable:

```text
Keep my email addresses private
```

Use GitHub noreply email:

```bash
git config --global user.email "123456+username@users.noreply.github.com"
```

---

# 11. Important: Do NOT Commit .venv

Accidentally committed:

```text
.venv/
```

Bad because:

* Thousands of files
* Huge repository
* Not needed

Create:

```bash
nano .gitignore
```

Contents:

```text
.venv/
__pycache__/
*.pyc
```

Remove from Git:

```bash
git rm -r --cached .venv
```

Commit again.

---

# 12. Vercel CLI Setup

Install if needed:

```bash
npm install -g vercel
```

Deploy:

```bash
vercel
```

Production:

```bash
vercel --prod
```

---

# 13. WSL + Vercel Problem

Error:

```text
CMD.EXE was started...
UNC paths are not supported
```

Reason:

Vercel CLI launched from Windows instead of WSL.

Fix:

Use:

```bash
npx vercel
```

inside WSL project folder.

---

# 14. Understanding URLs

Vercel gives:

### Production URL

```text
https://project.vercel.app
```

Stable.

Use this for submission.

---

### Preview URL

```text
https://project-xyz-user.vercel.app
```

Changes every deployment.

Do NOT submit.

---

# 15. CORS Problem

Initial grader error:

```text
Enable CORS with Access-Control-Allow-Origin: *
```

Even though API worked.

---

## What finally fixed it

Explicit headers:

```python
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Expose-Headers": "Access-Control-Allow-Origin",
}
```

Middleware:

```python
@app.middleware("http")
```

Options handler:

```python
@app.options("/{path:path}")
```

---

# 16. Testing CORS

OPTIONS:

```bash
curl -i -X OPTIONS \
https://your-app.vercel.app/api/latency \
-H "Origin: https://example.com" \
-H "Access-Control-Request-Method: POST"
```

Must contain:

```text
Access-Control-Allow-Origin: *
```

---

POST:

```bash
curl -i -X POST \
https://your-app.vercel.app/api/latency \
-H "Origin: https://example.com" \
-H "Content-Type: application/json" \
-d '{"regions":["apac"],"threshold_ms":155}'
```

---

# 17. Final Grader Error

After fixing CORS:

```text
Response should include a regions array or object
```

Meaning:

CORS passed.

Response format was wrong.

---

# 18. Final Response Format

Wrong:

```json
{
  "apac": {...},
  "emea": {...}
}
```

Expected:

```json
{
  "regions": [
    {
      "region": "apac",
      ...
    },
    {
      "region": "emea",
      ...
    }
  ]
}
```

Lesson:

Grader messages are not always the real root cause.

Fix one error at a time.

---

# 19. Debugging Strategy Learned

Always test:

### Local syntax

```bash
python -m py_compile api/index.py
```

---

### API manually

```bash
curl
```

---

### Headers

```bash
curl -i
```

---

### Preflight

```bash
curl -X OPTIONS
```

---

### Git status

```bash
git status
```

---

### Deployment

```bash
git push
```

---

### Verify live endpoint

Never trust deployment blindly.

Always test the deployed URL.

---

# Key Lessons

1. Use WSL virtual environments correctly.
2. Never commit `.venv`.
3. Vercel only installs from `requirements.txt`.
4. Test endpoints using curl.
5. CORS needs OPTIONS support.
6. Browser-based graders may require exposed headers.
7. Production URL is the submission URL.
8. Grader error messages can be misleading.
9. Always inspect actual HTTP headers.
10. Fix one issue at a time and retest.

```
```
