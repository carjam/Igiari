# Fallacy Scanner Backend

FastAPI server for detecting logical fallacies using Claude Haiku 4.5.

## Setup

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API key**:
   - Copy `.env.example` to `.env`
   - Add your Anthropic API key:
     ```
     ANTHROPIC_API_KEY=your_actual_api_key_here
     ```
   - **Never commit the `.env` file** (already in `.gitignore`)

## Running Locally

```bash
python server.py
```

Server runs on `http://localhost:8000`

API endpoint: `POST /api/scan`

## Testing

```bash
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Everyone I know loves this product, so it must be the best on the market."}'
```

## Rate Limiting

- 10 requests per IP per hour
- Enforced server-side for cost control

## Architecture Notes

- **Model**: Claude Haiku 4.5 (`claude-haiku-4-5-20251001`)
- **Input limit**: 4,000 characters
- **Rate limiting**: In-memory token bucket (resets on server restart)
- **Taxonomy**: 136 fallacies loaded at startup from `fallacy_reference/fallacies.json`
