# Deploying Chronos to Render (backend) + Vercel (frontend)

This project is a monorepo: FastAPI backend at the repo root, Next.js frontend in `frontend/`.

## 0. Prereqs

- Push the repo to GitHub (Render and Vercel both pull from git).
- Have a [Render](https://render.com) account and a [Vercel](https://vercel.com) account.
- (Optional) A Gemini or OpenAI API key. Without one the backend runs in `mock` LLM mode, which is fine for a demo.

---

## 1. Deploy the backend on Render

The repo already contains a `render.yaml` blueprint at the root.

### Option A — Blueprint (recommended)

1. Go to **Render Dashboard → New → Blueprint**.
2. Connect your GitHub repo. Render will detect `render.yaml` and propose a `chronos-backend` web service.
3. When prompted, fill in the env vars marked `sync: false`:
   - `CORS_ORIGINS` — **leave blank for now**, you'll set it in step 3 once you know the Vercel URL. (Defaults to `*` which lets things work while you finish setup.)
   - `DATABASE_URL` — leave blank to use SQLite on the ephemeral disk (fine for demos; data resets on redeploy). For persistence, create a Render PostgreSQL instance and paste its **Internal Database URL** here.
   - `GEMINI_API_KEY` / `OPENAI_API_KEY` — only if you want real LLM responses. Otherwise leave blank and keep `LLM_PROVIDER=mock`.
4. Click **Apply**. First build takes ~3–5 min.
5. Once live, note the service URL, e.g. `https://chronos-backend.onrender.com`. Hit `/healthz` to confirm it returns `{"status":"ok"}`.

### Option B — Manual (no blueprint)

If you'd rather click through:

- **New → Web Service**, point at the repo.
- Runtime: Python 3.11.
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/healthz`
- Add the env vars from `render.yaml` manually.

### Notes on the free plan

- Render's free web services sleep after ~15 min of inactivity. The first request after sleep takes 30–60s to wake. Fine for a demo, painful for real users.
- SQLite lives on the container's ephemeral filesystem — every redeploy wipes it. Attach a Render Postgres instance for anything you want to keep.

---

## 2. Deploy the frontend on Vercel

1. Go to **Vercel → Add New → Project** and import the same GitHub repo.
2. **Root Directory: `frontend`** (critical — the Next.js app is not at the repo root).
3. Framework preset auto-detects as Next.js. Leave build/output settings on defaults.
4. Under **Environment Variables**, add:
   - `NEXT_PUBLIC_API_URL` = the Render URL from step 1 (e.g. `https://chronos-backend.onrender.com`). No trailing slash.
5. Click **Deploy**. First build ~2 min.
6. Note the Vercel URL, e.g. `https://chronos.vercel.app`.

The frontend's default API URL now comes from `NEXT_PUBLIC_API_URL` (see `frontend/store/settingsStore.ts`). Users can still override it at runtime via the Settings page — that override is stored in `localStorage` and takes precedence.

---

## 3. Lock CORS to the Vercel origin

Once you have the Vercel URL, go back to Render → your `chronos-backend` service → **Environment** and set:

```
CORS_ORIGINS=https://chronos.vercel.app,https://*.vercel.app
```

(Include the `*.vercel.app` entry if you want preview deployments to work too. Otherwise just the production URL.)

Save; Render will redeploy. This flips `allow_credentials` on and stops the API accepting requests from arbitrary origins.

---

## 4. Smoke test

- `curl https://chronos-backend.onrender.com/healthz` → `{"status":"ok"}`
- Open `https://chronos.vercel.app` in a browser and check the DevTools Network tab — API calls should hit the Render URL and return 200s.
- If you see CORS errors: recheck `CORS_ORIGINS` on Render matches the exact Vercel origin (scheme + host, no trailing slash).
- If the frontend still talks to `localhost:8000`: `NEXT_PUBLIC_API_URL` wasn't set at build time. Redeploy after adding it — `NEXT_PUBLIC_*` vars are baked in at build, not read at runtime.

---

## 5. Ongoing

- Push to `main` → both services auto-deploy.
- To point the frontend at a different backend (staging, local ngrok), either change `NEXT_PUBLIC_API_URL` in Vercel and redeploy, or use the in-app Settings page for a temporary per-browser override.
