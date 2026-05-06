
# Network Route Optimization API

## Features
- Add nodes
- Add edges
- Find shortest route using Dijkstra Algorithm
- Route query history
- Swagger documentation

---

## Setup Instructions

### 1. Create Virtual Environment

Windows:
```bash
python -m venv venv_my_projects
venv\Scripts\activate
```

Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Run Server

```bash
uvicorn main:app --reload
```

---

## API Docs

Swagger UI:
```
http://127.0.0.1:8000/docs
```

ReDoc:
```
http://127.0.0.1:8000/redoc
```

---

## Example Flow

### Add Nodes

POST `/nodes`

```json
{
  "name": "ServerA"
}
```

---

### Add Edge

POST `/edges`

```json
{
  "source": "ServerA",
  "destination": "ServerB",
  "latency": 12.5
}
```

---

### Get Shortest Route

POST `/routes/shortest`

```json
{
  "source": "ServerA",
  "destination": "ServerB"
}
```

---

## Tech Stack

- FastAPI
- Python
- Dijkstra Algorithm
