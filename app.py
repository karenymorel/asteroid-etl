import os
import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_secret(key: str, default: str = None) -> str:
    try:
        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return os.getenv(key, default)

# --- DB & API CONFIGURATION ---
DB_HOST = get_secret("DB_HOST", "localhost")
DB_PORT = get_secret("DB_PORT", "5432")
DB_NAME = get_secret("DB_NAME")
DB_USER = get_secret("DB_USER")
DB_PASSWORD = get_secret("DB_PASSWORD")
GROQ_API_KEY = get_secret("GROQ_API_KEY")

if DB_HOST in ["localhost", "127.0.0.1", "db"]:
    DB_SSLMODE = "disable"
else:
    DB_SSLMODE = get_secret("DB_SSLMODE", "require")

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NASA Asteroid Analytics & AI Agent",
    page_icon="☄️",
    layout="wide"
)

# --- DATABASE CONNECTION & DATA FETCHING ---
@st.cache_data(ttl=300)
def load_data_from_postgres():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            sslmode=DB_SSLMODE
        )
        query = """
        SELECT 
            a.id AS asteroid_id,
            a.name,
            a.absolute_magnitude,
            a.diameter_min_meters,
            a.diameter_max_meters,
            a.is_potentially_hazardous,
            a.is_sentry_object,
            c.approach_date,
            c.velocity_kmh,
            c.miss_distance_km,
            c.orbiting_body
        FROM asteroids a
        JOIN close_approaches c ON a.id = c.asteroid_id;
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Could not connect to PostgreSQL ({DB_HOST}): {e}")
        return pd.DataFrame()

# --- MAIN APP HEADER ---
st.title("☄️ NASA Asteroid Analytics & Space Intelligence")
st.markdown("End-to-End ETL Data Pipeline & Interactive Analytics Platform")

# Fetch Data
df = load_data_from_postgres()

if df.empty:
    st.warning("⚠️ No data found in PostgreSQL. Ensure the pipeline ran successfully and Docker is active.")
    st.stop()

# SIDEBAR: NEO ANALYTICS AI ASSISTANT
with st.sidebar:
    st.header("🤖 NEO AI Assistant")
    st.markdown("Query the dataset using natural language.")
    
    if not GROQ_API_KEY:
        st.warning("⚠️ GROQ_API_KEY not found. Add it to secrets to enable AI.")
    else:
        try:
            from groq import Groq
            client = Groq(api_key=GROQ_API_KEY)
            
            # Initial Assistant Message
            if "messages" not in st.session_state:
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": "Hello! I am your NEO Data Assistant. How can I assist your analysis today?"
                    }
                ]
                
            # Render chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    
            # User Prompt Input
            if prompt := st.chat_input("Ask a data query..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                    
                total_asteroids = df["asteroid_id"].nunique()
                hazardous_df = df[df["is_potentially_hazardous"] == True]
                non_hazardous_df = df[df["is_potentially_hazardous"] == False]
                
                hazardous_count = hazardous_df["asteroid_id"].nunique()
                hazardous_pct = (hazardous_count / total_asteroids * 100) if total_asteroids > 0 else 0
                closest_distance = df["miss_distance_km"].min()
                max_velocity = df["velocity_kmh"].max()
                
                # Diameter metrics
                max_diameter = df["diameter_max_meters"].max()
                avg_haz_diameter = hazardous_df["diameter_max_meters"].mean() if not hazardous_df.empty else 0
                avg_non_haz_diameter = non_hazardous_df["diameter_max_meters"].mean() if not non_hazardous_df.empty else 0
                
                # Top tables for exact queries
                top_largest = df.sort_values("diameter_max_meters", ascending=False)[
                    ["name", "diameter_max_meters", "is_potentially_hazardous"]
                ].drop_duplicates("name").head(5).to_string(index=False)
                
                top_closest = df.sort_values("miss_distance_km", ascending=True)[
                    ["name", "miss_distance_km", "is_potentially_hazardous"]
                ].drop_duplicates("name").head(5).to_string(index=False)

                summary_context = f"""
                Dataset Telemetry Context:
                - Total Unique Asteroids: {total_asteroids}
                - Potentially Hazardous Count: {hazardous_count} ({hazardous_pct:.1f}%)
                - Max Diameter Recorded: {max_diameter:,.2f} meters
                - Average Hazardous Diameter: {avg_haz_diameter:,.2f} meters
                - Average Non-Hazardous Diameter: {avg_non_haz_diameter:,.2f} meters
                - Closest Miss Distance: {closest_distance:,.2f} km
                - Max Recorded Velocity: {max_velocity:,.2f} km/h

                Top 5 Largest Asteroids by Diameter:
                {top_largest}

                Top 5 Closest Approaching Asteroids:
                {top_closest}
                """
                
                system_instruction = (
                    "You are a professional Data Analytics Assistant specialized in Near-Earth Object (NEO) telemetry. "
                    "Answer questions accurately, concisely, and objectively in English based on the dataset telemetry provided. "
                    "You have exact diameter, velocity, distance, and top asteroid lists in your context."
                )
                
                # Query LLM
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing telemetry data..."):
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                {"role": "system", "content": system_instruction},
                                {"role": "system", "content": summary_context},
                                *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                            ],
                            temperature=0.2,
                            max_tokens=400
                        )
                        reply = response.choices[0].message.content
                        st.markdown(reply)
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                        
        except Exception as e:
            st.error(f"AI Assistant Error: {e}")

# MAIN PAGE: ANALYTICS DASHBOARD
st.header("Planetary Telemetry & Hazard Metrics")

# --- KPI CARDS ---
total_asteroids = df["asteroid_id"].nunique()
hazardous_count = df[df["is_potentially_hazardous"] == True]["asteroid_id"].nunique()
hazardous_pct = (hazardous_count / total_asteroids * 100) if total_asteroids > 0 else 0
closest_distance = df["miss_distance_km"].min()
max_velocity = df["velocity_kmh"].max()

col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Unique Asteroids", value=f"{total_asteroids:,}")
col2.metric(label="Potentially Hazardous", value=f"{hazardous_count:,}", delta=f"{hazardous_pct:.1f}% hazard rate", delta_color="inverse")
col3.metric(label="Closest Miss Distance", value=f"{closest_distance:,.0f} km")
col4.metric(label="Max Recorded Velocity", value=f"{max_velocity:,.0f} km/h")

st.markdown("---")

# --- PLOTLY CHARTS (LIGHT THEME) ---
c1, c2 = st.columns(2)

COLOR_MAP = {True: "#D90429", False: "#0077B6"}

with c1:
    st.subheader("Velocity vs. Miss Distance")
    fig_scatter = px.scatter(
        df,
        x="miss_distance_km",
        y="velocity_kmh",
        color="is_potentially_hazardous",
        hover_name="name",
        labels={"miss_distance_km": "Miss Distance (km)", "velocity_kmh": "Velocity (km/h)", "is_potentially_hazardous": "Hazardous?"},
        color_discrete_map=COLOR_MAP,
        template="plotly_white"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
with c2:
    st.subheader("Asteroid Diameter by Hazard Class")
    df_diameter_filtered = df[(df["diameter_max_meters"] > 0) & (df["diameter_max_meters"] <= 2000)]
    fig_box = px.box(
        df_diameter_filtered,
        x="is_potentially_hazardous",
        y="diameter_max_meters",
        color="is_potentially_hazardous",
        labels={"diameter_max_meters": "Max Diameter (Meters)", "is_potentially_hazardous": "Potentially Hazardous?"},
        color_discrete_map=COLOR_MAP,
        template="plotly_white"
    )
    st.plotly_chart(fig_box, use_container_width=True)
    
# --- DATA EXPLORER & FILTERS ---
st.subheader("🔍 Data Explorer")
hazard_filter = st.radio("Filter by Hazard Status:", options=["All", "Hazardous Only", "Non-Hazardous Only"], horizontal=True)

filtered_df = df.copy()
if hazard_filter == "Hazardous Only":
    filtered_df = filtered_df[filtered_df["is_potentially_hazardous"] == True]
elif hazard_filter == "Non-Hazardous Only":
    filtered_df = filtered_df[filtered_df["is_potentially_hazardous"] == False]
    
st.dataframe(
    filtered_df[["name", "approach_date", "velocity_kmh", "miss_distance_km", "diameter_min_meters", "diameter_max_meters", "is_potentially_hazardous"]],
    use_container_width=True
)