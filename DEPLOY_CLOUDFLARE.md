# Cloudflare Pages Deployment

## Quick Setup
1. Go to Cloudflare Dashboard → Workers & Pages → Create application → Pages
2. Connect GitHub repo: `carjam/Igiari`
3. Configure deployment:
   - **Project name:** `igiari` (or your choice)
   - **Build command:** (leave empty)
   - **Deploy/Output directory:** (leave empty or set to `/`)
   - **Branch:** `master`
4. Click "Save and Deploy"

## Notes
- Frontend files (index.html, app.js, styles.css) are in the repository root
- No build step needed - pure static HTML/CSS/JS
- API URL is already configured to point to: `https://igiari-backend.onrender.com`

## Custom Domain (Optional)
Add after deployment if desired
