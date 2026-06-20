# Render Deployment Configuration

## Service Type
Web Service

## Build Command
```bash
pip install -r requirements.txt
```

## Start Command
```bash
uvicorn server:app --host 0.0.0.0 --port $PORT
```

## Environment Variables
Add these in Render dashboard:
- `ANTHROPIC_API_KEY` = (your actual API key)
- `PYTHON_VERSION` = 3.11.9

## Root Directory
`backend`

## Region
Choose closest to your users (e.g., Oregon for US West)

## Instance Type
Free (or Starter $7/month for better performance)

## Auto-Deploy
Yes (deploys on git push)
