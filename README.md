# NASA Near-Earth Objects (NEO) ETL Pipeline

An end-to-end, modular, and containerized data pipeline (ETL) built in Python to extract daily near-Earth asteroid data from NASA's NeoWs API, transform and normalize the nested structures, and load them into an isolated PostgreSQL database running inside Docker.

## — Pipeline Architecture

```text
  [ NASA API ]
       │
       ▼  (Extract) - Bypasses 7-day API limit via weekly batching
  [ extract.py ]
       │
       ▼  (JSON Raw Data)
  [ transform.py ] 
       │
       ├─► (Normalize & Deduplicate: 1655 events -> 1502 unique entities)
       └─► (Data Type Conversion: string metrics to float)
       │
       ▼  (Clean JSON Data)
  [ load.py ]
       │
       ▼  (Load via psycopg2)
  [ Docker (PostgreSQL Server) ] ──► (Dimension vs. Fact SQL Tables)
```

## — Tech Stack & Practices

*   **Language:** Python 3.12.4
*   **Database:** PostgreSQL 15 (Containerized via Docker Compose)
*   **Security:** Environment variables protection (`python-dotenv` & `.gitignore`)
*   **Database Driver:** `psycopg2-binary` (Parameterized queries & `ON CONFLICT` handling)
*   **Software Design:** Modular architecture (`src/` package package) and single-entry orchestrator (`main.py`)

## — Database Schema

The database was modeled following **Dimensional Modeling** principles (separating static entities from dynamic events to prevent redundancy):

1.  **`asteroids` (Dimension Table):** Holds static information about unique asteroids.
2.  **`close_approaches` (Fact/Event Table):** Records each historical approach event, linked via a Foreign Key pointing to the asteroid's ID.

---

## — How to Run this Project

### 1. Prerequisites
*   Docker & Docker Desktop installed and running.
*   Python 3.12.4 installed.

### 2. Setup Configuration
Clone this repository and create a `.env` file in the root directory:

```env
NASA_API_KEY=your_nasa_api_key_here
DB_HOST=localhost
DB_PORT=5433
DB_NAME=nasa_asteroids
DB_USER=admin_nasa
DB_PASSWORD=your_secure_db_password
```

### 3. Spin up the PostgreSQL Database (Docker)
Run the following command to download and start the PostgreSQL container in detached mode:

```bash
docker compose up -d
```

### 4. Install Python Dependencies
```bash
pip install -r requirements.txt
```
*(Or install manually: `pip install requests python-dotenv psycopg2-binary`)*

### 5. Execute the ETL Pipeline
Run the central orchestrator to run the complete Extract, Transform, and Load cycle:

```bash
python main.py
```
