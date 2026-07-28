# Supabase Auth API

A secure REST API built with FastAPI and Supabase Auth, supporting user sign up, log in, log out, and JWT-protected routes.

## What this project does

This API demonstrates a standard modern authentication flow:

1. A client signs up or logs in through this API, which delegates credential verification to Supabase (the Identity Provider).
2. Supabase returns a JWT access token to the client.
3. The client attaches that token to subsequent requests via the `Authorization: Bearer <token>` header.
4. Protected routes verify the token against Supabase before returning any data.

Logout uses Supabase's Admin API to immediately revoke the session server-side, rather than relying on the token's natural expiry.

## Setup

1. Clone this repository.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   pip install -r requirements.txt
   ```
3. Create a Supabase project at [supabase.com](https://supabase.com).
4. Copy `.env.example` to `.env` and fill in your own values from **Project Settings → API**:
   ```
   SUPABASE_URL=your_project_url
   SUPABASE_KEY=your_anon_key
   SUPABASE_SERVICE_KEY=your_service_role_key
   PORT=8000
   ```
   The service role key is required only for `/auth/logout` (session revocation via the Admin API). Never expose this key to a client or commit it to version control.

## Running the server

```bash
uvicorn main:app --reload --port 8000
```

Interactive API docs (Swagger UI) are available at `http://localhost:8000/docs`. Click **Authorize**, paste an access token obtained from `/auth/login`, and all protected routes will use it automatically.

## API Reference

| Method | Endpoint              | Auth Required | Description                          |
|--------|------------------------|:--------------:|--------------------------------------|
| POST   | `/auth/signup`         | No             | Create a new user account            |
| POST   | `/auth/login`          | No             | Authenticate and receive a JWT       |
| POST   | `/auth/logout`         | Yes            | Revoke the current session           |
| GET    | `/public/info`         | No             | Public, unauthenticated data         |
| GET    | `/protected/profile`   | Yes            | Return the authenticated user's data |
| GET    | `/protected/dashboard` | Yes            | Example second protected route       |

**Status codes:** `201` on successful signup, `200` on successful login/read, `204` on logout, `400` on missing/invalid input, `401` on missing, malformed, or invalid/expired tokens.

## Swagger UI

![Swagger UI showing an authenticated request to /protected/profile](./swagger-screenshot.png)

*Authenticated `GET /protected/profile` request via Swagger UI, using the Authorize button to attach a bearer token to all protected routes.*

## Architecture notes

- **Two Supabase clients** are used: an anon-key client for all user-facing auth operations, and a separate service-role-key client used exclusively by `/auth/logout` to revoke an arbitrary session by token. The service role key is never used for any user-facing verification.
- Token verification is centralized in a single FastAPI dependency (`auth.py`), applied to every protected route, rather than duplicated per-route.
- All error responses use a consistent `{"error": "..."}` shape, including framework-level exceptions, via a global exception handler.