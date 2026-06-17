# Deploy to Vercel

## One-Click Deploy

1. Push this repo to GitHub
2. Go to [vercel.com/new](https://vercel.com/new)
3. Import the repository
4. Set **Root Directory** to `web`
5. Click **Deploy**

Vercel will auto-detect Next.js and run `npm run build`. The site is exported as static HTML (`output: "export"`).

## Update Financial Data

Before deploying (or when you want fresh numbers), run locally:

```bash
pip install -r requirements.txt
python scripts/export_for_web.py
```

This updates:
- `web/public/data/analysis.json` — dashboard data
- `web/data/analysis.json` — bundled for Next.js import
- `web/public/charts/*.png` — chart images

Then commit and push. Vercel will rebuild automatically.

## Local Development

Requires Node.js 18+:

```bash
cd web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Project Settings (Vercel Dashboard)

| Setting | Value |
|---------|-------|
| Root Directory | `web` |
| Framework Preset | Next.js |
| Build Command | `npm run build` (default) |
| Output Directory | *(leave empty — use default)* |
| Install Command | `npm install` (default) |

> Do **not** set Output Directory to `out`. Vercel deploys Next.js from `.next` automatically.

## Troubleshooting

### Build fails: `Module not found: Can't resolve '@/lib/data'`

**Cause:** Python `.gitignore` template includes `lib/`, which blocks `web/lib/` from being pushed to GitHub.

**Fix:**
1. Ensure `.gitignore` uses `/lib/` (root only) and includes `!web/lib/`
2. In GitHub Desktop you should now see these files to commit:
   - `web/lib/data.ts`
   - `web/lib/types.ts`
   - `web/lib/format.ts`
   - `.gitignore`
3. Commit → Push origin → Vercel will redeploy automatically

### Build fails: `routes-manifest.json couldn't be found`

**Cause:** `output: "export"` in `next.config.js` plus Output Directory set to `out` in Vercel conflicts with native Next.js deployment.

**Fix:** Use default Vercel Next.js settings (no custom Output Directory). The project config has been updated — commit and push, then in Vercel go to **Settings → General → Build & Development Settings** and clear the **Output Directory** field if it says `out`.

### Charts not showing on the live site

Run `python scripts/export_for_web.py` locally, then commit and push `web/public/charts/`.


After deploy, share your live URL:

> Built an interactive Financial Analysis dashboard for Tesla (TSLA) — live at [your-url].vercel.app
>
> P&L · Budgeting · Forecasting · Sensitivity Analysis
>
> #FinancialAnalysis #Python #DataAnalytics #Vercel
