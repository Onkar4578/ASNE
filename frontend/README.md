# ASNE Frontend

A minimal React dashboard for ASNE. It sends user queries to the backend API and displays the returned answer with routing metadata.

## Setup

1. Install dependencies:
   ```bash
   cd asne/frontend
   npm install
   ```

2. Set the API endpoint:
   ```bash
   export REACT_APP_ASNE_API_URL="https://your-backend-url/query"
   ```
   On Windows PowerShell:
   ```powershell
   $env:REACT_APP_ASNE_API_URL = "https://your-backend-url/query"
   ```

3. Run locally:
   ```bash
   npm start
   ```

4. Build for deployment:
   ```bash
   npm run build
   ```

## Deploy to Vercel

1. Add this repo to Vercel.
2. Set the environment variable `REACT_APP_ASNE_API_URL` to your deployed backend URL.
3. Deploy.
