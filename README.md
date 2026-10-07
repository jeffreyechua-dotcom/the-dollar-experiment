# The $1 Experiment

Deployment-ready Flask MVP for The $1 Experiment.

## Deploy
1. Upload this folder's contents to GitHub.
2. Create a Render Web Service from the GitHub repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app --workers 1 --threads 4 --timeout 120`
5. Set `GOAL=1000`, `FLASK_SECRET_KEY` (generated), and a persistent PostgreSQL `DATABASE_URL`.

## Important
The `/api/join` endpoint currently creates a test participant without charging. Do not take live payments until Paystack initialization, server-side verification/webhooks, secure participant authentication, privacy/terms/refund policies, and legal/payment classification are implemented.
