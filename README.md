---
title: ASNE Adaptive Symbolic-Neural Engine
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# ASNE — Adaptive Symbolic-Neural Engine

A cost-aware hybrid AI query router. Routes queries through free layers
first (rules, cache, a fast hosted model) and only escalates to a
premium model when confidence is too low — and it **works the same way
on your laptop and after deploying it online.**

## Architecture

```
Query
  -> Rule Engine        (instant, free — regex patterns)
  -> Semantic Cache     (instant, free — TF-IDF similarity, no GPU needed)
  -> Domain Classifier  (detects SPPU-subject vs general queries)
  -> Fast Tier Model    (Groq's free hosted API — Llama 3.1 8B, self-rates its confidence)
  -> Confidence Check   (escalate only if confidence is low)
  -> Escalation Tier    (Claude, if you add a paid key -- OR a bigger free
                         Groq model automatically, if you don't)
```

### Why no Ollama / local GPU model
An earlier version of this used Ollama running a model directly on your
machine. That only works on hardware you control — free hosting tiers
(Render, Railway, etc.) don't have the RAM or a persistent process for
it, so it would break immediately after deployment. Using Groq's hosted
free API for the "fast tier" instead means:
- Zero cost (Groq's free tier is generous for a project like this)
- Zero GPU/RAM burden on your side, laptop or server
- **Identical behavior locally and once deployed** — no separate "demo version"

This is still an honest hybrid-routing story: most queries get resolved
by rules, cache, or the free fast tier; only the hardest queries reach
the paid/premium tier. The cost savings you measure are real.

## Setup — runs identically on your laptop or a server

### 1. Get a free Groq API key
Sign up at https://console.groq.com — free tier, no card required for
the base limits. This powers Levels 3 and (as fallback) Level 4.

### 2. (Optional) Get an Anthropic API key
Only needed if you want Level 4 to use real Claude instead of the free
Groq fallback — useful if you want to demonstrate genuine "paid tier"
cost numbers in your benchmark. Skip this and the app still works fully
for free.

### 3. Install dependencies
```bash
cd asne
python3 -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Set environment variables
```bash
export GROQ_API_KEY="your-groq-key-here"
export ANTHROPIC_API_KEY="your-claude-key-here"   # optional
```

### 5. Run the server
```bash
uvicorn app.main:app --reload
```
Server runs at http://localhost:8000

### 6. Test it
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "define oop"}'
```

### 7. Run the benchmark
```bash
python benchmark.py
```
Reports total cost, route distribution, and % of queries resolved for
free vs. escalated.

## Deploying it live

### Option A (recommended): Hugging Face Spaces — backend
Best fit for an AI project: 16GB RAM free, no credit card, 48-hour sleep
window (vs Render's 15 min), and it visibly signals "AI project" on your
resume/portfolio link.

1. Create a free account at https://huggingface.co
2. Click **New Space** → choose **Docker** as the SDK → name it `asne`
3. Push this project's files to the Space's git repo (HF gives you the
   git remote URL on the Space's page):
   ```bash
   git init
   git remote add hf https://huggingface.co/spaces/<your-username>/asne
   git add .
   git commit -m "Initial ASNE deployment"
   git push hf main
   ```
4. In the Space's **Settings → Repository secrets**, add:
   - `GROQ_API_KEY` (required)
   - `ANTHROPIC_API_KEY` (optional)
5. The Space builds automatically from the `Dockerfile` and goes live at
   `https://<your-username>-asne.hf.space`

### Option B: Render (backup)
1. Push this project to a GitHub repo
2. Create a new Web Service on Render, connect the repo
3. Render auto-detects `Procfile` and `runtime.txt` — no extra config needed
4. Add environment variables `GROQ_API_KEY` (and `ANTHROPIC_API_KEY` if using it)
   in Render's dashboard under Environment
5. Deploy — you'll get a live URL like `https://asne-xxxx.onrender.com`

**Note on free-tier sleep:** Render sleeps after ~15 min idle (~30-60s
wake time on next request). Hugging Face Spaces sleeps after ~48 hours
idle — far less likely to catch a recruiter cold. Mention this honestly
if anyone tries your link after a long gap either way; it's a known
free-tier tradeoff, not a bug.

### Frontend (Vercel), once you build the dashboard
1. Point the dashboard's API calls at your HF Space or Render URL
2. Deploy the frontend folder to Vercel
3. You now have a live, clickable link for your resume/portfolio

## Next steps
- [ ] Expand `SPPU_SEEDS` in `app/core/domain_classifier.py` using real
      topics from your SPPU PYQ PDFs
- [ ] Add more rules to `app/core/rule_engine.py` as you discover
      repeated query patterns during testing
- [ ] Build a simple React or plain HTML dashboard showing live routing
      decisions (route, confidence, latency, cost per query)
- [ ] Tune `SIMILARITY_THRESHOLD`, `DOMAIN_THRESHOLD`, and
      `CONFIDENCE_ESCALATION_THRESHOLD` based on real test results
- [ ] Swap `cache_store.json` for a free Render Postgres/Redis instance
      if you want the cache to survive redeploys

## What each metric means for your resume
Run `benchmark.py` and record:
- **% resolved free**: rules + cache + fast tier, no escalation needed
- **Route distribution**: what % handled by each layer
- **Average latency**: response time across the test set
- If you add a real `ANTHROPIC_API_KEY`: actual $ saved vs. an all-Claude baseline
