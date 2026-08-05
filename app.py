import os
import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DB_SSLMODE = os.getenv("DB_SSLMODE", "require")

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
        st.error(f"❌ Could not connect to PostgreSQL: {e}")
        return pd.DataFrame()

# --- MAIN APP HEADER ---
st.title("☄️ NASA Asteroid Analytics & Data Assistant AI")
st.markdown("End-to-End ETL Data Pipeline & Interactive Analytics Platform")

# Fetch Data
df = load_data_from_postgres()

if df.empty:
    st.warning("⚠️ No data found in PostgreSQL. Ensure the pipeline ran successfully and Docker is active.")
    st.stop()

# --- TABS LAYOUT ---
tab1, tab2 = st.tabs(["📊 Analytics Dashboard", "💻 Data Analytics Assistant"])

# TAB 1: ANALYTICS DASHBOARD
with tab1:
    st.header("Planetary Defense & Asteroid Metrics")
    
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
    
    # --- PLOTLY CHARTS ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Velocity vs. Miss Distance")
        fig_scatter = px.scatter(
            df,
            x="miss_distance_km",
            y="velocity_kmh",
            color="is_potentially_hazardous",
            hover_name="name",
            labels={
                "miss_distance_km": "Miss Distance (km)",
                "velocity_kmh": "Velocity (km/h)",
                "is_potentially_hazardous": "Hazardous?"
            },
            color_discrete_map={True: "#EF553B", False: "#636EFA"},
            template="plotly_dark"
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
            labels={
                "diameter_max_meters": "Max Diameter (Meters)",
                "is_potentially_hazardous": "Potentially Hazardous?"
            },
            color_discrete_map={True: "#EF553B", False: "#636EFA"},
            template="plotly_dark"
        )
        st.plotly_chart(fig_box, use_container_width=True)
        
    # --- DATA EXPLORER & FILTERS ---
    st.subheader("🔍 Data Explorer")
    
    hazard_filter = st.radio(
        "Filter by Hazard Status:",
        options=["All", "Hazardous Only", "Non-Hazardous Only"],
        horizontal=True
    )
    
    filtered_df = df.copy()
    if hazard_filter == "Hazardous Only":
        filtered_df = filtered_df[filtered_df["is_potentially_hazardous"] == True]
    elif hazard_filter == "Non-Hazardous Only":
        filtered_df = filtered_df[filtered_df["is_potentially_hazardous"] == False]
        
    st.dataframe(
        filtered_df[[
            "name", "approach_date", "velocity_kmh", "miss_distance_km",
            "diameter_min_meters", "diameter_max_meters", "is_potentially_hazardous"
        ]],
        use_container_width=True
    )

# ==========================================
# TAB 2: NEO ANALYTICS AI ASSISTANT
# ==========================================
with tab2:
    st.header("💻 Data Analytics Assistant")
    st.markdown(
        "Query the astronomical dataset using natural language powered by LLM data intelligence."
    )
    
    if not GROQ_API_KEY:
        st.warning("⚠️ GROQ_API_KEY not found in `.env`. Please add your API key to enable the AI Assistant.")
    else:
        try:
            from groq import Groq
            client = Groq(api_key=GROQ_API_KEY)
            
            # Professional initial message
            if "messages" not in st.session_state:
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": (
                            "Hello! I am your Near-Earth Object (NEO) Data Assistant. "
                            "I can help you analyze asteroid telemetry, orbital velocities, miss distances, "
                            "and hazard evaluations based on NASA's dataset. How can I assist your analysis today?"
                        )
                    }
                ]
                
            # Render chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    
            # User Prompt Input
            if prompt := st.chat_input("Ask a data query (e.g., Summary of hazardous objects in 2025)..."):
                # Display user message
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                    
                # Prepare System Prompt with Data Context
                summary_context = (
                    f"Dataset Summary & Telemetry Context:\n"
                    f"- Total Unique Asteroids: {total_asteroids}\n"
                    f"- Hazardous Asteroids Count: {hazardous_count} ({hazardous_pct:.2f}% of total)\n"
                    f"- Minimum Miss Distance Recorded: {closest_distance:,.2f} km\n"
                    f"- Maximum Recorded Velocity: {max_velocity:,.2f} km/h\n"
                    f"\nTop 5 Closest Approaches in Dataset:\n"
                    f"{df.sort_values('miss_distance_km')[['name', 'approach_date', 'miss_distance_km', 'velocity_kmh', 'is_potentially_hazardous']].head(5).to_string(index=False)}"
                )
                
                # Professional & Objective System Instruction
                system_instruction = (
                    "You are a professional Data Analytics Assistant specialized in astronomical telemetry "
                    "and Near-Earth Object (NEO) datasets. Answer user questions objectively, concisely, "
                    "and accurately based strictly on the dataset context provided. Maintain a professional, "
                    "data-driven, and analytical tone in English."
                )
                
                # Query LLM
                with st.chat_message("assistant"):
                    with st.spinner("Processing telemetry data..."):
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                {"role": "system", "content": system_instruction},
                                {"role": "system", "content": f"Data Context:\n{summary_context}"},
                                *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                            ],
                            temperature=0.2, # Lower temperature for more factual responses
                            max_tokens=400
                        )
                        reply = response.choices[0].message.content
                        st.markdown(reply)
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                        
        except Exception as e:
            st.error(f"Error initializing AI Assistant: {e}")