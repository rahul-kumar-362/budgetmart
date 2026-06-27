# 🚀 Deploying BudgetMart on Vercel

Both the frontend and backend deploy from this single repo as **two separate
Vercel projects** (different root directories). No credit card required.

## 1. Push to GitHub
```bash
git add .
git commit -m "Deploy BudgetMart"
git push origin main
```

## 2. Deploy the backend
1. Go to [vercel.com](https://vercel.com/) and log in with GitHub.
2. **Add New… → Project**, import the `budgetmart` repo.
3. **Root Directory:** click *Edit* and select **`backend`**.
4. **Environment Variables** (all optional — without them the API runs in demo mode):
   | Name | Value |
   |------|-------|
   | `SERPAPI_KEY` | your SerpApi key (enables live prices) |
   | `REDIS_URL` | Upstash Redis URL (persistent cache) |
   | `DATABASE_URL` | Postgres URL (enables `/history`) |
   | `ALLOWED_ORIGINS` | `https://<your-frontend>.vercel.app` |
5. **Deploy.** Vercel detects `@vercel/python` from `vercel.json` and wraps the
   Flask `app` in `api/index.py`. Note the backend URL it gives you.

> Python version: Vercel's `@vercel/python` defaults to Python 3.12. Set the
> version in *Project Settings → General* if you need to pin it.

## 3. Point the frontend at the backend
The production backend URL lives in **one constant** in `frontend/src/main.ts`:
```ts
const PROD_API_BASE = "https://budgetmart-backend.vercel.app";
```
Update it to your backend URL, then rebuild and commit:
```bash
cd frontend
npm run build          # regenerates dist/main.js
git add src/main.ts dist/main.js
git commit -m "Point frontend at deployed backend"
git push
```

## 4. Deploy the frontend
1. **Add New… → Project**, import the same repo again.
2. **Root Directory:** **`frontend`**.
3. **Build Command:** `npm run build` · **Output Directory:** leave default
   (the static files, including `dist/`, are served as-is).
   *(`dist/main.js` is committed, so this works even with no build step.)*
4. **Deploy.**

Done — the frontend calls the backend across origins; `ALLOWED_ORIGINS` on the
backend should list the frontend domain.
