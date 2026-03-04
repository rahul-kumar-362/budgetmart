# 🚀 Deploying BudgetMart on Vercel

Since Render now requires a credit card, we will use **Vercel** instead! Vercel is incredibly fast, completely free, and does **not** require a credit card for GitHub signups. 

We will deploy both the Frontend and the Backend to Vercel at the same time.

## Step 1: Push to GitHub
I have already re-configured your files for Vercel. You just need to push them:
1. Open your terminal in VS Code (or PowerShell).
2. Run: `git add .`
3. Run: `git commit -m "Configure for Vercel deployment"`
4. Run: `git push origin main`

---

## Step 2: Deploy to Vercel
1. Go to [Vercel.com](https://v                                                                         ercel.com/) and sign up/log in using your **GitHub account**.
2. Click the black **Add New...** button and select **Project**.
3. You will see a list of your GitHub repositories. Find `budgetmart` and click **Import**.

### Step 3: Configure Settings
On the project configuration page, make the following precise changes:

1. **Framework Preset:** Leave as `Other`.
2. **Root Directory:** Click "Edit", select the `backend` folder, and save.
   *(We deploy the backend first, then we will deploy the frontend separately).*
3. **Environment Variables:** 
   - Expand this section.
   - **Name:** `SERPAPI_KEY`
   - **Value:** `YOUR_SERPAPI_KEY_HERE` (Get a new one from your SerpApi dashboard!)
   - Click **Add**.
4. Click the big **Deploy** button.

---

### Step 4: Link Frontend to the Deployed Backend
1. Once Vercel finishes deploying the backend, it will give you a domain (e.g., `https://budgetmart-backend-something.vercel.app`). **Copy that URL.**
2. Open your local `frontend/script.js` file.
3. Replace the placeholder URL with your actual Vercel backend URL:
   ```javascript
   const API_URL = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost' 
       ? 'http://127.0.0.1:5000' 
       : 'https://YOUR_NEW_VERCEL_BACKEND_URL.vercel.app'; // <--- PASTE HERE
   ```
4. Save the file, commit, and push again:
   - `git add frontend/script.js`
   - `git commit -m "Update API URL for prod"`
   - `git push origin main`

### Step 5: Deploy the Frontend
1. Go back to your Vercel Dashboard and click **Add New... > Project** again.
2. Import the `budgetmart` repository again.
3. This time, change the **Root Directory** to `frontend`.
4. Click **Deploy**.

**You're done!** Vercel will give you a new link for the frontend, and your full-stack app will be live and communicating perfectly without requiring any credit cards.
