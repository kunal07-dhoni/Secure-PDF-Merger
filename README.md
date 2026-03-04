# 🔒 Secure PDF Merger

A production-ready, privacy-focused PDF merging platform built with FastAPI + React.

## Features

- 🔐 **JWT Authentication** — Register, login, token refresh
- 📄 **PDF Merging** — Upload, reorder (drag & drop), merge multiple PDFs
- 📏 **Page Ranges** — Select specific pages from each PDF
- 💧 **Watermarks** — Add diagonal text watermarks
- 🗜️ **Compression** — Reduce output file size
- 📊 **History Dashboard** — Track past merges with download links
- 🗑️ **Auto-Cleanup** — Files auto-delete after 30 minutes
- 🌓 **Dark/Light Mode** — System-aware theme toggle
- 📱 **Responsive** — Full mobile support
- 🐳 **Docker Ready** — One-command deployment

## Tech Stack

| Layer     | Technology                    |
|-----------|-------------------------------|
| Backend   | Python, FastAPI, SQLAlchemy   |
| Frontend  | React 18, Tailwind CSS        |
| Database  | PostgreSQL (prod), SQLite (dev)|
| Auth      | JWT + bcrypt                  |
| PDF       | pypdf + ReportLab             |
| Queue     | APScheduler (cleanup)         |
| Cache     | Redis (rate limiting)         |
| Deploy    | Docker, Nginx                 |

## Quick Start

### Prerequisites
- Docker & Docker Compose
- OR: Python 3.11+, Node.js 18+, PostgreSQL

### With Docker (Recommended)

```bash
git clone <repo-url>
cd secure-pdf-merger

# Copy environment file
cp .env.example backend/.env

# Build and run
docker compose up --build

# Access:
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs