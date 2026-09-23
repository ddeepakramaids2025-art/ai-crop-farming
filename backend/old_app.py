import streamlit as st
import pandas as pd
import os
import requests


# =========================================================
# FASTAPI BACKEND
# =========================================================

API_URL = "http://127.0.0.1:8000"


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Crop Decision System",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# DARK DASHBOARD THEME
# =========================================================

st.markdown("""
<style>

html,
body,
.stApp,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
section.main,
.main {
    background-color: #0b1220 !important;
    color: #e5e7eb !important;
}

[data-testid="stAppViewContainer"] {
    background: #0b1220 !important;
}

[data-testid="stHeader"] {
    background: #0b1220 !important;
}

[data-testid="stMainBlockContainer"] {
    background: #0b1220 !important;
}


/* SIDEBAR */

[data-testid="stSidebar"] {
    background: #111827 !important;
    border-right: 1px solid #263244 !important;
}

[data-testid="stSidebar"] > div {
    background: #111827 !important;
}

[data-testid="stSidebarContent"] {
    background: #111827 !important;
}

[data-testid="stSidebar"] * {
    color: #f9fafb !important;
}


/* HEADINGS */

h1,
h2,
h3,
h4,
h5,
h6 {
    color: #ffffff !important;
    font-weight: 700 !important;
}


/* NORMAL TEXT */

p {
    color: #d1d5db !important;
}


/* SELECT BOX */

[data-testid="stSelectbox"] label {
    color: #ffffff !important;
    font-weight: 600 !important;
}

[data-baseweb="select"] {
    background-color: #1f2937 !important;
    border: 1px solid #374151 !important;
    border-radius: 10px !important;
}

[data-baseweb="select"] * {
    color: #ffffff !important;
}

[data-baseweb="select"] input {
    color: #ffffff !important;
}

[data-baseweb="popover"] {
    background-color: #111827 !important;
}

[data-baseweb="popover"] > div {
    background-color: #111827 !important;
}

[role="option"] {
    background-color: #111827 !important;
    color: #ffffff !important;
}

[role="option"]:hover {
    background-color: #1f2937 !important;
}


/* INPUT */

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background-color: #1f2937 !important;
    color: #ffffff !important;
    border: 1px solid #374151 !important;
    border-radius: 8px !important;
}


/* METRIC */

[data-testid="stMetric"] {
    background: linear-gradient(
        145deg,
        #172033,
        #111827
    ) !important;

    border: 1px solid #263244 !important;
    border-radius: 16px !important;
    padding: 18px !important;

    box-shadow:
        0 4px 15px rgba(0, 0, 0, 0.30) !important;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] * {
    color: #9ca3af !important;
}

[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {
    color: #ffffff !important;
}


/* DATAFRAME */

[data-testid="stDataFrame"] {
    background-color: #111827 !important;
    border: 1px solid #263244 !important;
    border-radius: 12px !important;
}


/* ALERT */

[data-testid="stAlert"] {
    background-color: #172033 !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
}

[data-testid="stAlert"] * {
    color: #e5e7eb !important;
}


/* BUTTON */

.stButton > button {
    background-color: #16a34a !important;
    color: white !important;
    border: none !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    width: 100%;
}

.stButton > button:hover {
    background-color: #22c55e !important;
    color: white !important;
}


/* DIVIDER */

hr {
    border-color: #263244 !important;
}


/* EXPANDER */

[data-testid="stExpander"] {
    background-color: #111827 !important;
    border: 1px solid #263244 !important;
    border-radius: 12px !important;
}


/* CODE */

code {
    color: #7dd3fc !important;
}


/* LINKS */

a {
    color: #60a5fa !important;
}


/* DASHBOARD TITLE */

.dashboard-title {
    background: linear-gradient(
        135deg,
        #111827,
        #172033
    );

    border: 1px solid #263244;
    border-radius: 18px;

    padding: 25px;
    margin-bottom: 20px;

    box-shadow:
        0 5px 20px rgba(0,0,0,0.25);
}

.dashboard-title h1 {
    margin: 0;
    color: #ffffff !important;
    font-size: 36px;
}

.dashboard-title p {
    margin-top: 8px;
    color: #9ca3af !important;
    font-size: 16px;
}


/* FARMER CARD */

.farmer-card {
    background: linear-gradient(
        135deg,
        #111827,
        #172033
    );

    border: 1px solid #263244;

    border-radius: 16px;

    padding: 20px;

    margin-top: 15px;
    margin-bottom: 20px;
}


/* PREDICTION CARD */

.prediction-card {
    background: linear-gradient(
        135deg,
        #123524,
        #10271c
    );

    border: 1px solid #166534;

    border-radius: 16px;

    padding: 20px;

    margin-top: 20px;
    margin-bottom: 20px;
}


/* FOOTER */

.footer {
    text-align: center;
    color: #6b7280;

    padding: 20px;
    margin-top: 20px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD DATA
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "Final_Crop_Dashboard_Data.csv"
)


if not os.path.exists(DATA_PATH):

    st.error(
        "❌ Final_Crop_Dashboard_Data.csv was not found."
    )

    st.code(DATA_PATH)

    st.stop()


df = pd.read_csv(DATA_PATH)


df.columns = (
    df.columns
    .astype(str)
    .str.strip()
)


# =========================================================
# CHECK REQUIRED COLUMNS
# =========================================================

required_columns = [
    "State",
    "District",
    "Season",
    "Crop",
    "Risk_Adjusted_Score"
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    st.error(
        "❌ Required columns are missing:"
    )

    st.write(missing_columns)

    st.stop()


# =========================================================
# FASTAPI CONNECTION
# =========================================================

backend_connected = False


try:

    response = requests.get(
        f"{API_URL}/",
        timeout=5
    )

    if response.status_code == 200:

        backend_connected = True

        st.sidebar.success(
            "🟢 FastAPI Backend Connected"
        )

    else:

        st.sidebar.warning(
            "🟡 FastAPI is running"
        )


except requests.exceptions.RequestException:

    st.sidebar.error(
        "🔴 FastAPI Backend Not Connected"
    )


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title(
    "🎯 Crop Decision System"
)

st.sidebar.markdown("---")

st.sidebar.subheader(
    "📍 Select Location"
)


# =========================================================
# GET STATES
# =========================================================

states = []


try:

    response = requests.get(
        f"{API_URL}/states",
        timeout=5
    )

    if response.status_code == 200:

        states = response.json().get(
            "states",
            []
        )

except requests.exceptions.RequestException:

    states = []


if not states:

    states = sorted(
        df["State"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )


if not states:

    st.error(
        "❌ No states available."
    )

    st.stop()


selected_state = st.sidebar.selectbox(
    "🇮🇳 State",
    states
)


# =========================================================
# STATE DATA
# =========================================================

state_data = df[
    df["State"]
    .astype(str)
    .str.strip()
    .str.lower()
    ==
    str(selected_state).strip().lower()
].copy()


# =========================================================
# GET DISTRICTS
# =========================================================

districts = []


try:

    response = requests.get(
        f"{API_URL}/districts/{selected_state}",
        timeout=5
    )

    if response.status_code == 200:

        districts = response.json().get(
            "districts",
            []
        )

except requests.exceptions.RequestException:

    districts = []


if not districts:

    districts = sorted(
        state_data["District"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )


if not districts:

    st.warning(
        f"No districts available for {selected_state}."
    )

    st.stop()


selected_district = st.sidebar.selectbox(
    "📍 District",
    districts
)


# =========================================================
# DISTRICT DATA
# =========================================================

district_data = state_data[
    state_data["District"]
    .astype(str)
    .str.strip()
    .str.lower()
    ==
    str(selected_district).strip().lower()
].copy()


# =========================================================
# GET SEASONS
# =========================================================

seasons = []


try:

    response = requests.get(
        f"{API_URL}/seasons/"
        f"{selected_state}/"
        f"{selected_district}",
        timeout=5
    )

    if response.status_code == 200:

        seasons = response.json().get(
            "seasons",
            []
        )

except requests.exceptions.RequestException:

    seasons = []


if not seasons:

    seasons = sorted(
        district_data["Season"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )


if not seasons:

    st.warning(
        "No seasons available."
    )

    st.stop()


selected_season = st.sidebar.selectbox(
    "🌦️ Season",
    seasons
)


# =========================================================
# CURRENT SELECTION
# =========================================================

st.sidebar.markdown("---")

st.sidebar.subheader(
    "📌 Current Selection"
)

st.sidebar.markdown(
    f"**State:** {selected_state}"
)

st.sidebar.markdown(
    f"**District:** {selected_district}"
)

st.sidebar.markdown(
    f"**Season:** {selected_season}"
)

st.sidebar.markdown("---")


if backend_connected:

    st.sidebar.success(
        "API Status: Online"
    )

else:

    st.sidebar.error(
        "API Status: Offline"
    )


# =========================================================
# MAIN HEADER
# =========================================================

st.markdown(
    """
    <div class="dashboard-title">

        <h1>🌾 AI Crop Decision System</h1>

        <p>
        Intelligent Crop Recommendation & Risk Analysis
        </p>

        <p>
        🌾 Production &nbsp; | &nbsp;
        💰 Market Price &nbsp; | &nbsp;
        💵 Cost &nbsp; | &nbsp;
        🦠 Disease &nbsp; | &nbsp;
        🌦️ Weather &nbsp; | &nbsp;
        🌱 Soil
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# FARMER INPUT
# =========================================================

st.subheader(
    "👨‍🌾 Farmer Prediction"
)

st.write(
    "Enter your field information and get a personalized crop recommendation."
)


st.markdown(
    '<div class="farmer-card">',
    unsafe_allow_html=True
)


input1, input2, input3 = st.columns(3)


with input1:

    soil_types = [
        "Select Soil Type",
        "Alluvial",
        "Black Soil",
        "Red Soil",
        "Laterite Soil",
        "Sandy Soil",
        "Clay Soil",
        "Loamy Soil",
        "Other"
    ]

    farmer_soil = st.selectbox(
        "🌱 Soil Type",
        soil_types
    )


with input2:

    farmer_land = st.number_input(
        "📐 Land Area (acres)",
        min_value=0.1,
        value=1.0,
        step=0.5
    )


with input3:

    farmer_budget = st.number_input(
        "💰 Budget (₹)",
        min_value=0,
        value=50000,
        step=5000
    )


input4, input5, input6 = st.columns(3)


with input4:

    farmer_water = st.number_input(
        "💧 Water Available (litres)",
        min_value=0,
        value=50000,
        step=5000
    )


with input5:

    st.text_input(
        "🇮🇳 Selected State",
        value=str(selected_state),
        disabled=True
    )


with input6:

    st.text_input(
        "📍 Selected District",
        value=str(selected_district),
        disabled=True
    )


st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# =========================================================
# PREDICTION BUTTON
# =========================================================

predict_button = st.button(
    "🔮 GET CROP PREDICTION"
)


# =========================================================
# FARMER PERSONALIZED PREDICTION
# =========================================================

if predict_button:

    # -----------------------------------------------------
    # CHECK SOIL
    # -----------------------------------------------------

    if farmer_soil == "Select Soil Type":

        st.warning(
            "⚠️ Please select the soil type first."
        )

        st.stop()


    # -----------------------------------------------------
    # CREATE FARMER PAYLOAD
    # -----------------------------------------------------

    farmer_payload = {

        "state":
            str(selected_state),

        "district":
            str(selected_district),

        "season":
            str(selected_season),

        "soil_type":
            str(farmer_soil),

        "land_acres":
            float(farmer_land),

        "budget":
            float(farmer_budget),

        "water":
            float(farmer_water)
    }


    # -----------------------------------------------------
    # SEND DATA TO FASTAPI
    # -----------------------------------------------------

    try:

        response = requests.post(

            f"{API_URL}/predict",

            json=farmer_payload,

            timeout=10
        )


        # -------------------------------------------------
        # CHECK RESPONSE
        # -------------------------------------------------

        if response.status_code != 200:

            st.error(
                f"❌ Prediction API error: "
                f"{response.status_code}"
            )

            st.code(
                response.text
            )

            st.stop()


        prediction_data = response.json()


        # -------------------------------------------------
        # CHECK SUCCESS
        # -------------------------------------------------

        if not prediction_data.get("success"):

            st.error(
                prediction_data.get(
                    "message",
                    "Prediction failed."
                )
            )

            st.stop()


        # -------------------------------------------------
        # GET RECOMMENDATIONS
        # -------------------------------------------------

        recommendations = (
            prediction_data.get(
                "recommendations",
                []
            )
        )


        if not recommendations:

            st.warning(
                "⚠️ No crop recommendations returned."
            )

            st.stop()


        top5 = pd.DataFrame(
            recommendations
        )


        # =================================================
        # BEST CROP
        # =================================================

        best_crop = prediction_data.get(
            "best_crop",
            recommendations[0]["Crop"]
        )


        best_row = top5.iloc[0]


        best_score = best_row.get(
            "Personalized_Score",
            None
        )


        best_rank = best_row.get(
            "Rank",
            1
        )


        # =================================================
        # RESULT CARD
        # =================================================

        st.markdown(
            '<div class="prediction-card">',
            unsafe_allow_html=True
        )


        st.subheader(
            "🔮 Personalized Prediction Result"
        )


        result1, result2, result3 = st.columns(3)


        with result1:

            st.metric(
                "🌾 Recommended Crop",
                str(best_crop)
            )


        with result2:

            if best_score is not None:

                st.metric(
                    "⭐ Personalized Score",
                    f"{float(best_score):.2f}"
                )

            else:

                st.metric(
                    "⭐ Personalized Score",
                    "N/A"
                )


        with result3:

            st.metric(
                "🏅 Rank",
                int(best_rank)
            )


        st.markdown(
            f"""
            **👨‍🌾 Farmer Input**

            🌱 Soil Type: **{farmer_soil}**

            🇮🇳 State: **{selected_state}**

            📍 District: **{selected_district}**

            🌦️ Season: **{selected_season}**

            📐 Land: **{farmer_land:,.1f} acres**

            💰 Budget: **₹{farmer_budget:,.0f}**

            💧 Water Available: **{farmer_water:,.0f} litres**
            """
        )


        st.success(
            f"🌾 Recommended crop: **{best_crop}**"
        )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


        # =================================================
        # TOP 5
        # =================================================

        st.subheader(
            "🌱 Top 5 Personalized Crop Recommendations"
        )


        display_columns = [

            "Rank",

            "Crop",

            "Personalized_Score",

            "Risk_Adjusted_Score",

            "Estimated_Cost",

            "Estimated_Water"
        ]


        available_columns = [

            column

            for column in display_columns

            if column in top5.columns
        ]


        display_data = top5[
            available_columns
        ].copy()


        display_data = display_data.rename(

            columns={

                "Rank":
                    "🏅 Rank",

                "Crop":
                    "🌱 Crop",

                "Personalized_Score":
                    "⭐ Personalized Score",

                "Risk_Adjusted_Score":
                    "📊 Risk Score",

                "Estimated_Cost":
                    "💰 Estimated Cost",

                "Estimated_Water":
                    "💧 Estimated Water"
            }
        )


        st.dataframe(

            display_data,

            use_container_width=True,

            hide_index=True
        )


        # =================================================
        # COST + WATER
        # =================================================

        st.subheader(
            "💰 Cost & Water Analysis"
        )


        cost1, cost2, cost3 = st.columns(3)


        estimated_cost = best_row.get(
            "Estimated_Cost",
            0
        )


        estimated_water = best_row.get(
            "Estimated_Water",
            0
        )


        with cost1:

            st.metric(
                "💰 Estimated Total Cost",
                f"₹{float(estimated_cost):,.0f}"
            )


        with cost2:

            st.metric(
                "💧 Estimated Water",
                f"{float(estimated_water):,.0f} L"
            )


        with cost3:

            st.metric(
                "💵 Farmer Budget",
                f"₹{farmer_budget:,.0f}"
            )


        # =================================================
        # SCORE CHART
        # =================================================

        st.subheader(
            "📊 Personalized Crop Score"
        )


        if (

            "Crop" in top5.columns

            and

            "Personalized_Score"
            in top5.columns

        ):

            chart_data = top5[
                [
                    "Crop",
                    "Personalized_Score"
                ]
            ].copy()


            chart_data = chart_data.set_index(
                "Crop"
            )


            st.bar_chart(
                chart_data
            )


        # =================================================
        # WHY THIS CROP?
        # =================================================

        st.divider()

        st.subheader(
            "🔍 Why was this crop recommended?"
        )


        st.write(
            f"""
            **{best_crop}** received the highest personalized
            score for your selected location and season.

            The system considered your:

            • Available land: **{farmer_land:,.1f} acres**

            • Budget: **₹{farmer_budget:,.0f}**

            • Available water: **{farmer_water:,.0f} litres**

            • Location: **{selected_district}, {selected_state}**

            • Season: **{selected_season}**

            The original risk-adjusted crop score was combined
            with budget and water suitability.
            """
        )


    except requests.exceptions.RequestException as e:

        st.error(
            f"❌ Could not connect to FastAPI: {e}"
        )


# =========================================================
# PROJECT OVERVIEW
# =========================================================

st.divider()

st.subheader(
    "📊 Project Overview"
)


overview1, overview2, overview3, overview4 = st.columns(4)


with overview1:

    st.metric(
        "📋 Records",
        f"{len(df):,}"
    )


with overview2:

    st.metric(
        "🇮🇳 States",
        df["State"].nunique()
    )


with overview3:

    st.metric(
        "📍 Districts",
        df["District"].nunique()
    )


with overview4:

    st.metric(
        "🌱 Crops",
        df["Crop"].nunique()
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    """
    <div class="footer">

        🌾 AI Crop Decision System<br>

        Data Science Project

    </div>
    """,
    unsafe_allow_html=True
)