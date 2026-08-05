# NASA Near-Earth Objects (NEO) ETL Pipeline & Analytics Platform

An end-to-end, modular, and containerized data engineering pipeline (ETL) built in Python to extract daily near-Earth asteroid data from NASA's NeoWs API, validate and transform the telemetry with Pydantic, load it into PostgreSQL, orchestrate execution with Mage.ai, and serve interactive analytics & AI query capabilities via Streamlit.

## — Pipeline Architecture

```text
  [ NASA API ]
       │
       ▼  (Extract) - Bypasses 7-day API limit via weekly batching
  [ extract.py ]
       │
       ▼  (JSON Raw Data)
  [ transform.py + schemas.py ] 
       │
       ├─► (Data Quality & Contract Validation via Pydantic V2)
       ├─► (Normalize & Deduplicate: 1:N Relational Entities)
       └─► (Data Type Conversion & Handling Outliers)
       │
       ▼  (Validated JSON Data)
  [ load.py ]
       │
       ▼  (Idempotent UPSERT via psycopg2)
  [ Docker Containers ] ──► (PostgreSQL DB + Mage.ai Orchestrator)
       │
       ▼  (Data Consumption & Analytics)
  [ Streamlit App ] ──► (Plotly Dashboards & Llama 3 AI Data Agent)
```

## — Tech Stack & Practices

*   **Language:** Python 3.12+
*   **Orchestration:** Mage.ai (Containerized DAG workflow)
*   **Data Validation:** Pydantic V2 (Data contracts & type enforcement)
*   **Database:** PostgreSQL 15 (Containerized via Docker Compose)
*   **Analytics & AI:** Streamlit, Plotly Express, Groq API (Llama 3 LLM)
*   **Security:** Environment variables protection (`python-dotenv` & `.gitignore`)
*   **Database Driver:** `psycopg2-binary` (Parameterized queries & `ON CONFLICT` handling)
*   **Software Design:** Modular architecture (`src/` package) and single-entry orchestrator (`main.py`)

## — Database Schema

The database was modeled following **Dimensional Modeling** principles (separating static entities from dynamic events to prevent redundancy):

1.  **`asteroids` (Dimension Table):** Holds static information about unique asteroids.
2.  **`close_approaches` (Fact/Event Table):** Records each historical approach event, linked via a Foreign Key pointing to the asteroid's ID.

---

## — How to Run this Project

### 1. Prerequisites
*   Docker & Docker Desktop installed and running.
*   Python 3.12+ installed.

### 2. Setup Configuration
Clone this repository and create a `.env` file in the root directory (refer to `.env.example`):

```env
NASA_API_KEY=your_nasa_api_key_here
GROQ_API_KEY=your_groq_api_key_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nasa_asteroids
DB_USER=postgres
DB_PASSWORD=your_secure_db_password
```

### 3. Spin up Infrastructure (Docker)
Run the following command to start PostgreSQL and the Mage.ai orchestrator in containerized mode:

```bash
docker compose up -d
```
*   **Mage.ai UI:** Available at `http://localhost:6789`

### 4. Install Python Dependencies
```bash
pip install -r requirements.txt
```
*(Dependencies include: `requests`, `python-dotenv`, `psycopg2-binary`, `pydantic`, `streamlit`, `plotly`, `pandas`, `groq`)*

### 5. Execute the ETL Pipeline
You can trigger the pipeline via the CLI orchestrator:

```bash
python main.py
```
*Or execute the visual DAG directly inside Mage.ai at `http://localhost:6789`.*

### 6. Launch the Analytics & AI Dashboard
Start the Streamlit web application to view interactive charts and query the dataset with Llama 3 AI:

```bash
streamlit run app.py
```
*   **Streamlit UI:** Available at `http://localhost:8501`
