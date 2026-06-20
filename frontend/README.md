# Fallacy Scanner Frontend

Vanilla HTML/CSS/JavaScript frontend for the Igiari fallacy scanner.

## Design

Based on `specs/02_design_direction.md`:
- **Theme**: Rhetoric/argumentation tool, not generic AI interface
- **Visual language**: Copyeditor's marks, red pen annotations, paper-like feel
- **Colors**: Warm off-white (#FAF8F3), soft black text, muted brick red accent
- **Typography**: Serif for user content, monospace for UI labels
- **Layout**: Single centered column with in-place transformation

## Features

✅ **F1-F9 Requirements** (from `specs/01_product_requirements.md`):
- F1: Text input area (textarea)
- F2: Scan button (disabled during processing)
- F3: Highlighted fallacious spans (wavy red underline)
- F4: Hover tooltips showing fallacy name + explanation
- F5: 4000 character limit with counter
- F6: Loading state ("Reading closely…")
- F7: Empty/error states (distinct visuals)
- F8: "Try an Example" button (pre-fills eval_002 - Straw Man)
- F9: Rate limiting handled by backend

## Running Locally

No build step required - just open in a browser:

1. **Option A: Simple file server**
   ```bash
   cd frontend
   python -m http.server 8080
   ```
   Open `http://localhost:8080`

2. **Option B: Live Server (VS Code)**
   - Install "Live Server" extension
   - Right-click `index.html` → "Open with Live Server"

3. **Option C: Direct file**
   ```bash
   open index.html  # macOS
   start index.html # Windows
   ```

## Configuration

**Backend URL**: Update `API_URL` in `app.js` when deploying:
```javascript
const API_URL = 'https://your-backend.com/api/scan';
```

For local development, it defaults to `http://localhost:8000/api/scan`.

## Testing Checklist (Phase 3 Acceptance Criteria)

- [ ] Click "Try an Example" → text loads
- [ ] Click "Scan" → results appear within ~10 seconds
- [ ] Hover over highlighted text → tooltip appears
- [ ] Paste >4000 chars → counter shows warning
- [ ] Scan empty text → clear error message
- [ ] Kill backend, try scan → clear error state
- [ ] Test on mobile (~375px width) → layout doesn't break

## File Structure

```
frontend/
├── index.html    # Main page structure
├── styles.css    # Design system + components
├── app.js        # Client-side logic + API calls
└── README.md     # This file
```

No dependencies, no build process, no framework.
