import os
import requests
import pandas as pd
import streamlit as st


# =========================================================
# CONFIG
# =========================================================

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Crop Decision System",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# DASHBOARD STYLE
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0b1220;
        color: #e5e7eb;
    }

    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #263244;
    }

    [data-testid="stSidebar"] * {
        color: #f9fafb;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }

    p, label {
        color: #d1d5db !important;
    }

    [data-baseweb="select"] {
        background-color: #1f2937 !important;
        border-radius: 10px;
    }

    [data-baseweb="select"] * {
        color: white !important;
    }

    [data-baseweb="popover"] {
        background-color: #111827 !important;
    }

    [role="option"] {
        background-color: #111827 !important;
        color: white !important;
    }

    [role="option"]:hover {
        background-color: #1f2937 !important;
    }

    [data-testid="stNumberInput"] input,
    [data-testid="stTextInput"] input {
        background-color: #1f2937 !important;
        color: white !important;
        border: 1px solid #374151 !important;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #172033, #111827);
        border: 1px solid #263244;
        border-radius: 16px;
        padding: 18px;
    }

    [data-testid="stMetricLabel"] {
        color: #9ca3af !important;
    }

    [data-testid="stMetricValue"] {
        color: white !important;
    }

    .stButton > button {
        background-color: #16a34a !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 12px !important;
    }

    .stButton > button:hover {
        background-color: #22c55e !important;
    }

    .dashboard-title {
        background: linear-gradient(135deg, #111827, #172033);
        border: 1px solid #263244;
        border-radius: 18px;
        padding: 25px;
        margin-bottom: 25px;
    }

    .farmer-card {
        background: linear-gradient(135deg, #111827, #172033);
        border: 1px solid #263244;
        border-radius: 16px;
        padding: 20px;
        margin-top: 15px;
        margin-bottom: 20px;
    }

    .prediction-card {
        background: linear-gradient(135deg, #123524, #10271c);
        border: 1px solid #166534;
        border-radius: 16px;
        padding: 20px;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    .footer {
        text-align: center;
        color: #6b7280;
        padding: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# FIND PROJECT DIRECTORY
# =========================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

possible_project_dirs = [
    CURRENT_DIR,
    os.path.dirname(CURRENT_DIR),
    os.path.dirname(os.path.dirname(CURRENT_DIR))
]

PROJECT_DIR = None

for folder in possible_project_dirs:

    dataset_folder = os.path.join(
        folder,
        "dataset"
    )

    if os.path.isdir(dataset_folder):

        PROJECT_DIR = folder
        break


if PROJECT_DIR is None:

    st.error(
        "❌ Could not find the project directory containing the dataset folder."
    )

    st.stop()


# =========================================================
# DATASET PATH
# =========================================================

DATA_PATH = os.path.join(
    PROJECT_DIR,
    "dataset",
    "Final_Crop_Dashboard_Data.csv"
)


# =========================================================
# CHECK DATASET
# =========================================================

if not os.path.exists(DATA_PATH):

    st.error(
        "❌ Final_Crop_Dashboard_Data.csv was not found."
    )

    st.write("Expected location:")

    st.code(DATA_PATH)

    st.info(
        "Make sure Final_Crop_Dashboard_Data.csv is inside the dataset folder."
    )

    st.stop()


# =========================================================
# LOAD DATASET
# =========================================================

try:

    df = pd.read_csv(DATA_PATH)

except Exception as e:

    st.error(
        f"❌ Could not read the CSV file: {e}"
    )

    st.stop()


# =========================================================
# CLEAN COLUMN NAMES
# =========================================================

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
)


# =========================================================
# REQUIRED COLUMNS
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
        "❌ Required columns are missing from the dataset."
    )

    st.write("Missing columns:")

    st.write(missing_columns)

    st.write("Available columns:")

    st.write(list(df.columns))

    st.stop()


# =========================================================
# CLEAN IMPORTANT DATA
# =========================================================

for column in [
    "State",
    "District",
    "Season",
    "Crop"
]:

    df[column] = (
        df[column]
        .astype(str)
        .str.strip()
    )


df["Risk_Adjusted_Score"] = pd.to_numeric(
    df["Risk_Adjusted_Score"],
    errors="coerce"
)


# =========================================================
# FASTAPI CONNECTION
# =========================================================

backend_connected = False

try:

    response = requests.get(
        f"{API_URL}/",
        timeout=3
    )

    if response.status_code == 200:

        backend_connected = True

except requests.exceptions.RequestException:

    backend_connected = False


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🎯 Crop Decision System")

st.sidebar.markdown("---")

st.sidebar.subheader("📍 Select Location")


# =========================================================
# STATES
# =========================================================

states = sorted(
    df["State"]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
    .tolist()
)


if not states:

    st.error("❌ No states available in the dataset.")

    st.stop()


selected_state = st.sidebar.selectbox(
    "🇮🇳 State",
    states
)


# =========================================================
# STATE DATA
# =========================================================

state_data = df[
    df["State"].astype(str).str.strip()
    == str(selected_state).strip()
].copy()


# =========================================================
# DISTRICTS
# =========================================================

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
        f"⚠️ No districts available for {selected_state}."
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
    state_data["District"].astype(str).str.strip()
    == str(selected_district).strip()
].copy()


# =========================================================
# SEASONS
# =========================================================

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
        "⚠️ No seasons available for the selected district."
    )

    st.stop()


selected_season = st.sidebar.selectbox(
    "🌦️ Season",
    seasons
)


# =========================================================
# SIDEBAR STATUS
# =========================================================

st.sidebar.markdown("---")

st.sidebar.subheader("📌 Current Selection")

st.sidebar.write(
    f"**State:** {selected_state}"
)

st.sidebar.write(
    f"**District:** {selected_district}"
)

st.sidebar.write(
    f"**Season:** {selected_season}"
)

st.sidebar.markdown("---")


if backend_connected:

    st.sidebar.success(
        "🟢 FastAPI API Online"
    )

else:

    st.sidebar.error(
        "🔴 FastAPI API Offline"
    )


# =========================================================
# MAIN TITLE
# =========================================================

st.markdown(
    """
    <div class="dashboard-title">
    """,
    unsafe_allow_html=True
)

st.title("🌾 AI Crop Decision System")

st.write(
    "Intelligent Crop Recommendation & Risk Analysis"
)

st.write(
    "🌾 Production  |  💰 Market Price  |  "
    "💵 Cost  |  🦠 Disease  |  "
    "🌦️ Weather  |  🌱 Soil"
)

st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# =========================================================
# FARMER INPUT
# =========================================================

st.header("👨‍🌾 Farmer Prediction")

st.write(
    "Enter the farmer's field information and "
    "generate an AI-assisted crop recommendation."
)


# =========================================================
# SOIL TYPES
# =========================================================

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


col1, col2, col3 = st.columns(3)


with col1:

    farmer_soil = st.selectbox(
        "🌱 Soil Type",
        soil_types
    )


with col2:

    farmer_land = st.number_input(
        "📐 Land Area (acres)",
        min_value=0.1,
        value=1.0,
        step=0.5
    )


with col3:

    farmer_budget = st.number_input(
        "💰 Budget (₹)",
        min_value=0.0,
        value=50000.0,
        step=5000.0
    )


col4, col5, col6 = st.columns(3)


with col4:

    farmer_water = st.number_input(
        "💧 Water Available (litres)",
        min_value=0.0,
        value=50000.0,
        step=5000.0
    )


with col5:

    st.text_input(
        "🇮🇳 Selected State",
        value=str(selected_state),
        disabled=True
    )


with col6:

    st.text_input(
        "📍 Selected District",
        value=str(selected_district),
        disabled=True
    )


# =========================================================
# FILTER CURRENT DATA
# =========================================================

filtered = district_data[
    district_data["Season"].astype(str).str.strip()
    == str(selected_season).strip()
].copy()


# =========================================================
# SORT CURRENT DATA
# =========================================================

if "Rank" in filtered.columns:

    filtered["Rank"] = pd.to_numeric(
        filtered["Rank"],
        errors="coerce"
    )

    filtered = filtered.sort_values(
        "Rank",
        na_position="last"
    )

else:

    filtered = filtered.sort_values(
        "Risk_Adjusted_Score",
        ascending=False,
        na_position="last"
    )


# =========================================================
# CHECK FILTERED DATA
# =========================================================

if filtered.empty:

    st.warning(
        "⚠️ No recommendation data available for the "
        "selected district and season."
    )

    st.stop()


# =========================================================
# PREDICT BUTTON
# =========================================================

predict_button = st.button(
    "🔮 GET CROP PREDICTION",
    use_container_width=True
)


# =========================================================
# PREDICTION
# =========================================================

if predict_button:

    # -----------------------------------------------------
    # SOIL VALIDATION
    # -----------------------------------------------------

    if farmer_soil == "Select Soil Type":

        st.warning(
            "⚠️ Please select the soil type first."
        )

    # -----------------------------------------------------
    # BACKEND VALIDATION
    # -----------------------------------------------------

    elif not backend_connected:

        st.error(
            "❌ FastAPI backend is not running."
        )

        st.info(
            "Start the FastAPI backend on port 8000 "
            "before clicking the prediction button."
        )

    else:

        # -------------------------------------------------
        # API PAYLOAD
        # -------------------------------------------------

        payload = {

            "state": str(selected_state),

            "district": str(selected_district),

            "season": str(selected_season),

            "soil_type": str(farmer_soil),

            "land_acres": float(farmer_land),

            "water_litres": float(farmer_water),

            "budget": float(farmer_budget)
        }


        st.info(
            "🔄 Generating crop recommendation..."
        )


        # -------------------------------------------------
        # CALL FASTAPI
        # -------------------------------------------------

        try:

            response = requests.post(
                f"{API_URL}/predict",
                json=payload,
                timeout=15
            )


            # =================================================
            # SUCCESS
            # =================================================

            if response.status_code == 200:

                try:

                    result = response.json()

                except ValueError:

                    st.error(
                        "❌ FastAPI returned an invalid JSON response."
                    )

                    st.code(response.text)

                    st.stop()


                # =================================================
                # GET RECOMMENDATIONS
                # =================================================

                recommendations = result.get(
                    "recommendations",
                    []
                )


                if recommendations:

                    top5 = pd.DataFrame(
                        recommendations
                    )

                else:

                    top5 = filtered.head(5).copy()


                # =================================================
                # NORMALIZE API COLUMN NAMES
                # =================================================

                if not top5.empty:

                    # Crop
                    if "Crop" not in top5.columns:

                        if "crop" in top5.columns:

                            top5["Crop"] = top5["crop"]


                    # Risk score
                    if "Risk_Adjusted_Score" not in top5.columns:

                        if "decision_score" in top5.columns:

                            top5["Risk_Adjusted_Score"] = (
                                top5["decision_score"]
                            )

                        elif "score" in top5.columns:

                            top5["Risk_Adjusted_Score"] = (
                                top5["score"]
                            )


                    # Rank
                    if "Rank" not in top5.columns:

                        if "rank" in top5.columns:

                            top5["Rank"] = top5["rank"]


                    # Data coverage
                    if "Data_Coverage" not in top5.columns:

                        if "data_coverage" in top5.columns:

                            top5["Data_Coverage"] = (
                                top5["data_coverage"]
                            )


                # =================================================
                # BEST CROP FROM API
                # =================================================

                best_crop_name = result.get(
                    "best_crop"
                )

                best_score = result.get(
                    "best_score"
                )

                best_rank = result.get(
                    "best_rank"
                )


                # =================================================
                # FALLBACK BEST CROP
                # =================================================

                if not best_crop_name:

                    if not top5.empty and "Crop" in top5.columns:

                        best_crop_name = (
                            top5.iloc[0]["Crop"]
                        )

                    else:

                        best_crop_name = (
                            filtered.iloc[0]["Crop"]
                        )


                # =================================================
                # FALLBACK SCORE
                # =================================================

                if best_score is None:

                    if (
                        not top5.empty
                        and "Risk_Adjusted_Score" in top5.columns
                    ):

                        best_score = (
                            top5.iloc[0][
                                "Risk_Adjusted_Score"
                            ]
                        )

                    else:

                        best_score = (
                            filtered.iloc[0][
                                "Risk_Adjusted_Score"
                            ]
                        )


                # =================================================
                # FALLBACK RANK
                # =================================================

                if best_rank is None:

                    if (
                        not top5.empty
                        and "Rank" in top5.columns
                    ):

                        best_rank = (
                            top5.iloc[0]["Rank"]
                        )

                    else:

                        best_rank = 1


                # =================================================
                # FIND BEST CROP DETAILS
                # =================================================

                matching_crop = filtered[
                    filtered["Crop"]
                    .astype(str)
                    .str.strip()
                    ==
                    str(best_crop_name)
                    .strip()
                ]


                if not matching_crop.empty:

                    best_crop = matching_crop.iloc[0]

                else:

                    best_crop = filtered.iloc[0]


                # =================================================
                # PREDICTION RESULT
                # =================================================

                st.divider()

                st.header(
                    "🔮 Prediction Result"
                )


                result1, result2, result3 = st.columns(3)


                with result1:

                    st.metric(
                        "🌾 Predicted Best Crop",
                        str(best_crop_name)
                    )


                with result2:

                    try:

                        st.metric(
                            "⭐ Decision Score",
                            f"{float(best_score):.2f}"
                        )

                    except (ValueError, TypeError):

                        st.metric(
                            "⭐ Decision Score",
                            "N/A"
                        )


                with result3:

                    try:

                        st.metric(
                            "🏅 Rank",
                            int(float(best_rank))
                        )

                    except (ValueError, TypeError):

                        st.metric(
                            "🏅 Rank",
                            "N/A"
                        )


                st.write(
                    f"🌱 **Soil:** {farmer_soil}"
                )

                st.write(
                    f"🌦️ **Season:** {selected_season}"
                )

                st.write(
                    f"📍 **District:** {selected_district}"
                )

                st.write(
                    f"📐 **Land:** {farmer_land:,.1f} acres"
                )

                st.write(
                    f"💰 **Budget:** ₹{farmer_budget:,.0f}"
                )

                st.write(
                    f"💧 **Water:** {farmer_water:,.0f} litres"
                )


                st.success(
                    f"🌾 Recommended crop: "
                    f"**{best_crop_name}**"
                )


                # =================================================
                # TOP 5 RECOMMENDATIONS
                # =================================================

                st.divider()

                st.subheader(
                    f"🌱 Top 5 Crop Recommendations — "
                    f"{selected_district} "
                    f"({selected_season})"
                )


                if not top5.empty:

                    top5 = top5.head(5).copy()


                    preferred_columns = [

                        "Rank",

                        "Crop",

                        "Risk_Adjusted_Score",

                        "Data_Coverage"
                    ]


                    available_columns = [

                        column

                        for column in preferred_columns

                        if column in top5.columns
                    ]


                    if available_columns:

                        display_data = top5[
                            available_columns
                        ].copy()


                        display_data = display_data.rename(
                            columns={

                                "Rank":
                                    "🏅 Rank",

                                "Crop":
                                    "🌱 Crop",

                                "Risk_Adjusted_Score":
                                    "⭐ Decision Score",

                                "Data_Coverage":
                                    "📊 Data Coverage"
                            }
                        )


                        st.dataframe(
                            display_data,
                            use_container_width=True,
                            hide_index=True
                        )

                    else:

                        st.dataframe(
                            top5,
                            use_container_width=True,
                            hide_index=True
                        )


                # =================================================
                # SCORE CHART
                # =================================================

                st.subheader(
                    "📊 Crop Decision Score"
                )


                if (
                    "Crop" in top5.columns
                    and
                    "Risk_Adjusted_Score" in top5.columns
                ):

                    chart_data = top5[
                        [
                            "Crop",
                            "Risk_Adjusted_Score"
                        ]
                    ].copy()


                    chart_data[
                        "Risk_Adjusted_Score"
                    ] = pd.to_numeric(
                        chart_data[
                            "Risk_Adjusted_Score"
                        ],
                        errors="coerce"
                    )


                    chart_data = chart_data.dropna(
                        subset=["Risk_Adjusted_Score"]
                    )


                    if not chart_data.empty:

                        chart_data = (
                            chart_data
                            .set_index("Crop")
                        )


                        st.bar_chart(
                            chart_data
                        )

                    else:

                        st.info(
                            "Decision score chart is not available."
                        )

                else:

                    st.info(
                        "Decision score data is not available."
                    )


                # =================================================
                # WHY THIS CROP?
                # =================================================

                st.divider()

                st.subheader(
                    "🔍 Why is this crop recommended?"
                )


                factor_columns = [

                    (
                        "🌾 Yield",
                        "Yield (quintals)"
                    ),

                    (
                        "📦 Production",
                        "Production (metric tons)"
                    ),

                    (
                        "💰 Average Price",
                        "Average_Price"
                    ),

                    (
                        "📈 Price Volatility",
                        "Price_Volatility"
                    ),

                    (
                        "📈 Price Trend",
                        "Price_Trend"
                    ),

                    (
                        "💵 Cultivation Cost",
                        "Cost_of_Cultivation"
                    ),

                    (
                        "🦠 Disease Risk",
                        "Disease_Risk"
                    ),

                    (
                        "🌦️ Weather Risk",
                        "Weather_Risk"
                    )
                ]


                factor_data = []


                for title, column in factor_columns:

                    if column in best_crop.index:

                        value = best_crop[column]

                        if pd.notna(value):

                            try:

                                numeric_value = float(value)

                                factor_data.append(
                                    {
                                        "🔎 Factor": title,

                                        "📊 Value": round(
                                            numeric_value,
                                            2
                                        )
                                    }
                                )

                            except (
                                ValueError,
                                TypeError
                            ):

                                factor_data.append(
                                    {
                                        "🔎 Factor": title,

                                        "📊 Value": str(value)
                                    }
                                )


                if factor_data:

                    st.dataframe(
                        pd.DataFrame(
                            factor_data
                        ),
                        use_container_width=True,
                        hide_index=True
                    )

                else:

                    st.info(
                        "Factor details are not available."
                    )


                # =================================================
                # SELECTED CROP DETAILS
                # =================================================

                st.divider()

                st.subheader(
                    "🌾 Selected Crop Details"
                )


                d1, d2, d3 = st.columns(3)


                with d1:

                    if "Area (hectares)" in best_crop.index:

                        try:

                            st.metric(
                                "📐 Area",
                                f"{float(best_crop['Area (hectares)']):,.2f} ha"
                            )

                        except (ValueError, TypeError):

                            st.metric(
                                "📐 Area",
                                str(
                                    best_crop[
                                        "Area (hectares)"
                                    ]
                                )
                            )


                with d2:

                    if "Yield (quintals)" in best_crop.index:

                        try:

                            st.metric(
                                "🌾 Yield",
                                f"{float(best_crop['Yield (quintals)']):,.2f}"
                            )

                        except (ValueError, TypeError):

                            st.metric(
                                "🌾 Yield",
                                str(
                                    best_crop[
                                        "Yield (quintals)"
                                    ]
                                )
                            )


                with d3:

                    if "Production (metric tons)" in best_crop.index:

                        try:

                            st.metric(
                                "📦 Production",
                                f"{float(best_crop['Production (metric tons)']):,.2f} MT"
                            )

                        except (ValueError, TypeError):

                            st.metric(
                                "📦 Production",
                                str(
                                    best_crop[
                                        "Production (metric tons)"
                                    ]
                                )
                            )


                d4, d5, d6 = st.columns(3)


                with d4:

                    if "Average_Price" in best_crop.index:

                        try:

                            st.metric(
                                "💰 Average Price",
                                f"₹{float(best_crop['Average_Price']):,.2f}"
                            )

                        except (ValueError, TypeError):

                            st.metric(
                                "💰 Average Price",
                                str(
                                    best_crop[
                                        "Average_Price"
                                    ]
                                )
                            )


                with d5:

                    if "Cost_of_Cultivation" in best_crop.index:

                        try:

                            st.metric(
                                "💵 Cultivation Cost",
                                f"₹{float(best_crop['Cost_of_Cultivation']):,.2f}"
                            )

                        except (ValueError, TypeError):

                            st.metric(
                                "💵 Cultivation Cost",
                                str(
                                    best_crop[
                                        "Cost_of_Cultivation"
                                    ]
                                )
                            )


                with d6:

                    if "Disease_Risk" in best_crop.index:

                        try:

                            st.metric(
                                "🦠 Disease Risk",
                                f"{float(best_crop['Disease_Risk']):.2f}"
                            )

                        except (ValueError, TypeError):

                            st.metric(
                                "🦠 Disease Risk",
                                str(
                                    best_crop[
                                        "Disease_Risk"
                                    ]
                                )
                            )


                # =================================================
                # WEATHER INFORMATION
                # =================================================

                st.divider()

                st.subheader(
                    "🌦️ Weather Information"
                )


                weather_columns = [

                    "Average_Temperature",

                    "Max_Temperature",

                    "Min_Temperature",

                    "Total_Rainfall",

                    "Average_Wind_Speed",

                    "Weather_Risk",

                    "Weather_Score"
                ]


                weather_data = {}


                for column in weather_columns:

                    if column in best_crop.index:

                        value = best_crop[column]

                        if pd.notna(value):

                            try:

                                weather_data[column] = round(
                                    float(value),
                                    2
                                )

                            except (
                                ValueError,
                                TypeError
                            ):

                                weather_data[column] = str(value)


                if weather_data:

                    weather_display = pd.DataFrame(
                        [weather_data]
                    )

                    st.dataframe(
                        weather_display,
                        use_container_width=True,
                        hide_index=True
                    )

                else:

                    st.info(
                        "Weather information is not available."
                    )


                # =================================================
                # SOIL INFORMATION
                # =================================================

                st.divider()

                st.subheader(
                    "🌱 Soil Information"
                )


                soil_columns = [

                    "Soil Type",

                    "pH Level",

                    "Organic Matter (%)",

                    "Nitrogen Content (kg/ha)",

                    "Phosphorus Content (kg/ha)",

                    "Potassium Content (kg/ha)"
                ]


                soil_data = {}


                for column in soil_columns:

                    if column in best_crop.index:

                        value = best_crop[column]

                        if pd.notna(value):

                            soil_data[column] = value


                if soil_data:

                    st.dataframe(
                        pd.DataFrame(
                            [soil_data]
                        ),
                        use_container_width=True,
                        hide_index=True
                    )

                else:

                    st.info(
                        "Soil information is not available."
                    )


                # =================================================
                # API MARKET NOTE
                # =================================================

                market_note = result.get(
                    "market_price_note"
                )


                if market_note:

                    st.info(
                        f"ℹ️ {market_note}"
                    )


            # =================================================
            # API ERROR
            # =================================================

            else:

                st.error(
                    f"❌ Prediction API returned "
                    f"status code {response.status_code}"
                )


                try:

                    error_data = response.json()

                    st.code(
                        str(error_data)
                    )

                except ValueError:

                    st.code(
                        response.text
                    )


        # =================================================
        # CONNECTION ERROR
        # =================================================

        except requests.exceptions.RequestException as e:

            st.error(
                f"❌ Could not connect to prediction API: {e}"
            )


# =========================================================
# PROJECT OVERVIEW
# =========================================================

st.divider()

st.header(
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