# 🚀 Deploying BudgetMart on Render

Your project is now 100% ready for production deployment. Follow these steps to host it for free on Render.com.

## Step 1: Push to GitHub
If you haven't already, push your code to a GitHub repository:
1. `git init`
2. `git add .`
3. `git commit -m "Initial commit"`
4. Push to your GitHub repo.

---

## Step 2: Deploy the Backend (Python/Flask)
1. Go to your [Render Dashboard](https://dashboard.render.com/) and click **New > Web Service**.
2. Connect your GitHub repository.
3. Use the following settings:
   - **Name:** `budgetmart-backend` (or whatever you prefer)
   - **Environment:** `Python 3`
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app` (this replaces the default block)
   - **Instance Type:** Free
4. Scroll down to **Environment Variables** and click Add Environment Variable:
   - **Key:** `SERPAPI_KEY`
   - **Value:** `0f91d9e6d9f61409ef5b5ebf23dda580ad4f4feaed63e3ed5252590164228995`
5. Click **Create Web Service**. 
6. Wait for it to deploy and copy the generated URL (e.g., `https://budgetmart-backend.onrender.com`).

---

## Step 3: Deploy the Frontend (HTML/JS/CSS)
1. In `frontend/script.js`, currently lines 14-16 look like this:
   ```javascript
   const API_URL = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost' 
       ? 'http://127.0.0.1:5000' 
       : 'https://budgetmart-backend.onrender.com';
   ```
   **If your Render backend URL is different**, edit `script.js` to replace `'https://budgetmart-backend.onrender.com'` with your actual backend URL. Commit and push again.

2. Go to your [Render Dashboard](https://dashboard.render.com/) and click **New > Static Site**.
3. Connect the SAME GitHub repository.
4. Use the following settings:
   - **Name:** `budgetmart-frontend`
   - **Root Directory:** `frontend`
   - **Build Command:** *(Leave Blank)*
   - **Publish Directory:** `.` (just a period, meaning current folder)
5. Click **Create Static Site**.
6. Done! Render will give you a live URL for your functional website.
