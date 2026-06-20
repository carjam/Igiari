# Render Deployment Configuration

## Option 1: Using render.yaml (Recommended)
A `render.yaml` file is included at the repository root. Render will automatically detect and use it.

## Option 2: Manual Configuration
If not using render.yaml, configure these settings in Render dashboard:

### Service Type
Web Service

### Python Version
**CRITICAL**: Set Python version to **3.11.9** in the Render dashboard under "Settings" → "Environment" section, NOT 3.13 or 3.14

### Build Command
```bash
pip install -r requirements.txt
```

### Start Command
```bash
uvicorn server:app --host 0.0.0.0 --port $PORT
```

### Environment Variables
Add these in Render dashboard:
- `ANTHROPIC_API_KEY` = (your actual API key)
- `PYTHON_VERSION` = 3.11.9

### Root Directory
`backend`

### Region
Choose closest to your users (e.g., Oregon for US West)

### Instance Type
Free (or Starter $7/month for better performance)

### Auto-Deploy
Yes (deploys on git push)

## Troubleshooting
If you see "maturin" errors, Render is using Python 3.13+ which lacks pre-built wheels. Manually set Python 3.11.9 in Render dashboard settings.
