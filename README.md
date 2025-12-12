---
title: AI Sandbox
emoji: 💻
colorFrom: gray
colorTo: blue
sdk: docker
pinned: false
app_port: 7860
---

# AI Sandbox Terminal

A browser-based terminal application capable of running a coding agent sandbox. Built with FastAPI, Xterm.js, and Supabase.

## Features
- **Web Terminal**: Full-featured terminal using Xterm.js and WebSocket.
- **Secure Auth**: Protected via Supabase Authentication.
- **Sandboxing**: Runs in a Docker container (non-root by default).

## Setup
### Environment Variables
You need to Configre the following secrets in your Space settings (or `.env` locally):
- `SUPABASE_URL`: Your Supabase Project URL.
- `SUPABASE_KEY`: Your Supabase Anon Key.

### Local Development
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Deployment
This Space is automatically deployed from GitHub via Actions.