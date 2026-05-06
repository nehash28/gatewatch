# Lumetra — Society Management App

A MyGate-style society management website built with Flask.

## Features
- Visitor Management (approve/deny gate entry)
- Staff Entry/Exit log and roster
- Society Notices board

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
python app.py
```

### 3. Open in browser
```
http://localhost:5000
```

## Project Structure
```
gatewatch/
├── app.py              ← Flask backend + API routes
├── requirements.txt    ← Python dependencies
├── README.md
└── templates/
    └── index.html      ← Main dashboard template
```

## API Endpoints
| Method | Route | Description |
|--------|-------|-------------|
| GET    | /     | Dashboard page |
| POST   | /api/visitors | Add a new visitor |
| PATCH  | /api/visitors/<id> | Approve or deny a visitor |
| POST   | /api/notices  | Post a new notice |

## Next Steps (to make it production-ready)
- Add a real database (SQLite or PostgreSQL with SQLAlchemy)
- Add user login/authentication (Flask-Login)
- Add separate views for Security Guard vs Resident vs Admin
- Deploy to Render, Railway, or a VPS
