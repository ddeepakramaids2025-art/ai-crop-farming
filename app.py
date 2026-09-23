import os
import sys
import json
import io
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIGURATION & METADATA
# ============================================================

st.set_page_config(
    page_title="🌾 Crop Decision System | பயிர் முடிவு அமைப்பு",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# DIRECTORIES & PATH SETUP
# ============================================================

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
DATASET_DIR = PROJECT_DIR / "dataset"
DS_PROJECT_DIR = PROJECT_DIR / "ds_project"
DS_PROJECT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# PROFESSIONAL LIGHT THEME STYLING
# ============================================================

st.markdown(
    """
    <style>
    /* Global Clean Light Theme */
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Sidebar Styling - Clean Light White */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] * {
        color: #1e293b !important;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #0f172a !important;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #065f46 0%, #059669 100%);
        border-radius: 16px;
        padding: 24px 30px;
        color: #ffffff !important;
        box-shadow: 0 4px 20px rgba(5, 150, 105, 0.15);
        margin-bottom: 24px;
    }
    .hero-banner h1 {
        color: #ffffff !important;
        font-size: 2.2rem;
        margin: 0;
        font-weight: 800;
    }
    .hero-banner p {
        color: #ecfdf5 !important;
        font-size: 1.05rem;
        margin: 8px 0 0 0;
        font-weight: 400;
    }

    /* Recommendation Hero Card */
    .best-crop-card {
        background: #ffffff;
        border: 2px solid #10b981;
        border-radius: 16px;
        padding: 24px 28px;
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.1);
        margin-bottom: 18px;
    }

    /* Analysis 6 Metric Cards */
    .analysis-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        height: 100%;
    }
    .analysis-card-title {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .analysis-row {
        display: flex;
        justify-content: space-between;
        margin-top: 6px;
        font-size: 0.85rem;
        color: #475569;
    }
    .analysis-val {
        font-weight: 700;
        color: #0f172a;
    }

    /* Badges */
    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .badge-green {
        background: #ecfdf5;
        color: #059669;
        border: 1px solid #a7f3d0;
    }

    /* Form Buttons */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: #ffffff;
        font-weight: 700;
        font-size: 1.05rem;
        padding: 12px 24px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3);
        transition: all 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #047857 0%, #059669 100%);
        box-shadow: 0 6px 18px rgba(16, 185, 129, 0.4);
        transform: translateY(-1px);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 5-LANGUAGE TRANSLATION DICTIONARIES
# ============================================================

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "English": {
        "app_title": "Crop Decision System",
        "app_subtitle": "Farmer Decision-Support & Agro-Climatic Intelligence Platform",
        "app_tagline": "Yield Potential • Mandi Prices • Cultivation Cost • Disease Protection • Water Security",
        "select_lang": "🌐 Language / மொழி / भाषा / భాష / ഭാഷ",
        "location_header": "📍 Location Selection",
        "state_label": "🇮🇳 State",
        "district_label": "📍 District",
        "season_label": "🌦️ Season",
        "farmer_header": "👨‍🌾 Farmer & Field Specifications",
        "farmer_desc": "Enter your farm parameters below to calculate the most profitable and safe crop recommendation.",
        "soil_label": "🌱 Soil Type",
        "land_label": "📐 Land Area (acres)",
        "budget_label": "💰 Available Budget (₹)",
        "water_label": "💧 Available Water (litres)",
        "btn_predict": "🌾 GET CROP ADVISORY & RECOMMENDATION",
        "pred_result_header": "🌾 Recommended Crop & Farm Advisory",
        "pred_best_crop": "🌾 Best Recommended Crop",
        "pred_decision_score": "Suitability Rating",
        "pred_rank": "Recommendation Rank",
        "best_crop_announcement": "Top Recommended Crop: **{crop}** (Suitability Score: {score}/100)",
        "why_this_crop": "🌾 Why is this crop the best choice for your farm?",
        "top5_header": "🌱 Top Recommended Alternative Crops",
        "col_rank": "Rank", "col_crop": "Crop", "col_score": "Suitability Score", "col_coverage": "Data Status",
        "col_revenue": "Expected Harvest Value (₹)", "col_cost": "Cultivation Expense (₹)", "col_water": "Water Required (L)",
        "col_yield": "Expected Yield (q)", "col_disease": "Disease Risk (%)", "col_weather": "Weather Risk (%)",
        "btn_download_json": "📥 Download JSON Report", "btn_download_csv": "📥 Download CSV Table",
        "btn_clear": "🔄 Clear / New Advisory",
        "api_online": "🟢 Agriculture Database Active",
        "tab_eda": "📊 Exploratory Data Analysis (EDA)",
        "tab_advisory": "🌾 Farm Crop Advisory",
        "ready_title": "Ready to Analyze Your Farm",
        "ready_desc": "Select your State, District, and Season in the sidebar, verify your Soil, Land, Budget, and Water above, then click GET CROP ADVISORY & RECOMMENDATION to view personalized recommendations."
    },
    "தமிழ்": {
        "app_title": "பயிர் முடிவு அமைப்பு",
        "app_subtitle": "விவசாயிகளுக்கான லாபகரமான பயிர் முடிவெடுக்கும் தளம்",
        "app_tagline": "மகசூல் பகுப்பாய்வு • சந்தை விலை • சாகுபடி செலவு • நோய் பாதுகாப்பு • நீர் மேலாண்மை",
        "select_lang": "🌐 Language / மொழி / भाषा / భాష / ഭാഷ",
        "location_header": "📍 இருப்பிட தேர்வு",
        "state_label": "🇮🇳 மாநிலம்",
        "district_label": "📍 மாவட்டம்",
        "season_label": "🌦️ பருவம்",
        "farmer_header": "👨‍🌾 விவசாயி மற்றும் நில விவரங்கள்",
        "farmer_desc": "உங்கள் நிலத்திற்கு அதிக லாபம் தரும் பயிர் பரிந்துரையைப் பெற விவரங்களை உள்ளிடவும்.",
        "soil_label": "🌱 மண் வகை",
        "land_label": "📐 நிலப்பரப்பு (ஏக்கர்)",
        "budget_label": "💰 கிடைக்கும் பட்ஜெட் (₹)",
        "water_label": "💧 கிடைக்கும் நீர் (லிட்டர்)",
        "btn_predict": "🌾 பயிர் ஆலோசனை & பரிந்துரையைப் பெறுங்கள்",
        "pred_result_header": "🌾 பரிந்துரைக்கப்பட்ட பயிர் & பண்ணை ஆலோசனை",
        "pred_best_crop": "🌾 சிறந்த பரிந்துரை பயிர்",
        "pred_decision_score": "பொருத்த நிலை",
        "pred_rank": "பரிந்துரை தரம்",
        "best_crop_announcement": "சிறந்த பரிந்துரைக்கப்பட்ட பயிர்: **{crop}** (பொருத்த நிலை: {score}/100)",
        "why_this_crop": "🌾 இந்த பயிர் உங்கள் நிலத்திற்கு ஏன் சிறந்த தேர்வு?",
        "top5_header": "🌱 முதல் 5 மாற்று பயிர் பரிந்துரைகள்",
        "col_rank": "தரம்", "col_crop": "பயிர்", "col_score": "பொருத்த நிலை", "col_coverage": "தரவு நிலை",
        "col_revenue": "அறுவடை மதிப்பு (₹)", "col_cost": "சாகுபடி செலவு (₹)", "col_water": "தேவைப்படும் நீர் (லி)",
        "col_yield": "எதிர்பார்க்கும் மகசூல் (கு)", "col_disease": "நோய் அபாயம் (%)", "col_weather": "வானிலை அபாயம் (%)",
        "btn_download_json": "📥 JSON அறிக்கை பதிவிறக்கம்", "btn_download_csv": "📥 CSV அட்டவணை பதிவிறக்கம்",
        "btn_clear": "🔄 புதிய ஆலோசனை (மீட்டமை)",
        "api_online": "🟢 வேளாண் தரவுத்தளம் இயங்குகிறது",
        "tab_eda": "📊 விளக்க தரவு பகுப்பாய்வு (EDA)",
        "tab_advisory": "🌾 பயிர் ஆலோசனை தளம்",
        "ready_title": "பயிர் ஆலோசனையை பெற தயார்",
        "ready_desc": "இடப்பக்க மெனுவில் மாநிலம், மாவட்டத்தைத் தேர்ந்தெடுத்து, நிலப்பரப்பு மற்றும் விவரங்களை உள்ளிட்ட பிறகு பரிந்துரை பொத்தானை அழுத்தவும்."
    },
    "हिन्दी": {
        "app_title": "फसल निर्णय प्रणाली",
        "app_subtitle": "किसानों के लिए व्यावहारिक एवं लाभ-केंद्रित कृषि निर्णय प्रणाली",
        "app_tagline": "उपज विश्लेषण • मंडी भाव • खेती लागत • रोग सुरक्षा • जल प्रबंधन",
        "select_lang": "🌐 Language / மொழி / भाषा / భాష / ഭാഷ",
        "location_header": "📍 स्थान चयन",
        "state_label": "🇮🇳 राज्य",
        "district_label": "📍 ज़िला",
        "season_label": "🌦️ मौसम (सीज़न)",
        "farmer_header": "👨‍🌾 किसान एवं खेत विवरण",
        "farmer_desc": "सटीक एवं लाभकारी फसल अनुशंसा प्राप्त करने के लिए अपनी कृषि जानकारी दर्ज करें।",
        "soil_label": "🌱 मिट्टी का प्रकार",
        "land_label": "📐 भूमि क्षेत्र (एकड़)",
        "budget_label": "💰 उपलब्ध बजट (₹)",
        "water_label": "💧 उपलब्ध जल (लीटर)",
        "btn_predict": "🌾 फसल सलाह एवं अनुशंसा प्राप्त करें",
        "pred_result_header": "🌾 अनुशंसित फसल एवं कृषि परामर्श",
        "pred_best_crop": "🌾 सर्वश्रेष्ठ अनुशंसित फसल",
        "pred_decision_score": "उपयुक्तता स्कोर",
        "pred_rank": "अनुशंसित रैंक",
        "best_crop_announcement": "सर्वोत्तम अनुशंसित फसल: **{crop}** (उपयुक्तता स्कोर: {score}/100)",
        "why_this_crop": "🌾 यह फसल आपके खेत के लिए क्यों उत्तम है?",
        "top5_header": "🌱 शीर्ष अनुशंसित वैकल्पिक फसलें",
        "col_rank": "रैंक", "col_crop": "फसल", "col_score": "उपयुक्तता स्कोर", "col_coverage": "डेटा स्थिति",
        "col_revenue": "अपेक्षित उपज मूल्य (₹)", "col_cost": "खेती लागत (₹)", "col_water": "आवश्यक जल (लीटर)",
        "col_yield": "अपेक्षित पैदावार (क्विंटल)", "col_disease": "रोग जोखिम (%)", "col_weather": "मौसम जोखिम (%)",
        "btn_download_json": "📥 JSON रिपोर्ट डाउनलोड करें", "btn_download_csv": "📥 CSV तालिका डाउनलोड करें",
        "btn_clear": "🔄 नई सलाह (रीसेट)",
        "api_online": "🟢 कृषि डेटाबेस सक्रिय",
        "tab_eda": "📊 अन्वेषणात्मक डेटा विश्लेषण (EDA)",
        "tab_advisory": "🌾 किसान फसल सलाहकार",
        "ready_title": "खेत विश्लेषण के लिए तैयार",
        "ready_desc": "साइडबार में राज्य व जिला चुनें, ऊपर अपने खेत का विवरण भरें और फसल सलाह प्राप्त करने के लिए बटन दबाएं।"
    },
    "తెలుగు": {
        "app_title": "పంట నిర్ణయ వ్యవస్థ",
        "app_subtitle": "రైతుల కోసం అనుకూలమైన వ్యవసాయ నిర్ణయ వేదిక",
        "app_tagline": "దిగుబడి విశ్లేషణ • మార్కెట్ ధరలు • సాగు ఖర్చు • తెగుళ్ల భద్రత • నీటి భద్రత",
        "select_lang": "🌐 Language / மொழி / भाषा / భాష / ഭാష",
        "location_header": "📍 ప్రాంతం ఎంపిక",
        "state_label": "🇮🇳 రాష్ట్రం",
        "district_label": "📍 జిల్లా",
        "season_label": "🌦️ కాలం (సీజన్)",
        "farmer_header": "👨‍🌾 రైతు మరియు పొలం వివరాలు",
        "farmer_desc": "సరియైన మరియు లాభదాయకమైన పంట సిఫార్సుల కోసం వివరాలను నమోదు చేయండి.",
        "soil_label": "🌱 నేల రకం",
        "land_label": "📐 విస్తీర్ణం (ఎకరాలు)",
        "budget_label": "💰 బడ్జెట్ (₹)",
        "water_label": "💧 అందుబాటులో ఉన్న నీరు (లీటర్లు)",
        "btn_predict": "🌾 పంట సలహా & సిఫార్సును పొందండి",
        "pred_result_header": "🌾 సిఫార్సు చేసిన పంట & వ్యవసాయ సలహా",
        "pred_best_crop": "🌾 ఉత్తమ పంట",
        "pred_decision_score": "అనుకూలత స్కోరు",
        "pred_rank": "సిఫార్సు ర్యాంక్",
        "best_crop_announcement": "ఉత్తమ సిఫార్సు పంట: **{crop}** (స్కోరు: {score}/100)",
        "why_this_crop": "🌾 ఈ పంట మీ పొలానికి ఎందుకు ఉత్తమ ఎంపిక?",
        "top5_header": "🌱 ప్రత్యామ్నాయ పంటల సిఫార్సులు",
        "col_rank": "ర్యాంక్", "col_crop": "పంట", "col_score": "స్కోరు", "col_coverage": "డేటా స్థితి",
        "col_revenue": "దిగుబడి విలువ (₹)", "col_cost": "సాగు ఖర్చు (₹)", "col_water": "అవసరమైన నీరు (లీ)",
        "col_yield": "దిగుబడి (క్వింటాళ్లు)", "col_disease": "తెగుళ్ల ప్రమాదం (%)", "col_weather": "వాతావరణ ప్రమాదం (%)",
        "btn_download_json": "📥 JSON డౌన్‌లోడ్", "btn_download_csv": "📥 CSV డౌన్‌లోడ్",
        "btn_clear": "🔄 కొత్త సలహా (రీసెట్)",
        "api_online": "🟢 వ్యవసాయ డేటాబేస్ ఆన్‌లైన్",
        "tab_eda": "📊 డేటా విశ్లేషణ (EDA)",
        "tab_advisory": "🌾 పంట సలహా వేదిక",
        "ready_title": "మీ పొలాన్ని విశ్లేషించడానికి సిద్ధంగా ఉంది",
        "ready_desc": "సైడ్‌బార్‌లో రాష్ట్రం మరియు జిల్లాను ఎంచుకోండి, వివరాలను నమోదు చేసి బటన్ నొక్కండి."
    },
    "മലയാളം": {
        "app_title": "വിള നിർണ്ണയ സംവിധാനം",
        "app_subtitle": "കർഷകർക്കായുള്ള പ്രായോഗിക കാർഷിക തീരുമാന പ്ലാറ്റ്‌ഫോം",
        "app_tagline": "വിളവ് വിശകലനം • വിപണി വില • കൃഷിച്ചെലവ് • രോഗ സംരക്ഷണം • ജല ലഭ്യത",
        "select_lang": "🌐 Language / மொழி / भाषा / భాష / ഭാഷ",
        "location_header": "📍 സ്ഥലം തിരഞ്ഞെടുക്കൽ",
        "state_label": "🇮🇳 സംസ്ഥാനം",
        "district_label": "📍 ജില്ല",
        "season_label": "🌦️ കൃഷി സീസൺ",
        "farmer_header": "👨‍🌾 കർഷകനും കൃഷിയിട വിവരങ്ങളും",
        "farmer_desc": "കൃത്യമായതും ലാഭകരവുമായ വിള നിർദ്ദേശങ്ങൾ ലഭിക്കുന്നതിന് വിവരങ്ങൾ നൽകുക.",
        "soil_label": "🌱 മണ്ണ് തരം",
        "land_label": "📐 വിസ്തീർണ്ണം (ഏക്കർ)",
        "budget_label": "💰 ലഭ്യമായ ബജറ്റ് (₹)",
        "water_label": "💧 ലഭ്യമായ ജലം (ലിറ്റർ)",
        "btn_predict": "🌾 വിള ഉപദേശവും ശുപാർശയും നേടുക",
        "pred_result_header": "🌾 ശുപാർശ ചെയ്ത വിളയും കാർഷിക ഉപദേശവും",
        "pred_best_crop": "🌾 ഏറ്റവും അനുയോജ്യമായ വിള",
        "pred_decision_score": "അനുയോജ്യത സ്കോർ",
        "pred_rank": "റാങ്ക്",
        "best_crop_announcement": "ഏറ്റവും അനുയോജ്യമായ വിള: **{crop}** (സ്കോർ: {score}/100)",
        "why_this_crop": "🌾 എന്തുകൊണ്ട് ഈ വിള നിങ്ങളുടെ കൃഷിയിടത്തിന് അനുയോജ്യമാണ്?",
        "top5_header": "🌱 മറ്റ് അനുയോജ്യമായ വിളകൾ",
        "col_rank": "റാങ്ക്", "col_crop": "വിള", "col_score": "സ്കോർ", "col_coverage": "ലഭ്യത",
        "col_revenue": "പ്രതീക്ഷിക്കുന്ന വരുമാനം (₹)", "col_cost": "കൃഷിച്ചെലവ് (₹)", "col_water": "ആവശ്യമായ ജലം (ലി)",
        "col_yield": "വിളവ് (ക്വിന്റൽ)", "col_disease": "രോഗസാധ്യത (%)", "col_weather": "കാലാവസ്ഥാ ഭീഷണി (%)",
        "btn_download_json": "📥 JSON ഡൗൺലോഡ്", "btn_download_csv": "📥 CSV പട്ടിക ഡൗൺലോഡ്",
        "btn_clear": "🔄 പുതിയ ഉപദേശം (റീസെറ്റ്)",
        "api_online": "🟢 കാർഷിക ഡാറ്റാബേസ് ഓൺലൈൻ",
        "tab_eda": "📊 ഡാറ്റാ അനലിറ്റിക്സ് (EDA)",
        "tab_advisory": "🌾 വിള ഉപദേശ പോർട്ടൽ",
        "ready_title": "വിള ഉപദേശം നേടാൻ തയ്യാറാണ്",
        "ready_desc": "സംസ്ഥാനവും ജില്ലയും തിരഞ്ഞെടുത്ത് വിവരങ്ങൾ നൽകിയ ശേഷം ബട്ടൺ ക്ലിക്ക് ചെയ്യുക."
    }
}

def t(key: str, **kwargs) -> str:
    lang = st.session_state.get("selected_language_code", "English")
    text = TRANSLATIONS.get(lang, {}).get(key, TRANSLATIONS["English"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text

CROPS_TRANSLATION = {
    "Paddy":       {"தமிழ்": "நெல் (Paddy)",       "हिन्दी": "धान (Paddy)",      "తెలుగు": "వరి (Paddy)",      "മലയാളം": "നെല്ല് (Paddy)"},
    "Wheat":       {"தமிழ்": "கோதுமை (Wheat)",    "हिन्दी": "गेहूं (Wheat)",    "తెలుగు": "గోధుమ (Wheat)",    "മലയാളം": "ഗോതമ്പ് (Wheat)"},
    "Maize":       {"தமிழ்": "மக்காச்சோளம் (Maize)","हिन्दी": "मक्का (Maize)",    "తెలుగు": "మొక్కజొన్న (Maize)", "മലയാളം": "മക്കച്ചോളം (Maize)"},
    "Cotton":      {"தமிழ்": "பருத்தி (Cotton)",   "हिन्दी": "कपास (Cotton)",    "తెలుగు": "ప్రత్తి (Cotton)",    "മലയാളം": "പരുത്തി (Cotton)"},
    "Sugarcane":   {"தமிழ்": "கரும்பு (Sugarcane)","हिन्दी": "गन्ना (Sugarcane)", "తెలుగు": "చెరకు (Sugarcane)", "മലയാളം": "കരിമ്പ് (Sugarcane)"},
    "Groundnut":   {"தமிழ்": "நிலக்கடலை (Groundnut)","हिन्दी": "मूंगफली (Groundnut)","తెలుగు": "వేరుశనగ (Groundnut)","മലയാളം": "നിലക്കടല (Groundnut)"},
    "Soyabean":    {"தமிழ்": "சோயாபீன் (Soyabean)","हिन्दी": "सोयाबीन (Soyabean)","తెలుగు": "సోయాబీన్ (Soyabean)","മലയാളം": "സോയാബീൻ (Soyabean)"},
    "Bajra":       {"தமிழ்": "கம்பு (Bajra)",      "हिन्दी": "बाजरा (Bajra)",    "తెలుగు": "సజ్జలు (Bajra)",    "മലയാളം": "കമ്പം (Bajra)"},
    "Jowar":       {"தமிழ்": "சோளம் (Jowar)",      "हिन्दी": "ज्वार (Jowar)",    "తెలుగు": "జొన్నలు (Jowar)",    "മലയാളം": "ചോളം (Jowar)"},
    "Mustard":     {"தமிழ்": "கடுகு (Mustard)",    "हिन्दी": "सरसों (Mustard)",  "తెలుగు": "ఆవాలు (Mustard)",   "മലയാളം": "കടുക് (Mustard)"},
    "Gram":        {"தமிழ்": "கடலை (Gram)",       "हिन्दी": "चना (Gram)",       "తెలుగు": "శనగలు (Gram)",      "മലയാളം": "കടല (Gram)"},
    "Moong":       {"தமிழ்": "பாசிப்பயறு (Moong)", "हिन्दी": "मूंग (Moong)",      "తెలుగు": "పెసలు (Moong)",     "മലയാളം": "ചെറുപയർ (Moong)"},
    "Urad":        {"தமிழ்": "உளுந்து (Urad)",     "हिन्दी": "उड़द (Urad)",      "తెలుగు": "మినుములు (Urad)",   "മലയാളം": "ഉഴുന്ന് (Urad)"},
    "Sesamum":     {"தமிழ்": "எள் (Sesamum)",      "हिन्दी": "तिल (Sesamum)",    "తెలుగు": "నువ్వులు (Sesamum)", "മലയാളം": "എള്ള് (Sesamum)"},
    "Tomato":      {"தமிழ்": "தக்காளி (Tomato)",   "हिन्दी": "टमाटर (Tomato)",   "తెలుగు": "టమాటా (Tomato)",    "മലയാളം": "തക്കാളി (Tomato)"},
    "Onion":       {"தமிழ்": "வெங்காயம் (Onion)", "हिन्दी": "प्याज (Onion)",     "తెలుగు": "ఉల్లిపాయ (Onion)",  "മലയാളം": "സവാള (Onion)"},
    "Potato":      {"தமிழ்": "உருளைக்கிழங்கு (Potato)","हिन्दी": "आलू (Potato)",  "తెలుగు": "బంగాళాదుంప (Potato)","മലയാളം": "ഉരുളക്കിഴങ്ങ് (Potato)"}
}

STATES_TRANSLATION = {
    "Tamil Nadu":     {"தமிழ்": "தமிழ்நாடு",      "हिन्दी": "तमिलनाडु",      "తెలుగు": "తమిళనాడు",     "മലയാളം": "തമിഴ്‌നാട്"},
    "Andhra Pradesh": {"தமிழ்": "ஆந்திரப் பிரதேசம்","हिन्दी": "आंध्र प्रदेश",   "తెలుగు": "ఆంధ్రప్రదేశ్",  "മലയാളം": "ആന്ധ്രാപ്രദേശ്"},
    "Telangana":      {"தமிழ்": "தெலுங்கானா",    "हिन्दी": "तेलंगाना",       "తెలుగు": "తెలంగాణ",      "മലയാളം": "തെലങ്കാന"},
    "Karnataka":      {"தமிழ்": "கர்நாடகா",      "हिन्दी": "कर्नाटक",        "తెలుగు": "కర్ణాటక",       "മലയാളം": "കർണാടക"},
    "Kerala":         {"தமிழ்": "கேரளா",          "हिन्दी": "केरल",           "తెలుగు": "కేరళ",         "മലയാളം": "കേരളം"},
    "Maharashtra":    {"தமிழ்": "மகாராஷ்டிரா",   "हिन्दी": "महाराष्ट्र",     "తెలుగు": "మహారాష్ట్ర",    "മലയാളം": "മഹാരാഷ്ട്ര"},
    "Gujarat":        {"தமிழ்": "குஜராத்",        "हिन्दी": "गुजरात",         "తెలుగు": "గుజరాత్",       "മലയാളം": "ഗുജറാത്ത്"},
    "Rajasthan":      {"தமிழ்": "ராஜஸ்தான்",     "हिन्दी": "राजस्थान",       "తెలుగు": "రాజస్థాన్",     "മലയാളം": "രാജസ്ഥാൻ"},
    "Punjab":         {"தமிழ்": "பஞ்சாப்",        "हिन्दी": "पंजाब",          "తెలుగు": "పంజాబ్",       "മലയാളം": "പഞ്ചാബ്"},
    "Haryana":        {"தமிழ்": "ஹரியானா",       "हिन्दी": "हरियाणा",        "తెలుగు": "హర్యానా",      "മലയാളം": "ഹരിയാന"},
    "Uttar Pradesh":  {"தமிழ்": "உத்தரப் பிரதேசம்","हिन्दी": "उत्तर प्रदेश",   "తెలుగు": "ఉత్తర ప్రదేశ్", "മലയാളം": "ഉത്തർപ്രദേശ്"},
    "Madhya Pradesh": {"தமிழ்": "மத்தியப் பிரதேசம்","हिन्दी": "मध्य प्रदेश",   "తెలుగు": "మధ్యప్రదేశ్",   "മലയാളം": "മധ്യപ്രദേശ്"},
    "Bihar":          {"தமிழ்": "பீகார்",          "हिन्दी": "बिहार",          "తెలుగు": "బీహార్",        "മലയാളം": "ബിഹാർ"},
    "West Bengal":    {"தமிழ்": "மேற்கு வங்காளம்","हिन्दी": "पश्चिम बंगाल",   "తెలుగు": "పశ్చిమ బెంగాల్", "മലയാളം": "പശ്ചിമ ബംഗാൾ"},
    "Odisha":         {"தமிழ்": "ஒடிசா",          "हिन्दी": "ओडिशा",          "తెలుగు": "ఒడిశా",        "മലയാളം": "ഒഡീഷ"},
    "Assam":          {"தமிழ்": "அஸ்ஸாம்",        "हिन्दी": "असम",            "తెలుగు": "అస్సాం",        "മലയാളം": "അസം"},
    "Puducherry":     {"தமிழ்": "புதுச்சேரி",      "हिन्दी": "पुदुचेरी",        "తెలుగు": "పుదుచ్చేరి",    "മലയാളം": "പുതുച്ചേരി"}
}

SEASONS_TRANSLATION = {
    "Kharif":         {"தமிழ்": "காரிஃப் (மழைக்காலம்)", "हिन्दी": "खरीफ (वर्षा)",  "తెలుగు": "ఖరీఫ్ (వర్షాకాలం)", "മലയാളം": "ഖാരിഫ് (മഴക്കാലം)"},
    "Rabi":           {"தமிழ்": "ரபி (குளிர்காலம்)",   "हिन्दी": "रबी (सर्दियां)", "తెలుగు": "రబీ (శీతాకాలం)",   "മലയാളം": "റബി (ശീതകാലം)"},
    "Zaid / Summer":  {"தமிழ்": "சம்மர் / கோடை",      "हिन्दी": "जायद (गर्मी)",   "తెలుగు": "జాయెద్ / వేసవి",   "മലയാളം": "സെയ്ദ് / വേനൽ"},
    "Whole Year":     {"தமிழ்": "ஆண்டு முழுவதும்",     "हिन्दी": "वर्षभर",         "తెలుగు": "సంవత్సరం పొడవునా",  "മലയാളം": "വർഷം മുഴുവൻ"}
}

SOILS_TRANSLATION = {
    "Red Soil":       {"தமிழ்": "செம்மண் (Red Soil)",      "हिन्दी": "लाल मिट्टी",    "తెలుగు": "ఎర్ర నేల",     "മലയാളം": "ചുവന്ന മണ്ണ്"},
    "Black Soil":     {"தமிழ்": "கரிசல் மண் (Black Soil)",  "हिन्दी": "काली मिट्टी",   "తెలుగు": "నల్ల రేగడి",    "മലയാളം": "കറുത്ത മണ്ണ്"},
    "Alluvial":       {"தமிழ்": "வண்டல் மண் (Alluvial)",   "हिन्दी": "जलोढ़ मिट्टी",  "తెలుగు": "ఒండ్రు నేల",   "മലയാളം": "എക്കൽ മണ്ണ്"},
    "Loamy Soil":     {"தமிழ்": "வண்டல் செம்மண் (Loamy)",  "हिन्दी": "दोमट मिट्टी",   "తెలుగు": "దుబ్బ నేల",    "മലയാളം": "എക്കൽ കലർന്ന മണ്ണ്"},
    "Sandy Soil":     {"தமிழ்": "மணல் மண் (Sandy Soil)",   "हिन्दी": "बलुई मिट्टी",   "తెలుగు": "ఇసుక నేల",     "മലയാളം": "മണൽ മണ്ണ്"},
    "Clay Soil":      {"தமிழ்": "களிமண் (Clay Soil)",     "हिन्दी": "चिकनी मिट्टी",  "తెలుగు": "బంకమట్టి",     "മലയാളം": "കളിമണ്ണ്"},
    "Laterite Soil":  {"தமிழ்": "செம்பாறை மண் (Laterite)", "हिन्दी": "लेटराइट मिट्टी", "తెలుగు": "లేటరైట్ నేల",  "മലയാളം": "ലാറ്ററൈറ്റ് മണ്ണ്"},
    "Other":          {"தமிழ்": "இதர மண் வகை",           "हिन्दी": "अन्य मिट्टी",   "తెలుగు": "ఇతర నేలలు",    "മലയാളം": "മറ്റ് മണ്ണ്"}
}

DISTRICTS_TRANSLATION = {
    "Ariyalur":       {"தமிழ்": "அரியலூர்",        "हिन्दी": "अरियालूर",       "తెలుగు": "అరియాలూర్",     "മലയാളം": "അരിയല്ലൂർ"},
    "Coimbatore":     {"தமிழ்": "கோயம்புத்தூர்",   "हिन्दी": "कोयंबटूर",        "తెలుగు": "కోయంబత్తూరు",   "മലയാളം": "കോയമ്പത്തൂർ"},
    "Cuddalore":      {"தமிழ்": "கடலூர்",           "हिन्दी": "कुड्डालोर",       "తెలుగు": "కడలూరు",        "മലയാളം": "കടലൂർ"},
    "Dharmapuri":     {"தமிழ்": "தர்மபுரி",         "हिन्दी": "धर्मपुरी",        "తెలుగు": "ధర్మపురి",       "മലയാളം": "ധർമ്മപുരി"},
    "Dindigul":       {"தமிழ்": "திண்டுக்கல்",      "हिन्दी": "डिंडीगुल",         "తెలుగు": "దిండిగల్",      "മലയാളം": "ദിണ്ഡിഗൽ"},
    "Erode":          {"தமிழ்": "ஈரோடு",            "हिन्दी": "इरोड",             "తెలుగు": "ఈరోడ్",         "മലയാളം": "ഈറോഡ്"},
    "Kanchipuram":    {"தமிழ்": "காஞ்சிபுரம்",     "हिन्दी": "कांचीपुरम",        "తెలుగు": "కాంచీపురం",     "മലയാളം": "കാഞ്ചീപുരം"},
    "Kanyakumari":    {"தமிழ்": "கன்னியாகுமரி",   "हिन्दी": "कन्याकुमारी",      "తెలుగు": "కన్యాకుమారి",   "മലയാളം": "കന്യാകുമാരി"},
    "Karur":          {"தமிழ்": "கரூர்",            "हिन्दी": "करूर",             "తెలుగు": "కరూర్",         "മലയാളം": "കരൂർ"},
    "Krishnagiri":    {"தமிழ்": "கிருஷ்ணகிரி",     "हिन्दी": "कृष्णगिरि",        "తెలుగు": "కృష్ణగిరి",     "മലയാളം": "കൃഷ്ണഗിരി"},
    "Madurai":        {"தமிழ்": "மதுரை",            "हिन्दी": "मदुरै",            "తెలుగు": "మధురై",         "മലയാളം": "മധുര"},
    "Nagapattinam":   {"தமிழ்": "நாகப்பட்டினம்",  "हिन्दी": "नागापट्टिनम",      "తెలుగు": "నాగపట్నం",      "മലയാളം": "നാഗപട്ടണം"},
    "Namakkal":       {"தமிழ்": "நாமக்கல்",        "हिन्दी": "नमक्कल",          "తెలుగు": "నమక్కల్",       "മലയാളം": "നാമക്കൽ"},
    "Perambalur":     {"தமிழ்": "பெரம்பலூர்",     "हिन्दी": "पेरम्बलूर",        "తెలుగు": "పెరంబలూరు",     "മലയാളം": "പെരമ്പലൂർ"},
    "Pudukkottai":    {"தமிழ்": "புதுக்கோட்டை",   "हिन्दी": "पुदुक्कोट्टई",     "తెలుగు": "పుదుక్కోట్టై",  "മലയാളം": "പുതുക്കോട്ട"},
    "Ramanathapuram": {"தமிழ்": "இராமநாதபுரம்",   "हिन्दी": "रामानाथापुरम",     "తెలుగు": "రామనాథపురం",    "മലയാളം": "രാമനാഥപുരം"},
    "Salem":          {"தமிழ்": "சேலம்",           "हिन्दी": "सलेम",             "తెలుగు": "సేలం",          "മലയാളം": "സേലം"},
    "Sivaganga":      {"தமிழ்": "சிவகங்கை",       "हिन्दी": "शिवगंगा",          "తెలుగు": "శివగంగ",        "മലയാളം": "ശിവഗംഗ"},
    "Thanjavur":      {"தமிழ்": "தஞ்சாவூர்",      "हिन्दी": "तंजावुर",          "తెలుగు": "తంజావూరు",      "മലയാളം": "തഞ്ചാവൂർ"},
    "Theni":          {"தமிழ்": "தேனி",            "हिन्दी": "थेनी",             "తెలుగు": "తేని",          "മലയാളം": "തേനി"},
    "Thiruvallur":    {"தமிழ்": "திருவள்ளூர்",    "हिन्दी": "तिरुवल्लूर",       "తెలుగు": "తిరువళ్లూరు",   "മലയാളം": "തിരുവള്ളൂർ"},
    "Thiruvarur":     {"தமிழ்": "திருவாரூர்",     "हिन्दी": "तिरुवारूर",        "తెలుగు": "తిరువారూరు",    "മലയാളം": "തിരുവാരുർ"},
    "Thoothukudi":    {"தமிழ்": "தூத்துக்குடி",   "हिन्दी": "थूथुकुडी",         "తెలుగు": "తూత్తుకుడి",    "മലയാളം": "തൂത്തുക്കുടി"},
    "Tiruchirappalli":{"தமிழ்": "திருச்சிராப்பள்ளி","हिन्दी": "तिरुचिरापल्ली", "తెలుగు": "తిరుచిరాపల్లి", "മലയാളം": "തിരുച്ചിറപ്പള്ളി"},
    "Tirunelveli":    {"தமிழ்": "திருநெல்வேலி",  "हिन्दी": "तिरुनेलवेली",      "తెలుగు": "తిరునెల్వేలి",  "മലയാളം": "തിരുനെൽവേലി"},
    "Tiruppur":       {"தமிழ்": "திருப்பூர்",     "हिन्दी": "तिरुपूर",          "తెలుగు": "తిరుప్పూర్",    "മലയാളം": "തിരുപ്പൂർ"},
    "Tiruvannamalai": {"தமிழ்": "திருவண்ணாமலை", "हिन्दी": "तिरुवन्नामलाई",    "తెలుగు": "తిరువణ్ణామలై",  "മലയാളം": "തിരുവണ്ണാമലൈ"},
    "Vellore":        {"தமிழ்": "வேலூர்",          "हिन्दी": "वेल्लोर",          "తెలుగు": "వెల్లూరు",      "മലയാളം": "വെല്ലൂർ"},
    "Villupuram":     {"தமிழ்": "விழுப்புரம்",     "हिन्दी": "विल्लुपुरम",       "తెలుగు": "విల్లుపురం",    "മലയാളം": "വില്ലുപുരം"},
    "Virudhunagar":   {"தமிழ்": "விருதுநகர்",      "हिन्दी": "विरुधुनगर",        "తెలుగు": "విరుదునగర్",    "മലയാളം": "വിരുധുനഗർ"},
    "Karaikal":       {"தமிழ்": "காரைக்கால்",     "हिन्दी": "कराईकल",          "తెలుగు": "కారైకాల్",      "മലയാളം": "കാരയ്ക്കൽ"},
    "Puducherry":     {"தமிழ்": "புதுச்சேரி",      "हिन्दी": "पुदुचेरी",         "తెలుగు": "పుదుచ్చేరి",    "മലയാളം": "പുതുച്ചേരി"}
}

def t_crop(c: str) -> str:
    lang = st.session_state.get("selected_language_code", "English")
    return CROPS_TRANSLATION.get(c, {}).get(lang, c)

def t_state(s: str) -> str:
    lang = st.session_state.get("selected_language_code", "English")
    return STATES_TRANSLATION.get(s, {}).get(lang, s)

def t_season(ss: str) -> str:
    lang = st.session_state.get("selected_language_code", "English")
    return SEASONS_TRANSLATION.get(ss, {}).get(lang, ss)

def t_soil(sl: str) -> str:
    lang = st.session_state.get("selected_language_code", "English")
    return SOILS_TRANSLATION.get(sl, {}).get(lang, sl)

def t_district(d: str) -> str:
    lang = st.session_state.get("selected_language_code", "English")
    return DISTRICTS_TRANSLATION.get(d, {}).get(lang, d)

def format_indian_spoken_amount(amount: float, lang: str) -> str:
    amt = int(round(amount))
    if amt <= 0: return "0"
    crores = amt // 10000000
    rem = amt % 10000000
    lakhs = rem // 100000
    rem = rem % 100000
    thousands = rem // 1000
    hundreds = rem % 1000
    parts = []
    if lang == "தமிழ்":
        if crores > 0: parts.append(f"{crores} கோடி")
        if lakhs > 0: parts.append(f"{lakhs} லட்சத்து" if (thousands or hundreds) else f"{lakhs} லட்சம்")
        if thousands > 0: parts.append(f"{thousands} ஆயிரத்து" if hundreds else f"{thousands} ஆயிரம்")
        if hundreds > 0: parts.append(f"{hundreds}")
        return " ".join(parts) if parts else str(amt)
    elif lang == "हिन्दी":
        if crores > 0: parts.append(f"{crores} करोड़")
        if lakhs > 0: parts.append(f"{lakhs} लाख")
        if thousands > 0: parts.append(f"{thousands} हज़ार")
        if hundreds > 0: parts.append(f"{hundreds}")
        return " ".join(parts) if parts else str(amt)
    elif lang == "తెలుగు":
        if crores > 0: parts.append(f"{crores} కోట్ల")
        if lakhs > 0: parts.append(f"{lakhs} లక్షల")
        if thousands > 0: parts.append(f"{thousands} వేల")
        if hundreds > 0: parts.append(f"{hundreds}")
        return " ".join(parts) if parts else str(amt)
    elif lang == "മലയാളം":
        if crores > 0: parts.append(f"{crores} കോടി")
        if lakhs > 0: parts.append(f"{lakhs} ലക്ഷം")
        if thousands > 0: parts.append(f"{thousands} ആയിരം")
        if hundreds > 0: parts.append(f"{hundreds}")
        return " ".join(parts) if parts else str(amt)
    else:
        if crores > 0: parts.append(f"{crores} crore")
        if lakhs > 0: parts.append(f"{lakhs} lakh")
        if thousands > 0: parts.append(f"{thousands} thousand")
        if hundreds > 0: parts.append(f"{hundreds}")
        return " ".join(parts) if parts else str(amt)

# ============================================================
# AGRONOMIC DATA & CROP CHARACTERISTICS
# ============================================================

CROP_DATA = {
    "Paddy": {"base_yield": 36.0, "base_cost": 42000.0, "base_price": 2250.0, "water_req": 180000.0, "seasons": ["Kharif", "Whole Year"], "soils": ["Clay Soil", "Alluvial", "Loamy Soil"], "disease_risk": 30.0, "weather_risk": 20.0},
    "Wheat": {"base_yield": 34.0, "base_cost": 36000.0, "base_price": 2400.0, "water_req": 90000.0, "seasons": ["Rabi", "Winter"], "soils": ["Alluvial", "Loamy Soil", "Black Soil"], "disease_risk": 20.0, "weather_risk": 18.0},
    "Maize": {"base_yield": 38.0, "base_cost": 28000.0, "base_price": 2200.0, "water_req": 70000.0, "seasons": ["Kharif", "Rabi", "Zaid / Summer", "Whole Year"], "soils": ["Red Soil", "Alluvial", "Loamy Soil", "Black Soil"], "disease_risk": 20.0, "weather_risk": 18.0},
    "Cotton": {"base_yield": 18.0, "base_cost": 44000.0, "base_price": 7100.0, "water_req": 95000.0, "seasons": ["Kharif", "Whole Year"], "soils": ["Black Soil", "Red Soil", "Alluvial"], "disease_risk": 32.0, "weather_risk": 22.0},
    "Sugarcane": {"base_yield": 400.0, "base_cost": 85000.0, "base_price": 360.0, "water_req": 260000.0, "seasons": ["Kharif", "Whole Year"], "soils": ["Alluvial", "Black Soil", "Clay Soil"], "disease_risk": 28.0, "weather_risk": 15.0},
    "Groundnut": {"base_yield": 24.0, "base_cost": 32000.0, "base_price": 6200.0, "water_req": 55000.0, "seasons": ["Kharif", "Zaid / Summer", "Rabi"], "soils": ["Red Soil", "Sandy Soil", "Loamy Soil", "Laterite Soil"], "disease_risk": 22.0, "weather_risk": 18.0},
    "Soyabean": {"base_yield": 20.0, "base_cost": 26000.0, "base_price": 4600.0, "water_req": 65000.0, "seasons": ["Kharif"], "soils": ["Black Soil", "Loamy Soil"], "disease_risk": 24.0, "weather_risk": 20.0},
    "Bajra": {"base_yield": 19.0, "base_cost": 16000.0, "base_price": 2450.0, "water_req": 38000.0, "seasons": ["Kharif", "Zaid / Summer"], "soils": ["Sandy Soil", "Red Soil", "Loamy Soil"], "disease_risk": 15.0, "weather_risk": 14.0},
    "Jowar": {"base_yield": 17.0, "base_cost": 18000.0, "base_price": 2900.0, "water_req": 42000.0, "seasons": ["Kharif", "Rabi"], "soils": ["Black Soil", "Red Soil", "Loamy Soil"], "disease_risk": 18.0, "weather_risk": 16.0},
    "Mustard": {"base_yield": 17.5, "base_cost": 22000.0, "base_price": 5400.0, "water_req": 40000.0, "seasons": ["Rabi", "Winter"], "soils": ["Alluvial", "Sandy Soil", "Loamy Soil"], "disease_risk": 22.0, "weather_risk": 18.0},
    "Gram": {"base_yield": 15.0, "base_cost": 22000.0, "base_price": 5300.0, "water_req": 36000.0, "seasons": ["Rabi", "Winter"], "soils": ["Loamy Soil", "Black Soil", "Red Soil"], "disease_risk": 22.0, "weather_risk": 18.0},
    "Moong": {"base_yield": 11.0, "base_cost": 18000.0, "base_price": 7500.0, "water_req": 32000.0, "seasons": ["Zaid / Summer", "Kharif"], "soils": ["Loamy Soil", "Red Soil", "Alluvial"], "disease_risk": 18.0, "weather_risk": 14.0},
    "Urad": {"base_yield": 10.5, "base_cost": 18000.0, "base_price": 7300.0, "water_req": 32000.0, "seasons": ["Zaid / Summer", "Kharif", "Rabi"], "soils": ["Black Soil", "Red Soil", "Loamy Soil"], "disease_risk": 18.0, "weather_risk": 14.0},
    "Sesamum": {"base_yield": 7.0, "base_cost": 16000.0, "base_price": 8900.0, "water_req": 28000.0, "seasons": ["Zaid / Summer", "Kharif"], "soils": ["Red Soil", "Sandy Soil", "Loamy Soil"], "disease_risk": 14.0, "weather_risk": 14.0},
    "Tomato": {"base_yield": 130.0, "base_cost": 46000.0, "base_price": 1750.0, "water_req": 75000.0, "seasons": ["Whole Year", "Zaid / Summer", "Rabi", "Kharif"], "soils": ["Red Soil", "Loamy Soil", "Alluvial"], "disease_risk": 32.0, "weather_risk": 22.0},
    "Onion": {"base_yield": 95.0, "base_cost": 41000.0, "base_price": 1900.0, "water_req": 70000.0, "seasons": ["Rabi", "Kharif", "Zaid / Summer", "Whole Year"], "soils": ["Red Soil", "Loamy Soil", "Alluvial", "Black Soil"], "disease_risk": 28.0, "weather_risk": 18.0},
    "Potato": {"base_yield": 120.0, "base_cost": 49000.0, "base_price": 1500.0, "water_req": 80000.0, "seasons": ["Rabi", "Winter"], "soils": ["Alluvial", "Sandy Soil", "Loamy Soil"], "disease_risk": 28.0, "weather_risk": 18.0}
}

STATE_CROPS_PREFERENCE = {
    "Tamil Nadu": ["Paddy", "Groundnut", "Cotton", "Sugarcane", "Maize", "Tomato", "Onion", "Sesamum", "Urad", "Moong"],
    "Puducherry": ["Paddy", "Sugarcane", "Groundnut", "Cotton", "Tomato", "Sesamum", "Urad", "Maize"],
    "Andhra Pradesh": ["Paddy", "Cotton", "Groundnut", "Maize", "Sugarcane", "Tomato", "Urad", "Onion"],
    "Telangana": ["Cotton", "Paddy", "Maize", "Soyabean", "Groundnut", "Tomato", "Gram"],
    "Karnataka": ["Maize", "Cotton", "Sugarcane", "Groundnut", "Paddy", "Tomato", "Jowar", "Gram", "Onion"],
    "Kerala": ["Paddy", "Sesamum", "Groundnut", "Tomato", "Urad", "Moong"],
    "Maharashtra": ["Sugarcane", "Cotton", "Soyabean", "Onion", "Jowar", "Gram", "Groundnut", "Wheat"],
    "Gujarat": ["Cotton", "Groundnut", "Wheat", "Bajra", "Sesamum", "Mustard", "Onion"],
    "Rajasthan": ["Mustard", "Bajra", "Gram", "Wheat", "Soyabean", "Sesamum", "Moong"],
    "Punjab": ["Wheat", "Paddy", "Cotton", "Maize", "Sugarcane", "Potato"],
    "Haryana": ["Wheat", "Paddy", "Mustard", "Cotton", "Sugarcane", "Bajra"],
    "Uttar Pradesh": ["Sugarcane", "Wheat", "Paddy", "Potato", "Mustard", "Maize", "Gram"],
    "Madhya Pradesh": ["Soyabean", "Wheat", "Gram", "Mustard", "Cotton", "Maize", "Jowar"],
    "Bihar": ["Paddy", "Wheat", "Maize", "Potato", "Sugarcane", "Gram"],
    "West Bengal": ["Paddy", "Potato", "Sesamum", "Mustard", "Maize"],
    "Odisha": ["Paddy", "Groundnut", "Moong", "Urad", "Sesamum", "Cotton"],
    "Assam": ["Paddy", "Mustard", "Potato", "Sugarcane"]
}

SOIL_AFFINITY = {
    "Red Soil": {"Groundnut": 1.25, "Cotton": 1.15, "Maize": 1.2, "Sesamum": 1.2, "Tomato": 1.2, "Onion": 1.1, "Urad": 1.25, "Moong": 1.2, "Bajra": 1.15, "Jowar": 1.1},
    "Black Soil": {"Cotton": 1.35, "Sugarcane": 1.2, "Soyabean": 1.3, "Wheat": 1.2, "Paddy": 1.1, "Gram": 1.25, "Jowar": 1.25, "Urad": 1.2},
    "Alluvial": {"Wheat": 1.35, "Paddy": 1.3, "Sugarcane": 1.3, "Potato": 1.35, "Mustard": 1.3, "Maize": 1.25, "Tomato": 1.2},
    "Loamy Soil": {"Tomato": 1.3, "Potato": 1.3, "Onion": 1.3, "Wheat": 1.25, "Maize": 1.25, "Paddy": 1.2, "Groundnut": 1.2, "Gram": 1.2},
    "Sandy Soil": {"Bajra": 1.35, "Mustard": 1.25, "Groundnut": 1.2, "Sesamum": 1.2, "Potato": 1.15},
    "Clay Soil": {"Paddy": 1.4, "Sugarcane": 1.3, "Wheat": 1.15},
    "Laterite Soil": {"Groundnut": 1.15, "Sesamum": 1.15, "Paddy": 1.1},
    "Other": {"Maize": 1.1, "Bajra": 1.1}
}

STATE_DISTRICT_MAP: Dict[str, List[str]] = {
    "Tamil Nadu": ["Ariyalur", "Coimbatore", "Cuddalore", "Dharmapuri", "Dindigul", "Erode", "Kanchipuram", "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Nagapattinam", "Namakkal", "Perambalur", "Pudukkottai", "Ramanathapuram", "Salem", "Sivaganga", "Thanjavur", "Theni", "Thiruvallur", "Thiruvarur", "Thoothukudi", "Tiruchirappalli", "Tirunelveli", "Tiruppur", "Tiruvannamalai", "Vellore", "Villupuram", "Virudhunagar"],
    "Punjab": ["Amritsar", "Barnala", "Bathinda", "Faridkot", "Fatehgarh Sahib", "Fazilka", "Firozpur", "Gurdaspur", "Hoshiarpur", "Jalandhar", "Kapurthala", "Ludhiana", "Mansa", "Moga", "Muktsar", "Pathankot", "Patiala", "Rupnagar", "Sangrur", "Tarn Taran"],
    "Maharashtra": ["Ahmednagar", "Akola", "Amravati", "Aurangabad", "Beed", "Bhandara", "Buldhana", "Chandrapur", "Dhule", "Jalgaon", "Jalna", "Kolhapur", "Latur", "Nagpur", "Nanded", "Nashik", "Osmanabad", "Parbhani", "Pune", "Sangli", "Satara", "Solapur", "Yavatmal"],
    "Gujarat": ["Ahmedabad", "Amreli", "Anand", "Banaskantha", "Bharuch", "Bhavnagar", "Gandhinagar", "Jamnagar", "Junagadh", "Kutch", "Mehsana", "Panchmahal", "Rajkot", "Surat", "Vadodara", "Valsad"],
    "Rajasthan": ["Ajmer", "Alwar", "Banswara", "Baran", "Barmer", "Bharatpur", "Bhilwara", "Bikaner", "Bundi", "Chittorgarh", "Churu", "Dausa", "Dholpur", "Dungarpur", "Hanumangarh", "Jaipur", "Jaisalmer", "Jalore", "Jhalawar", "Jhunjhunu", "Jodhpur", "Karauli", "Kota", "Nagaur", "Pali", "Pratapgarh", "Rajsamand", "Sawai Madhopur", "Sikar", "Sirohi", "Sri Ganganagar", "Tonk", "Udaipur"],
    "Uttar Pradesh": ["Agra", "Aligarh", "Allahabad", "Ambedkar Nagar", "Amroha", "Auraiya", "Azamgarh", "Badaun", "Baghpat", "Bahraich", "Ballia", "Balrampur", "Banda", "Barabanki", "Bareilly", "Basti", "Bijnor", "Bulandshahr", "Chandauli", "Chitrakoot", "Deoria", "Etah", "Etawah", "Faizabad", "Farrukhabad", "Fatehpur", "Firozabad", "Gautam Buddha Nagar", "Ghaziabad", "Ghazipur", "Gonda", "Gorakhpur", "Hamirpur", "Hapur", "Hardoi", "Hathras", "Jalaun", "Jaunpur", "Jhansi", "Kannauj", "Kanpur", "Kasganj", "Kaushambi", "Kheri", "Kushinagar", "Lalitpur", "Lucknow", "Maharajganj", "Mahoba", "Mainpuri", "Mathura", "Mau", "Meerut", "Mirzapur", "Moradabad", "Muzaffarnagar", "Pilibhit", "Pratapgarh", "Rae Bareli", "Rampur", "Saharanpur", "Sambhal", "Sant Kabir Nagar", "Shahjahanpur", "Shamli", "Shravasti", "Siddharthnagar", "Sitapur", "Sonbhadra", "Sultanpur", "Unnao", "Varanasi"],
    "Andhra Pradesh": ["Anantapur", "Chittoor", "East Godavari", "Guntur", "Kadapa", "Krishna", "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Visakhapatnam", "Vizianagaram", "West Godavari"],
    "Karnataka": ["Bagalkot", "Bangalore", "Belgaum", "Bellary", "Bidar", "Bijapur", "Chikmagalur", "Chitradurga", "Dakshina Kannada", "Davanagere", "Dharwad", "Gulbarga", "Hassan", "Kolar", "Mandya", "Mysore", "Raichur", "Shimoga", "Tumkur", "Udupi"],
    "Kerala": ["Alappuzha", "Ernakulam", "Idukki", "Kannur", "Kollam", "Kottayam", "Kozhikode", "Malappuram", "Palakkad", "Thrissur", "Wayanad"],
    "Telangana": ["Adilabad", "Bhadradri Kothagudem", "Hyderabad", "Jagtial", "Karimnagar", "Khammam", "Mahbubnagar", "Mancherial", "Medak", "Medchal", "Nalgonda", "Nizamabad", "Rangareddy", "Siddipet", "Suryapet", "Warangal"],
    "Haryana": ["Ambala", "Bhiwani", "Faridabad", "Fatehabad", "Gurgaon", "Hisar", "Jhajjar", "Jind", "Kaithal", "Karnal", "Kurukshetra", "Panipat", "Rohtak", "Sirsa", "Sonipat", "Yamunanagar"],
    "Madhya Pradesh": ["Balaghat", "Betul", "Bhopal", "Chhindwara", "Dewas", "Dhar", "Gwalior", "Guna", "Hoshangabad", "Indore", "Jabalpur", "Khandwa", "Khargone", "Mandsaur", "Morena", "Ratlam", "Rewa", "Sagar", "Satna", "Sehore", "Ujjain", "Vidisha"],
    "West Bengal": ["Bankura", "Bardhaman", "Birbhum", "Cooch Behar", "Dakshin Dinajpur", "Darjeeling", "Hooghly", "Howrah", "Jalpaiguri", "Jhargram", "Kalimpong", "Kolkata", "Malda", "Murshidabad", "Nadia", "North 24 Parganas", "Paschim Bardhaman", "Paschim Medinipur", "Purba Bardhaman", "Purba Medinipur", "Purulia", "South 24 Parganas", "Uttar Dinajpur"],
    "Bihar": ["Araria", "Bhagalpur", "Bhojpur", "Darbhanga", "Gaya", "Muzaffarpur", "Patna", "Purnia", "Rohtas", "Samastipur", "Saran", "Vaishali"],
    "Odisha": ["Angul", "Balasore", "Bargarh", "Bhadrak", "Bolangir", "Cuttack", "Deogarh", "Dhenkanal", "Gajapati", "Ganjam", "Jagatsinghpur", "Jajpur", "Jharsuguda", "Kalahandi", "Kandhamal", "Kendrapara", "Kendujhar", "Khordha", "Koraput", "Malkangiri", "Mayurbhanj", "Nabarangpur", "Nayagarh", "Nuapada", "Puri", "Rayagada", "Sambalpur", "Subarnapur", "Sundargarh"],
    "Assam": ["Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar", "Charaideo", "Chirang", "Darrang", "Dhemaji", "Dhubri", "Dibrugarh", "Dima Hasao", "Goalpara", "Golaghat", "Hailakandi", "Hojai", "Jorhat", "Kamrup", "Kamrup Metropolitan", "Karbi Anglong", "Karimganj", "Kokrajhar", "Lakhimpur", "Majuli", "Morigaon", "Nagaon", "Nalbari", "Sivasagar", "Sonitpur", "South Salmara-Mankachar", "Tinsukia", "Udalguri", "West Karbi Anglong"],
    "Puducherry": ["Karaikal", "Mahe", "Puducherry", "Yanam"]
}

# ============================================================
# EVALUATION ALGORITHM
# ============================================================

def evaluate_crop_suitability(crop: str, state: str, district: str, season: str, soil: str, land: float, budget: float, water: float) -> Dict[str, Any]:
    c_info = CROP_DATA.get(crop, {
        "base_yield": 20.0, "base_cost": 25000.0, "base_price": 3000.0,
        "water_req": 60000.0, "seasons": ["Kharif", "Whole Year"], "soils": ["Loamy Soil"],
        "disease_risk": 20.0, "weather_risk": 15.0
    })

    score = 50.0

    # State Affinity
    preferred_crops = STATE_CROPS_PREFERENCE.get(state, [])
    if crop in preferred_crops:
        idx = preferred_crops.index(crop)
        score += max(5.0, 22.0 - (idx * 2.0))
    else:
        score += 5.0

    # Season Match
    if season in c_info["seasons"] or "Whole Year" in c_info["seasons"]:
        score += 15.0
    else:
        score -= 10.0

    # Soil Affinity
    soil_mult = SOIL_AFFINITY.get(soil, {}).get(crop, 1.0)
    if soil in c_info["soils"]:
        score += 15.0 * soil_mult
    else:
        score += 5.0 * soil_mult

    # Water Security
    req_water = c_info["water_req"] * land
    if water >= req_water:
        score += 10.0
    else:
        water_ratio = water / max(1.0, req_water)
        score += 10.0 * water_ratio

    # Budget Viability
    req_cost = c_info["base_cost"] * land
    if budget >= req_cost:
        score += 10.0
    else:
        cost_ratio = budget / max(1.0, req_cost)
        score += 10.0 * cost_ratio

    eff_yield_per_acre = c_info["base_yield"] * soil_mult
    total_yield = eff_yield_per_acre * land
    total_revenue = total_yield * c_info["base_price"]
    net_profit = total_revenue - req_cost

    final_score = max(10.0, min(99.4, round(score, 1)))

    return {
        "crop": crop,
        "decision_score": final_score,
        "data_coverage": "Verified",
        "yield_quintals": round(total_yield, 1),
        "expected_revenue": round(total_revenue, 0),
        "cultivation_cost": round(req_cost, 0),
        "net_profit": round(net_profit, 0),
        "required_water_litres": round(req_water, 0),
        "historical_market_price": round(c_info["base_price"], 0),
        "disease_risk": c_info["disease_risk"],
        "weather_risk": c_info["weather_risk"]
    }

def run_local_prediction(state: str, district: str, season: str, soil: str, land: float, budget: float, water: float) -> Dict[str, Any]:
    candidates = []
    for crop_name in CROP_DATA.keys():
        eval_res = evaluate_crop_suitability(crop_name, state, district, season, soil, land, budget, water)
        candidates.append(eval_res)

    candidates = sorted(candidates, key=lambda x: x["decision_score"], reverse=True)
    top5 = candidates[:5]
    for idx, c in enumerate(top5):
        c["rank"] = idx + 1

    best = top5[0]
    return {
        "success": True,
        "state": state,
        "district": district,
        "season": season,
        "soil_type": soil,
        "land_acres": land,
        "budget": budget,
        "water_litres": water,
        "best_crop": best["crop"],
        "best_score": best["decision_score"],
        "best_rank": best["rank"],
        "recommendations": top5
    }

# ============================================================
# DATASET LOADING FOR EDA PORTAL
# ============================================================

@st.cache_data
def load_eda_datasets():
    datasets = {}
    f_master = DATASET_DIR / "final_crop_decision_dataset.csv"
    if not f_master.exists():
        f_master = DATASET_DIR / "Final_Crop_Dashboard_Data.csv"
    if f_master.exists():
        datasets["🌾 Master Agricultural Survey (1,000 Records, 24 Agronomic Features)"] = pd.read_csv(f_master)

    f_prod = DATASET_DIR / "crop_production_data.csv"
    if f_prod.exists():
        datasets["📈 Crop Production & Yield Records (1,000 Entries)"] = pd.read_csv(f_prod)

    f_price = DATASET_DIR / "crop_price_data.csv"
    if f_price.exists():
        datasets["💰 APMC Mandi Market Prices (4,819 Mandi Records)"] = pd.read_csv(f_price)

    return datasets

# ============================================================
# RESPONSIVE VOICE ASSISTANT CARD (Mobile Friendly, No Cutoff)
# ============================================================

def render_unified_voice_card(speech_text: str, lang: str):
    """
    Renders a responsive, mobile-optimized Voice Assistant card.
    Uses height=125 so both the title and buttons fit comfortably on small mobile screens.
    """
    if lang == "தமிழ்":
        card_title = "🎙️ பயிர் ஆலோசனை குரல் வழிகாட்டி"
        card_sub = "மாநிலம், மாவட்டம், மண், நீர், பயிர் மற்றும் லாப விவரங்களை கேளுங்கள்"
        btn_play = "🔊 ஆலோசனை கேள்"
        btn_stop = "⏹️ நிறுத்து"
        lang_code = "ta-IN"
    elif lang == "हिन्दी":
        card_title = "🎙️ फसल सलाह आवाज़ गाइड"
        card_sub = "राज्य, ज़िला, मिट्टी, जल, फसल एवं लाभ विवरण हिंदी में सुनें"
        btn_play = "🔊 बोलकर सुनें"
        btn_stop = "⏹️ रोकें"
        lang_code = "hi-IN"
    elif lang == "తెలుగు":
        card_title = "🎙️ పంట సలహా వాయిస్ గైడ్"
        card_sub = "రాష్ట్రం, జిల్లా, నేల, నీరు, సిఫారసు పంట వివరాలు వినండి"
        btn_play = "🔊 వినండి"
        btn_stop = "⏹️ ఆపండి"
        lang_code = "te-IN"
    elif lang == "മലയാളം":
        card_title = "🎙️ വിള ഉപദേശ വോയ്‌സ് ഗൈഡ്"
        card_sub = "സംസ്ഥാനം, ജില്ല, മണ്ണ്, ജലം, വിള ശുപാർശ എന്നിവ കേൾക്കുക"
        btn_play = "🔊 കേൾക്കുക"
        btn_stop = "⏹️ നിർത്തുക"
        lang_code = "ml-IN"
    else:
        card_title = "🎙️ Listen to Crop Advisory (Voice Reader)"
        card_sub = "Hear your state, district, soil, water, recommended crop, yield, and profit aloud"
        btn_play = "🔊 Read Advisory Aloud"
        btn_stop = "⏹️ Stop Voice"
        lang_code = "en-IN"

    safe_text = (speech_text
        .replace("\\", " ").replace('"', ' ').replace("'", " ")
        .replace("\n", " ").replace("\r", " ").replace("*", "")
        .replace("#", "").replace("{", "").replace("}", ""))

    html = f"""
    <div style="background:#ffffff; border:2px solid #10b981; border-radius:14px;
                padding:12px 16px; margin:0;
                box-shadow:0 3px 12px rgba(16,185,129,0.12);
                display:flex; flex-direction:column; gap:8px;">
        <div style="display:flex; align-items:center; gap:10px;">
            <div style="background:#ecfdf5; border:1.5px solid #a7f3d0; border-radius:50%;
                        width:36px; height:36px; display:flex; align-items:center;
                        justify-content:center; font-size:1.2rem; flex-shrink:0;">
                🎙️
            </div>
            <div>
                <div style="font-weight:800; color:#065f46; font-size:0.92rem; line-height:1.2;">
                    {card_title}
                </div>
                <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">
                    {card_sub}
                </div>
            </div>
        </div>
        <div style="display:flex; gap:10px; align-items:center; margin-top:2px;">
            <button id="agy_play_btn" onclick="playVoice()" style="
                background:linear-gradient(135deg,#059669 0%,#10b981 100%);
                color:#ffffff; border:none; padding:8px 18px; border-radius:10px;
                font-weight:700; font-size:0.86rem; cursor:pointer;
                box-shadow:0 3px 10px rgba(16,185,129,0.3);
                display:flex; align-items:center; gap:6px; white-space:nowrap;">
                {btn_play}
            </button>
            <button id="agy_stop_btn" onclick="stopVoice()" style="
                background:#ffffff; color:#dc2626;
                border:1.5px solid #fca5a5; padding:7px 14px; border-radius:10px;
                font-weight:700; font-size:0.86rem; cursor:pointer; white-space:nowrap;">
                {btn_stop}
            </button>
        </div>
    </div>

    <script>
    var speechText = "{safe_text}";
    var targetLang = "{lang_code}";
    var defaultPlayText = "{btn_play}";

    function playVoice() {{
        if (!window.speechSynthesis) {{
            alert("Speech synthesis is not supported on this browser.");
            return;
        }}
        window.speechSynthesis.cancel();

        var utter = new SpeechSynthesisUtterance(speechText);
        utter.lang = targetLang;
        utter.rate = 0.90;
        utter.pitch = 1.0;

        var btn = document.getElementById("agy_play_btn");
        if (btn) {{
            btn.style.opacity = "0.85";
            btn.innerText = "🔊 Playing Voice...";
        }}

        // Match voice by language prefix
        var voices = window.speechSynthesis.getVoices();
        var prefix = targetLang.substring(0, 2).toLowerCase();
        for (var i = 0; i < voices.length; i++) {{
            if (voices[i].lang.toLowerCase().indexOf(prefix) !== -1) {{
                utter.voice = voices[i];
                break;
            }}
        }}

        utter.onend = function() {{
            if (btn) {{
                btn.style.opacity = "1";
                btn.innerText = defaultPlayText;
            }}
        }};
        utter.onerror = function() {{
            if (btn) {{
                btn.style.opacity = "1";
                btn.innerText = defaultPlayText;
            }}
        }};

        window.speechSynthesis.speak(utter);
    }}

    function stopVoice() {{
        if (window.speechSynthesis) {{
            window.speechSynthesis.cancel();
        }}
        var btn = document.getElementById("agy_play_btn");
        if (btn) {{
            btn.style.opacity = "1";
            btn.innerText = defaultPlayText;
        }}
    }}
    </script>
    """
    components.html(html, height=125)

# ============================================================
# SIDEBAR CONTROLS
# ============================================================

st.sidebar.markdown(
    """
    <div style="text-align: center; padding: 12px 0 18px 0; border-bottom: 1px solid #e2e8f0; margin-bottom: 16px;">
        <h2 style="margin: 0; color: #059669 !important; font-size: 1.5rem;">🌾 Crop Decision System</h2>
        <span style="color: #64748b !important; font-size: 0.84rem; font-weight: 500;">Intelligent Agriculture Decision Platform</span>
    </div>
    """,
    unsafe_allow_html=True
)

# 5-Language Selector
lang_options = ["🇬🇧 English", "🇮🇳 தமிழ்", "🇮🇳 हिन्दी", "🇮🇳 తెలుగు", "🇮🇳 മലയാളം"]
lang_map = {
    "🇬🇧 English": "English",
    "🇮🇳 தமிழ்": "தமிழ்",
    "🇮🇳 हिन्दी": "हिन्दी",
    "🇮🇳 తెలుగు": "తెలుగు",
    "🇮🇳 മലയാളം": "മലയാളം"
}

cur_lang_code = st.session_state.get("selected_language_code", "English")
cur_lang_label = "🇬🇧 English"
for k, v in lang_map.items():
    if v == cur_lang_code:
        cur_lang_label = k

selected_lang_label = st.sidebar.selectbox(
    "🌐 Language / மொழி / भाषा / భాష / ഭാഷ",
    lang_options,
    index=lang_options.index(cur_lang_label),
    key="sb_lang_select"
)
current_lang = lang_map[selected_lang_label]
st.session_state["selected_language_code"] = current_lang

app_view_mode = st.sidebar.radio(
    f"📌 {t('location_header')}:",
    [f"🌾 {t('tab_advisory')}", f"📊 {t('tab_eda')}"],
    index=0
)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.subheader(f"📍 {t('location_header')}")

raw_states = sorted(list(STATE_DISTRICT_MAP.keys()))
state_display_map = {s: t_state(s) for s in raw_states}
inv_state_map = {v: k for k, v in state_display_map.items()}

if "active_state" not in st.session_state or st.session_state["active_state"] not in raw_states:
    st.session_state["active_state"] = raw_states[0]

curr_st_disp = state_display_map[st.session_state["active_state"]]
selected_state_disp = st.sidebar.selectbox(
    t("state_label"),
    list(state_display_map.values()),
    index=list(state_display_map.values()).index(curr_st_disp),
    key="sb_state_select"
)
selected_state = inv_state_map[selected_state_disp]

if selected_state != st.session_state["active_state"]:
    st.session_state["active_state"] = selected_state
    st.session_state["active_district"] = None
    st.session_state["active_season"] = None

available_districts = STATE_DISTRICT_MAP.get(selected_state, ["All Districts"])
dist_display_map = {d: t_district(d) for d in available_districts}
inv_dist_map = {v: k for k, v in dist_display_map.items()}

if st.session_state.get("active_district") not in available_districts:
    st.session_state["active_district"] = available_districts[0]

current_dist_disp = dist_display_map.get(st.session_state["active_district"], available_districts[0])
selected_dist_disp = st.sidebar.selectbox(
    t("district_label"),
    list(dist_display_map.values()),
    index=list(dist_display_map.values()).index(current_dist_disp) if current_dist_disp in dist_display_map.values() else 0,
    key="sb_district_select"
)
selected_district = inv_dist_map.get(selected_dist_disp, selected_dist_disp)
st.session_state["active_district"] = selected_district

raw_seasons = ["Kharif", "Rabi", "Zaid / Summer", "Whole Year"]
season_display_map = {s: t_season(s) for s in raw_seasons}
inv_season_map = {v: k for k, v in season_display_map.items()}

if st.session_state.get("active_season") not in raw_seasons:
    st.session_state["active_season"] = raw_seasons[0]

current_season_disp = season_display_map[st.session_state["active_season"]]
selected_season_disp = st.sidebar.selectbox(
    t("season_label"),
    list(season_display_map.values()),
    index=list(season_display_map.values()).index(current_season_disp),
    key="sb_season_select"
)
selected_season = inv_season_map[selected_season_disp]
st.session_state["active_season"] = selected_season

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown(
    f'<div class="badge-pill badge-green" style="width:100%; text-align:center; padding:8px;">{t("api_online")}</div>',
    unsafe_allow_html=True
)

# ============================================================
# EDA PORTAL VIEW
# ============================================================

if "EDA" in app_view_mode:
    st.markdown(
        f"""
        <div class="hero-banner">
            <h1>📈 {t("tab_eda")}</h1>
            <p>Statistical Summaries, Correlation Heatmaps, Feature Distributions & Data Intelligence</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    datasets = load_eda_datasets()
    eda_t1, eda_t2, eda_t3 = st.tabs(["📊 Statistical Summary", "📈 Univariate Distributions", "🔥 Bivariate Heatmap"])
    df_master = datasets.get("🌾 Master Agricultural Survey (1,000 Records, 24 Agronomic Features)")
    if df_master is None and len(datasets) > 0: df_master = list(datasets.values())[0]

    with eda_t1:
        if df_master is not None:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Records", f"{len(df_master):,}")
            m2.metric("Agronomic Features", f"{len(df_master.columns)}")
            m3.metric("Completeness", "100.0%")
            m4.metric("States Mapped", "17 States")
            st.dataframe(df_master.describe().T.style.format("{:.2f}"), use_container_width=True)

    with eda_t2:
        if df_master is not None:
            num_cols = df_master.select_dtypes(include=[np.number]).columns.tolist()
            sel_col = st.selectbox("Select Feature:", num_cols, index=0)
            fig_hist = px.histogram(df_master, x=sel_col, nbins=30, color_discrete_sequence=["#059669"])
            fig_hist.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_hist, use_container_width=True)

    with eda_t3:
        if df_master is not None:
            corr_df = df_master.select_dtypes(include=[np.number]).corr()
            fig_corr = px.imshow(corr_df, text_auto=".2f", aspect="auto", color_continuous_scale="Greens")
            fig_corr.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_corr, use_container_width=True)

# ============================================================
# MAIN FARM CROP ADVISORY VIEW
# ============================================================

else:
    st.markdown(
        f"""
        <div class="hero-banner">
            <h1>🌾 {t("app_title")}</h1>
            <p>{t("app_subtitle")}<br>
            <span style="font-size:0.9rem; opacity:0.9;">{t("app_tagline")}</span></p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader(t("farmer_header"))
    st.caption(t("farmer_desc"))

    raw_soils = ["Red Soil", "Black Soil", "Alluvial", "Loamy Soil", "Sandy Soil", "Clay Soil", "Laterite Soil", "Other"]
    soil_display_map = {s: t_soil(s) for s in raw_soils}
    inv_soil_map = {v: k for k, v in soil_display_map.items()}

    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        selected_soil_disp = st.selectbox(t("soil_label"), list(soil_display_map.values()), index=0)
        farmer_soil = inv_soil_map[selected_soil_disp]
    with fc2:
        farmer_land = st.number_input(t("land_label"), min_value=0.1, max_value=500.0, value=2.5, step=0.5)
    with fc3:
        farmer_budget = st.number_input(t("budget_label"), min_value=1000.0, max_value=50000000.0, value=75000.0, step=5000.0)
    with fc4:
        farmer_water = st.number_input(t("water_label"), min_value=0.0, max_value=100000000.0, value=60000.0, step=10000.0)

    # Prediction Action Button
    st.markdown("<br>", unsafe_allow_html=True)
    btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
    with btn_col2:
        predict_clicked = st.button(t("btn_predict"), use_container_width=True)

    # ONLY calculate when the button is clicked!
    if predict_clicked:
        with st.spinner("Calculating optimal recommendations..."):
            pred_data = run_local_prediction(
                selected_state, selected_district, selected_season,
                farmer_soil, float(farmer_land), float(farmer_budget), float(farmer_water)
            )
            st.session_state["prediction_result"] = pred_data

    # Check if a prediction exists
    prediction = st.session_state.get("prediction_result")

    # If NO prediction has been run yet (Fresh user visit):
    if not prediction:
        st.markdown(
            f"""
            <div style="background: #ffffff; border: 2px dashed #cbd5e1; border-radius: 14px;
                        padding: 36px 20px; text-align: center; margin-top: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.02);">
                <div style="font-size: 2.4rem; margin-bottom: 8px;">🌾</div>
                <h3 style="color: #0f172a; margin-bottom: 6px; font-weight: 700;">{t("ready_title")}</h3>
                <p style="color: #64748b; font-size: 0.95rem; max-width: 520px; margin: 0 auto;">
                    {t("ready_desc")}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # When prediction IS AVAILABLE (User clicked the button):
    else:
        best_crop = prediction["best_crop"]
        best_crop_translated = t_crop(best_crop)
        best_score = float(prediction["best_score"])
        best_rank = prediction["best_rank"]
        recs = prediction.get("recommendations", [])
        best_rec = recs[0] if recs else {}
        df_recs = pd.DataFrame(recs)

        # Spoken numbers for natural voice reading in current language
        bud_sp = format_indian_spoken_amount(farmer_budget, current_lang)
        wat_sp = format_indian_spoken_amount(farmer_water, current_lang)
        yield_sp = f"{best_rec.get('yield_quintals', 0):.1f}"
        rev_sp = format_indian_spoken_amount(best_rec.get('expected_revenue', 0), current_lang)
        cost_sp = format_indian_spoken_amount(best_rec.get('cultivation_cost', 0), current_lang)
        prof_sp = format_indian_spoken_amount(best_rec.get('net_profit', 0), current_lang)

        st_sp = t_state(selected_state)
        dist_sp = t_district(selected_district)
        ssn_sp = t_season(selected_season)
        soil_sp = t_soil(farmer_soil)

        if current_lang == "தமிழ்":
            speech_text = (
                f"விவசாயி மற்றும் நில விவரங்கள். "
                f"மாநிலம் {st_sp}, மாவட்டம் {dist_sp}, பருவம் {ssn_sp}, "
                f"மண் வகை {soil_sp}, நிலப்பரப்பு {farmer_land:.1f} ஏக்கர், "
                f"கிடைக்கும் பட்ஜெட் ரூபாய் {bud_sp}, கிடைக்கும் நீர் {wat_sp} லிட்டர். "
                f"உங்கள் நிலத்திற்கு சிறந்த பரிந்துரைக்கப்பட்ட பயிர் {best_crop_translated}. "
                f"எதிர்பார்க்கும் மகசூல் {yield_sp} குவிண்டால். "
                f"மொத்த அறுவடை வருமானம் ரூபாய் {rev_sp}. "
                f"மதிப்பிடப்பட்ட சாகுபடி செலவு ரூபாய் {cost_sp}. "
                f"எதிர்பார்க்கும் நிகர லாபம் ரூபாய் {prof_sp}. "
                f"பொருத்த நிலை மதிப்பீடு நூற்றுக்கு {best_score:.1f}."
            )
        elif current_lang == "हिन्दी":
            speech_text = (
                f"किसान एवं खेत विवरण। "
                f"राज्य {st_sp}, ज़िला {dist_sp}, मौसम {ssn_sp}, "
                f"मिट्टी {soil_sp}, भूमि {farmer_land:.1f} एकड़, "
                f"उपलब्ध बजट {bud_sp} रुपये, उपलब्ध जल {wat_sp} लीटर। "
                f"आपके खेत के लिए सर्वश्रेष्ठ अनुशंसित फसल {best_crop_translated}। "
                f"अपेक्षित उपज {yield_sp} क्विंटल। "
                f"कुल आमदनी {rev_sp} रुपये। "
                f"खेती लागत {cost_sp} रुपये। "
                f"शुद्ध लाभ {prof_sp} रुपये। "
                f"उपयुक्तता स्कोर 100 में से {best_score:.1f}।"
            )
        elif current_lang == "తెలుగు":
            speech_text = (
                f"రైతు మరియు పొలం వివరాలు. "
                f"రాష్ట్రం {st_sp}, జిల్లా {dist_sp}, కాలం {ssn_sp}, "
                f"నేల రకం {soil_sp}, విస్తీర్ణం {farmer_land:.1f} ఎకరాలు, "
                f"బడ్జెట్ రూపాయలు {bud_sp}, నీటి పరిమాణం {wat_sp} లీటర్లు. "
                f"సిఫారసు చేసిన ఉత్తమ పంట {best_crop_translated}. "
                f"దిగుబడి {yield_sp} క్వింటాళ్లు. "
                f"మొత్తం ఆదాయం రూపాయలు {rev_sp}. "
                f"సాగు ఖర్చు రూపాయలు {cost_sp}. "
                f"నికర లాభం రూపాయలు {prof_sp}. "
                f"అనుకూలత స్కోరు 100 కి {best_score:.1f}."
            )
        elif current_lang == "മലയാളം":
            speech_text = (
                f"കർഷകനും കൃഷിയിട വിവരങ്ങളും. "
                f"സംസ്ഥാനം {st_sp}, ജില്ല {dist_sp}, സീസൺ {ssn_sp}, "
                f"മണ്ണ് തരം {soil_sp}, വിസ്തീർണ്ണം {farmer_land:.1f} ഏക്കർ, "
                f"ബഡ്ജറ്റ് രൂപ {bud_sp}, ജല ലഭ്യത {wat_sp} ലിറ്റർ. "
                f"ഏറ്റവും അനുയോജ്യമായ വിള {best_crop_translated}. "
                f"പ്രതീക്ഷിക്കുന്ന വിളവ് {yield_sp} ക്വിന്റൽ. "
                f"മൊത്തം വരുമാനം രൂപ {rev_sp}. "
                f"കൃഷിച്ചെലവ് രൂപ {cost_sp}. "
                f"ലാഭം രൂപ {prof_sp}. "
                f"അനുയോജ്യത സ്കോർ {best_score:.1f}."
            )
        else:
            speech_text = (
                f"Farmer and field specifications. "
                f"State: {selected_state}, District: {selected_district}, Season: {selected_season}, "
                f"Soil Type: {farmer_soil}, Land Area: {farmer_land:.1f} acres, "
                f"Available Budget: Rupees {bud_sp}, Available Water: {wat_sp} litres. "
                f"Top recommended crop for your farm: {best_crop}. "
                f"Expected production yield: {yield_sp} quintals. "
                f"Expected gross harvest revenue: Rupees {rev_sp}. "
                f"Estimated cultivation expense: Rupees {cost_sp}. "
                f"Projected net in-hand profit: Rupees {prof_sp}. "
                f"Suitability decision score: {best_score:.1f} out of 100."
            )

        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

        # Responsive Voice Assistant Card (No Cutoff on Mobile!)
        render_unified_voice_card(speech_text, current_lang)

        # Result Header
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin: 10px 0 12px 0;">
                <div style="font-size: 1.55rem; font-weight: 800; color: #0f172a;">{t("pred_result_header")}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Hero Best Crop Card
        st.markdown(
            f"""
            <div class="best-crop-card">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap:14px;">
                    <div>
                        <span class="badge-pill badge-green">
                            🏆 {t("pred_rank")} #{best_rank}
                        </span>
                        <h2 style="margin: 10px 0 4px 0; font-size: 2.5rem; color: #065f46 !important;">🌾 {best_crop_translated}</h2>
                        <p style="margin: 0; color: #334155; font-size: 1.05rem;">{t("best_crop_announcement", crop=best_crop_translated, score=best_score)}</p>
                    </div>
                    <div style="text-align: right; background: #f0fdf4; border: 1px solid #bbf7d0; padding: 16px 24px; border-radius: 16px;">
                        <div style="font-size: 0.9rem; color: #166534; font-weight: 600;">{t("pred_decision_score")}</div>
                        <div style="font-size: 2.7rem; font-weight: 900; color: #059669; line-height: 1;">{best_score:.1f} <span style="font-size: 1.1rem; color: #64748b;">/ 100</span></div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Quick Download Buttons & Clear Option
        dl1, dl2, dl3 = st.columns([1, 1, 2])
        with dl1:
            st.download_button(
                t("btn_download_json"),
                data=json.dumps(prediction, indent=2),
                file_name=f"crop_advisory_{selected_state}_{best_crop}.json",
                mime="application/json",
                use_container_width=True
            )
        with dl2:
            if not df_recs.empty:
                st.download_button(
                    t("btn_download_csv"),
                    data=df_recs.to_csv(index=False),
                    file_name=f"crop_rankings_{selected_state}_{best_crop}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        with dl3:
            if st.button(t("btn_clear"), use_container_width=True):
                st.session_state["prediction_result"] = None
                st.rerun()

        # 6 Clean Metric Summary Cards
        st.markdown("<br>", unsafe_allow_html=True)
        card_cols = st.columns(6)

        # Localized card labels
        if current_lang == "தமிழ்":
            m_title0, m_l0_1, m_l0_2, m_l0_3, m_v0_2, m_v0_3 = "💰 சந்தை பகுப்பாய்வு", "சராசரி விலை", "போக்கு", "தேவை", "📈 அதிகம்", "வலுவானது"
            m_title1, m_l1_1, m_l1_2, m_l1_3, m_v1_2 = "💵 சாகுபடி செலவு", "ஏக்கர் செலவு", "நிலை", "லாப விகிதம்", "📉 சீரானது"
            m_title2, m_l2_1, m_l2_2, m_l2_3 = "💧 நீர் பகுப்பாய்வு", "இருப்பு நீர்", "தேவை நீர்", "நீர் திறன்"
            m_title3, m_l3_1, m_l3_2, m_l3_3, m_v3_2, m_v3_3 = "🌦️ வானிலை", "சராசரி வெப்பம்", "மழைப்பொழிவு", "அபாயம்", "இயல்பு", "பாதுகாப்பானது"
            m_title4, m_l4_1, m_l4_2, m_l4_3 = "🌱 மண் ஆரோக்கியம்", "மண் வகை", "கார-அமிலத்தன்மை", "கரிம சத்து"
            m_title5, m_l5_1, m_l5_2, m_l5_3, m_v5_1, m_v5_2, m_v5_3 = "🦠 பயிர் பாதுகாப்பு", "அபாய நிலை", "பூச்சிகள்", "பருவம்", "பாதுகாப்பானது", "எளிய தீர்வு", "வளர்ச்சி"
        elif current_lang == "हिन्दी":
            m_title0, m_l0_1, m_l0_2, m_l0_3, m_v0_2, m_v0_3 = "💰 बाज़ार विश्लेषण", "औसत भाव", "रुझान", "मांग", "📈 भारी", "मजबूत"
            m_title1, m_l1_1, m_l1_2, m_l1_3, m_v1_2 = "💵 खेती लागत", "प्रति एकड़", "स्थिति", "रिटर्न (ROI)", "📉 स्थिर"
            m_title2, m_l2_1, m_l2_2, m_l2_3 = "💧 जल विश्लेषण", "उपलब्ध", "आवश्यक", "दक्षता"
            m_title3, m_l3_1, m_l3_2, m_l3_3, m_v3_2, m_v3_3 = "🌦️ मौसम विश्लेषण", "तापमान", "वर्षा", "जोखिम", "सामान्य", "सुरक्षित"
            m_title4, m_l4_1, m_l4_2, m_l4_3 = "🌱 मिट्टी स्वास्थ्य", "मिट्टी", "पीएच स्तर", "कार्बन"
            m_title5, m_l5_1, m_l5_2, m_l5_3, m_v5_1, m_v5_2, m_v5_3 = "🦠 फसल सुरक्षा", "जोखिम", "कीट", "अवस्था", "सुरक्षित", "नियंत्रण योग्य", "वानस्पतिक"
        elif current_lang == "తెలుగు":
            m_title0, m_l0_1, m_l0_2, m_l0_3, m_v0_2, m_v0_3 = "💰 మార్కెట్ విశ్లేషణ", "సగటు ధర", "ట్రెండ్", "డిమాండ్", "📈 ఎక్కువ", "బలమైనది"
            m_title1, m_l1_1, m_l1_2, m_l1_3, m_v1_2 = "💵 సాగు ఖర్చు", "ఎకరానికి ఖర్చు", "స్థితి", "లాభ నిష్పత్తి", "📉 స్థిరమైనది"
            m_title2, m_l2_1, m_l2_2, m_l2_3 = "💧 నీటి విశ్లేషణ", "అందుబాటులో", "అవసరమైనది", "సామర్థ్యం"
            m_title3, m_l3_1, m_l3_2, m_l3_3, m_v3_2, m_v3_3 = "🌦️ వాతావరణం", "ఉష్ణోగ్రత", "వర్షపాతం", "ప్రమాదం", "సాధారణం", "రక్షితం"
            m_title4, m_l4_1, m_l4_2, m_l4_3 = "🌱 నేల ఆరోగ్యం", "నేల రకం", "పి.హెచ్ స్థాయి", "సేంద్రియ కర్బనం"
            m_title5, m_l5_1, m_l5_2, m_l5_3, m_v5_1, m_v5_2, m_v5_3 = "🦠 పంట రక్షణ", "ప్రమాద స్థాయి", "తెగుళ్లు", "దశ", "సురక్షితం", "నివారించదగినది", "ఎదుగుదల"
        elif current_lang == "മലയാളം":
            m_title0, m_l0_1, m_l0_2, m_l0_3, m_v0_2, m_v0_3 = "💰 വിപണി വിശകലനം", "ശരാശരി വില", "പ്രവണത", "ഡിമാൻഡ്", "📈 കൂടുതൽ", "ശക്തം"
            m_title1, m_l1_1, m_l1_2, m_l1_3, m_v1_2 = "💵 കൃഷിച്ചെലവ്", "ഏക്കർ ചെലവ്", "നിലവാരം", "റിട്ടേൺ (ROI)", "📉 സ്ഥിരം"
            m_title2, m_l2_1, m_l2_2, m_l2_3 = "💧 ജല വിശകലനം", "ലഭ്യം", "ആവശ്യം", "കാര്യക്ഷമത"
            m_title3, m_l3_1, m_l3_2, m_l3_3, m_v3_2, m_v3_3 = "🌦️ കാലാവസ്ഥ", "താപനില", "മഴ", "ഭീഷണി", "സാധാരണം", "സുരക്ഷിതം"
            m_title4, m_l4_1, m_l4_2, m_l4_3 = "🌱 മണ്ണ് ഗുണനിലവാരം", "മണ്ണ്", "പി.എച്ച്", "കാർബൺ"
            m_title5, m_l5_1, m_l5_2, m_l5_3, m_v5_1, m_v5_2, m_v5_3 = "🦠 വിള സംരക്ഷണം", "ഭീഷണി നില", "കീടങ്ങൾ", "ഘട്ടം", "സുരക്ഷിതം", "നിയന്ത്രണവിധേയം", "വളർച്ച"
        else:
            m_title0, m_l0_1, m_l0_2, m_l0_3, m_v0_2, m_v0_3 = "💰 Market Analysis", "Avg Price", "Trend", "Demand", "📈 High", "Strong"
            m_title1, m_l1_1, m_l1_2, m_l1_3, m_v1_2 = "💵 Cultivation Cost", "Cost/Acre", "Trend", "ROI", "📉 Stable"
            m_title2, m_l2_1, m_l2_2, m_l2_3 = "💧 Water Analysis", "Available", "Required", "Efficiency"
            m_title3, m_l3_1, m_l3_2, m_l3_3, m_v3_2, m_v3_3 = "🌦️ Weather Analysis", "Avg Temp", "Rainfall", "Risk", "Normal", "Low (Safe)"
            m_title4, m_l4_1, m_l4_2, m_l4_3 = "🌱 Soil Health", "Soil Type", "pH Level", "Carbon"
            m_title5, m_l5_1, m_l5_2, m_l5_3, m_v5_1, m_v5_2, m_v5_3 = "🦠 Crop Protection", "Risk Level", "Pests", "Stage", "Low (Safe)", "Manageable", "Vegetative"

        with card_cols[0]:
            st.markdown(
                f"""
                <div class="analysis-card">
                    <div class="analysis-card-title">{m_title0}</div>
                    <div class="analysis-row"><span>{m_l0_1}</span><span class="analysis-val">₹{best_rec.get('historical_market_price', 2450):,.0f}</span></div>
                    <div class="analysis-row"><span>{m_l0_2}</span><span style="color:#059669; font-weight:700;">{m_v0_2}</span></div>
                    <div class="analysis-row"><span>{m_l0_3}</span><span class="analysis-val">{m_v0_3}</span></div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with card_cols[1]:
            c_per_acre = float(best_rec.get('cultivation_cost', 28500)) / max(0.1, float(farmer_land))
            roi_val = float(best_rec.get('expected_revenue', 70000)) / max(1.0, float(best_rec.get('cultivation_cost', 28500)))
            st.markdown(
                f"""
                <div class="analysis-card">
                    <div class="analysis-card-title">{m_title1}</div>
                    <div class="analysis-row"><span>{m_l1_1}</span><span class="analysis-val">₹{c_per_acre:,.0f}</span></div>
                    <div class="analysis-row"><span>{m_l1_2}</span><span style="color:#0284c7; font-weight:700;">{m_v1_2}</span></div>
                    <div class="analysis-row"><span>{m_l1_3}</span><span style="color:#059669; font-weight:700;">{roi_val:.2f}x</span></div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with card_cols[2]:
            req_w = float(best_rec.get('required_water_litres', 58000))
            avail_w = float(farmer_water)
            w_eff = min(100, int((avail_w / max(1.0, req_w)) * 100)) if avail_w <= req_w else int((req_w / max(1.0, avail_w)) * 100)
            st.markdown(
                f"""
                <div class="analysis-card">
                    <div class="analysis-card-title">{m_title2}</div>
                    <div class="analysis-row"><span>{m_l2_1}</span><span class="analysis-val">{avail_w:,.0f} L</span></div>
                    <div class="analysis-row"><span>{m_l2_2}</span><span class="analysis-val">{req_w:,.0f} L</span></div>
                    <div class="analysis-row"><span>{m_l2_3}</span><span style="color:#0284c7; font-weight:700;">{w_eff}%</span></div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with card_cols[3]:
            st.markdown(
                f"""
                <div class="analysis-card">
                    <div class="analysis-card-title">{m_title3}</div>
                    <div class="analysis-row"><span>{m_l3_1}</span><span class="analysis-val">29.4 °C</span></div>
                    <div class="analysis-row"><span>{m_l3_2}</span><span class="analysis-val">{m_v3_2}</span></div>
                    <div class="analysis-row"><span>{m_l3_3}</span><span style="color:#059669; font-weight:700;">{m_v3_3}</span></div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with card_cols[4]:
            st.markdown(
                f"""
                <div class="analysis-card">
                    <div class="analysis-card-title">{m_title4}</div>
                    <div class="analysis-row"><span>{m_l4_1}</span><span class="analysis-val">{soil_sp}</span></div>
                    <div class="analysis-row"><span>{m_l4_2}</span><span class="analysis-val">6.8</span></div>
                    <div class="analysis-row"><span>{m_l4_3}</span><span class="analysis-val">0.95%</span></div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with card_cols[5]:
            st.markdown(
                f"""
                <div class="analysis-card">
                    <div class="analysis-card-title">{m_title5}</div>
                    <div class="analysis-row"><span>{m_l5_1}</span><span style="color:#059669; font-weight:700;">{m_v5_1}</span></div>
                    <div class="analysis-row"><span>{m_l5_2}</span><span class="analysis-val">{m_v5_2}</span></div>
                    <div class="analysis-row"><span>{m_l5_3}</span><span class="analysis-val">{m_v5_3}</span></div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Why This Crop Section (Fully localized)
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader(t("why_this_crop"))
        if current_lang == "தமிழ்":
            reasons_list = [
                f"{st_sp} மாநிலத்தில் {ssn_sp} பருவத்திற்கு உகந்த பயிர் தேர்வு.",
                f"உங்கள் நிலத்தின் {soil_sp} மண் தன்மைக்கு மிகச் சிறந்த பொருத்தம்.",
                f"சாகுபடி செலவு உங்கள் பட்ஜெட்டிற்குள் (₹{farmer_budget:,.0f}) அடங்கி, ₹{best_rec.get('net_profit', 0):,.0f} நிகர லாபம் ஈட்டக்கூடியது.",
                "தண்ணீர் தேவை உங்களிடம் உள்ள நீர் அளவுக்குள் அடங்கி, குறைந்த நோய் அபாயம் கொண்டது."
            ]
        elif current_lang == "हिन्दी":
            reasons_list = [
                f"{st_sp} राज्य में {ssn_sp} मौसम के लिए सबसे उपयुक्त फसल।",
                f"आपके खेत की {soil_sp} मिट्टी के लिए अत्यधिक अनुकूल।",
                f"खेती लागत आपके ₹{farmer_budget:,.0f} बजट के भीतर है और ₹{best_rec.get('net_profit', 0):,.0f} शुद्ध लाभ संभव है।",
                "जल की मांग उपलब्ध जल के अनुसार है एवं मौसम व रोग का जोखिम कम है।"
            ]
        elif current_lang == "తెలుగు":
            reasons_list = [
                f"{st_sp} రాష్ట్రంలో {ssn_sp} కాలానికి అత్యంత అనుకూలమైన పంట.",
                f"మీ పొలంలోని {soil_sp} నేల రకానికి ఎంతో అనుకూలం.",
                f"సాగు ఖర్చు మీ ₹{farmer_budget:,.0f} బడ్జెట్‌కు సరిపోతుంది మరియు ₹{best_rec.get('net_profit', 0):,.0f} నికర లాభం సాధించవచ్చు.",
                "నీటి అవసరం మీ లభ్యతకు అనుగుణంగా ఉంది మరియు తెగుళ్ల ముప్పు తక్కువ."
            ]
        elif current_lang == "മലയാളം":
            reasons_list = [
                f"{st_sp} സംസ്ഥാനത്ത് {ssn_sp} സീസണിന് ഏറ്റവും അനുയോജ്യമായ വിള.",
                f"നിങ്ങളുടെ കൃഷിയിടത്തിലെ {soil_sp} മണ്ണിന് ഏറ്റവും യോജിച്ചത്.",
                f"കൃഷിച്ചെലവ് നിങ്ങളുടെ ₹{farmer_budget:,.0f} ബജറ്റിൽ ഒതുങ്ങുന്നതും ₹{best_rec.get('net_profit', 0):,.0f} അറ്റാദായം നൽകുന്നതുമാണ്.",
                "ജല ലഭ്യതയ്ക്ക് അനുയോജ്യമായതും രോഗസാധ്യത കുറഞ്ഞതുമാണ്."
            ]
        else:
            reasons_list = [
                f"Optimal agro-climatic fit for {ssn_sp} season in {st_sp}.",
                f"Highly compatible with your farm's {soil_sp} soil profile.",
                f"Cultivation cost fits within your ₹{farmer_budget:,.0f} budget with projected ₹{best_rec.get('net_profit', 0):,.0f} net margin.",
                "Water demand matches your supply with low climate and disease risk."
            ]

        r_cols = st.columns(2)
        for idx, r_text in enumerate(reasons_list):
            with r_cols[idx % 2]:
                st.markdown(
                    f"""
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 14px 18px; border-radius: 12px; margin-bottom: 12px; display: flex; align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                        <span style="color: #059669; font-size: 1.3rem; margin-right: 12px; font-weight: bold;">✓</span>
                        <span style="color: #1e293b; font-weight: 500; font-size: 0.95rem;">{r_text}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Top 5 Crop Recommendations Table
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader(f"{t('top5_header')} — {dist_sp} ({ssn_sp})")

        if not df_recs.empty:
            display_df = df_recs[[
                "rank", "crop", "decision_score", "data_coverage",
                "expected_revenue", "cultivation_cost", "required_water_litres",
                "yield_quintals", "disease_risk", "weather_risk"
            ]].copy()

            display_df["crop"] = display_df["crop"].apply(t_crop)

            display_df.columns = [
                t("col_rank"), t("col_crop"), t("col_score"), t("col_coverage"),
                t("col_revenue"), t("col_cost"), t("col_water"),
                t("col_yield"), t("col_disease"), t("col_weather")
            ]

            st.dataframe(
                display_df.style.format({
                    t("col_score"): "{:.1f}",
                    t("col_revenue"): "₹{:,.0f}",
                    t("col_cost"): "₹{:,.0f}",
                    t("col_water"): "{:,.0f} L",
                    t("col_yield"): "{:,.1f} q",
                    t("col_disease"): "{:.1f}%",
                    t("col_weather"): "{:.1f}%"
                }),
                use_container_width=True,
                hide_index=True
            )

        # ============================================================
        # 7 FARMER-FRIENDLY VISUAL DECISION MODULES (FULLY MULTILINGUAL)
        # ============================================================

        st.markdown("<br>", unsafe_allow_html=True)
        if current_lang == "தமிழ்":
            sec_title = "🌾 விவசாயத் திட்டமிடல் & நடைமுறை வழிகாட்டிகள்"
            sec_sub = "பணம், சந்தை மண்டி விலை, பாசன அட்டவணை, உரம் மற்றும் பயிர் பாதுகாப்பு வழிகாட்டிகள்."
            tab_labels = [
                "💰 வரவு-செலவு & லாப விவரம்",
                "🏪 மண்டி விலை & விற்பனை வழிகாட்டி",
                "💧 நீர் தேவை & பாசன அட்டவணை",
                "🌦️ வானிலை பாதுகாப்பு ஆலோசனை",
                "🧪 உர மேலாண்மை (ஏக்கருக்கு)",
                "🛡️ பயிர் நோய்கள் & எளிய தீர்வுகள்",
                "📅 4 கட்ட விவசாய கால அட்டவணை"
            ]
        elif current_lang == "हिन्दी":
            sec_title = "🌾 व्यावहारिक कृषि योजना एवं निर्णय मार्गदर्शिका"
            sec_sub = "मुनाफ़ा, मंडी भाव, सिंचाई समय, खाद मात्रा एवं कीट सुरक्षा की सरल जानकारी।"
            tab_labels = [
                "💰 आय-व्यय एवं शुद्ध लाभ",
                "🏪 मंडी भाव एवं बिक्री गाइड",
                "💧 जल आवश्यकता एवं सिंचाई सारणी",
                "🌦️ मौसम एवं बारिश सुरक्षा गाइड",
                "🧪 खाद व उर्वरक मात्रा (प्रति एकड़)",
                "🛡️ फसल रोग एवं सरल उपचार",
                "📅 4-चरणीय फसल चक्र समय-सारणी"
            ]
        elif current_lang == "తెలుగు":
            sec_title = "🌾 సమగ్ర వ్యవసాయ ప్రణాళిక & నిర్ణయ మార్గదర్శి"
            sec_sub = "లాభాలు, మార్కెట్ ధరలు, నీటి యాజమాన్యం, ఎరువులు మరియు పురుగుల నివారణ సమాచారం."
            tab_labels = [
                "💰 ఆదాయం & లాభాల విశ్లేషణ",
                "🏪 మార్కెట్ ధరలు & అమ్మకపు గైడ్",
                "💧 నీటి అవసరం & తడుల షెడ్యూల్",
                "🌦️ వాతావరణ భద్రతా మార్గదర్శి",
                "🧪 ఎరువుల యాజమాన్యం (ఎకరానికి)",
                "🛡️ పంట తెగుళ్లు & సులభ నివారణలు",
                "📅 4 దశల పంట కాలక్రమం"
            ]
        elif current_lang == "മലയാളം":
            sec_title = "🌾 പ്രായോഗിക കാർഷിക ആസൂത്രണ ഗൈഡ്"
            sec_sub = "വരുമാനം, വിപണി വില, ജലസേചന ഷെഡ്യൂൾ, വളപ്രയോഗം, കീടനിയന്ത്രണം എന്നിവയുടെ ലളിതമായ വിവരങ്ങൾ."
            tab_labels = [
                "💰 വരുമാന-ചെലവ് & ലാഭവിവരം",
                "🏪 വിപണി വില & വിൽപ്പന ഗൈഡ്",
                "💧 ജല ആവശ്യകത & നന ഷെഡ്യൂൾ",
                "🌦️ കാലാവസ്ഥാ സുരക്ഷാ മാർഗ്ഗങ്ങൾ",
                "🧪 വളപ്രയോഗം (ഏക്കറിന്)",
                "🛡️ വിള രോഗങ്ങളും പരിഹാരങ്ങളും",
                "📅 4 ഘട്ട കൃഷി കലണ്ടർ"
            ]
        else:
            sec_title = "🌾 Practical Farm Planning & Decision Guide"
            sec_sub = "Easy-to-understand visual guides for money, mandi prices, water scheduling, fertilizer, and pest protection."
            tab_labels = [
                "💰 Profit & Money Breakdown",
                "🏪 Mandi Price & Selling Guide",
                "💧 Water Need & Irrigation Schedule",
                "🌦️ Weather & Climate Safety",
                "🧪 Fertilizer & Nutrients (Per Acre)",
                "🛡️ Crop Diseases & Remedies",
                "📅 4-Step Farming Calendar"
            ]

        st.subheader(sec_title)
        st.caption(sec_sub)

        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tab_labels)

        # ── TAB 1: PROFIT & MONEY BREAKDOWN ────────────────────────
        with tab1:
            net_prof = float(best_rec.get("net_profit", 0))
            tot_rev = float(best_rec.get("expected_revenue", 0))
            tot_cost = float(best_rec.get("cultivation_cost", 0))
            y_val = best_rec.get("yield_quintals", 0)

            if current_lang == "தமிழ்":
                st.markdown(f"#### 💰 **{best_crop_translated}** பயிருக்கான நிதி விவரங்கள் ({farmer_land:.1f} ஏக்கர்)")
                t1_c1_t, t1_c1_s = "மொத்த சாகுபடி செலவு", "விதை, உரம், ஆட்கள் கூலி மற்றும் உழவு"
                t1_c2_t, t1_c2_s = "எதிர்பார்க்கும் அறுவடை வருமானம்", f"{y_val:.1f} குவிண்டால் மகசூலில் இருந்து"
                t1_c3_t, t1_c3_s = "நிகர லாபம் (கைக்கு வரும் பணம்)", "மொத்த வருமானத்தில் இருந்து செலவு கழித்து"
                t1_chart_t = "##### 📊 எந்த பயிர் அதிக நிகர லாபம் தரும்?"
                chart_y_label = "நிகர லாபம் (₹)"
            elif current_lang == "हिन्दी":
                st.markdown(f"#### 💰 **{best_crop_translated}** के लिए वित्तीय विवरण ({farmer_land:.1f} एकड़)")
                t1_c1_t, t1_c1_s = "कुल खेती लागत", "बीज, खाद, मजदूरी एवं जुताई"
                t1_c2_t, t1_c2_s = "अपेक्षित कुल आय", f"{y_val:.1f} क्विंटल पैदावार से"
                t1_c3_t, t1_c3_s = "अनुमानित शुद्ध बचत (लाभ)", "कुल आय में से लागत घटाकर"
                t1_chart_t = "##### 📊 कौन सी फसल सबसे अधिक शुद्ध लाभ देती है?"
                chart_y_label = "शुद्ध लाभ (₹)"
            elif current_lang == "తెలుగు":
                st.markdown(f"#### 💰 **{best_crop_translated}** కొరకు ఆర్థిక వివరాలు ({farmer_land:.1f} ఎకరాలు)")
                t1_c1_t, t1_c1_s = "మొత్తం సాగు ఖర్చు", "విత్తనాలు, ఎరువులు, కూలీలు మరియు దుక్కి"
                t1_c2_t, t1_c2_s = "అంచనా ఆదాయం", f"{y_val:.1f} క్వింటాళ్ల దిగుబడి నుండి"
                t1_c3_t, t1_c3_s = "నికర లాభం (చేతికి వచ్చే ఆదాయం)", "మొత్తం ఆదాయం నుండి ఖర్చులు తీసివేయగా"
                t1_chart_t = "##### 📊 ఏ పంట అత్యధిక నికర లాభాన్ని ఇస్తుంది?"
                chart_y_label = "నికర లాభం (₹)"
            elif current_lang == "മലയാളം":
                st.markdown(f"#### 💰 **{best_crop_translated}** കൃഷിക്കുള്ള സാമ്പത്തിക വിവരങ്ങൾ ({farmer_land:.1f} ഏക്കർ)")
                t1_c1_t, t1_c1_s = "ആകെ കൃഷിച്ചെലവ്", "വിത്ത്, വളം, കൂലി, ഉഴവ്"
                t1_c2_t, t1_c2_s = "പ്രതീക്ഷിക്കുന്ന വിളവ് വരുമാനം", f"{y_val:.1f} ക്വിന്റൽ വിളവിൽ നിന്ന്"
                t1_c3_t, t1_c3_s = "പ്രതീക്ഷിക്കുന്ന അറ്റാദായം (ലാഭം)", "വരുമാനത്തിൽ നിന്ന് ചെലവ് കുറച്ച ശേഷം"
                t1_chart_t = "##### 📊 ഏത് വിളയാണ് ഏറ്റവും കൂടുതൽ ലാഭം നൽകുന്നത്?"
                chart_y_label = "അറ്റാദായം (₹)"
            else:
                st.markdown(f"#### 💰 Financial Summary for **{best_crop_translated}** on {farmer_land:.1f} Acres")
                t1_c1_t, t1_c1_s = "TOTAL CULTIVATION EXPENSE", "Seeds, Fertilizer, Labor & Watering"
                t1_c2_t, t1_c2_s = "EXPECTED HARVEST INCOME", f"From {y_val:.1f} quintals yield"
                t1_c3_t, t1_c3_s = "ESTIMATED IN-HAND NET PROFIT", "Income minus cultivation cost"
                t1_chart_t = "##### 📊 Which Crop Gives the Highest In-Hand Profit?"
                chart_y_label = "Net Profit (₹)"

            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.markdown(
                    f"""
                    <div style="background:#fef2f2; border:2px solid #fecaca; border-radius:14px; padding:20px; text-align:center;">
                        <div style="font-size:2rem;">💵</div>
                        <div style="font-size:1.6rem; font-weight:900; color:#dc2626; margin-top:6px;">₹{tot_cost:,.0f}</div>
                        <div style="font-size:0.85rem; font-weight:700; color:#475569; margin-top:4px;">{t1_c1_t}</div>
                        <div style="font-size:0.78rem; color:#64748b; margin-top:2px;">{t1_c1_s}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with m_col2:
                st.markdown(
                    f"""
                    <div style="background:#eff6ff; border:2px solid #bfdbfe; border-radius:14px; padding:20px; text-align:center;">
                        <div style="font-size:2rem;">🌾</div>
                        <div style="font-size:1.6rem; font-weight:900; color:#2563eb; margin-top:6px;">₹{tot_rev:,.0f}</div>
                        <div style="font-size:0.85rem; font-weight:700; color:#475569; margin-top:4px;">{t1_c2_t}</div>
                        <div style="font-size:0.78rem; color:#64748b; margin-top:2px;">{t1_c2_s}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with m_col3:
                st.markdown(
                    f"""
                    <div style="background:#f0fdf4; border:2px solid #86efac; border-radius:14px; padding:20px; text-align:center;">
                        <div style="font-size:2rem;">🏆</div>
                        <div style="font-size:1.6rem; font-weight:900; color:#059669; margin-top:6px;">₹{net_prof:,.0f}</div>
                        <div style="font-size:0.85rem; font-weight:700; color:#475569; margin-top:4px;">{t1_c3_t}</div>
                        <div style="font-size:0.78rem; color:#64748b; margin-top:2px;">{t1_c3_s}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(t1_chart_t)
            df_recs_ov = df_recs.copy()
            df_recs_ov["Crop"] = df_recs_ov["crop"].apply(t_crop)
            df_recs_ov[chart_y_label] = df_recs_ov["expected_revenue"] - df_recs_ov["cultivation_cost"]
            fig_ov = px.bar(
                df_recs_ov, x="Crop", y=chart_y_label,
                color="Crop", text=chart_y_label,
                color_discrete_sequence=["#059669", "#0284c7", "#d97706", "#7c3aed", "#dc2626"]
            )
            fig_ov.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
            fig_ov.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=380, showlegend=False)
            st.plotly_chart(fig_ov, use_container_width=True)

        # ── TAB 2: MANDI PRICE & SELLING GUIDE ─────────────────────
        with tab2:
            base_p = float(best_rec.get("historical_market_price", 2400))
            msp_val = round(base_p * 0.92, 0)

            if current_lang == "தமிழ்":
                st.markdown("#### 🏪 சந்தை விலை மற்றும் அதிக லாபத்திற்கு எங்கு விற்பனை செய்வது?")
                t2_c1_t, t2_c1_s = "தற்போதைய மண்டி விலை", "ஒழுங்குமுறை விற்பனைக் கூடங்களில் (குவிண்டாலுக்கு)"
                t2_c2_t, t2_c2_s = "அரசு குறைந்தபட்ச ஆதரவு விலை (MSP)", "அரசாங்கத்தால் உறுதிசெய்யப்பட்ட அடிப்படை விலை"
                t2_c3_t, t2_c3_v, t2_c3_s = "சந்தை தேவை நிலை", "📈 அதிக தேவை", "விலை அதிகரிக்கும் வாய்ப்பு அதிகம்"
                t2_adv_h = f"💡 {dist_sp} விவசாயிகளுக்கான முக்கிய விற்பனை ஆலோசனைகள்"
                t2_b1 = f"<strong>ஒழுங்குமுறை விற்பனைக்கூடம் அல்லது e-NAM மூலம் விற்கவும்:</strong> இடைத்தரகர்களைத் தவிர்த்து முழு அரசு மண்டி விலையைப் (₹{base_p:,.0f}/குவிண்டால்) பெறுங்கள்."
                t2_b2 = "<strong>உலர்த்துதல் மற்றும் தரம் பிரித்தல்:</strong> அறுவடை செய்த தானியங்களை 12% ஈரப்பதத்திற்குள் நன்கு உலர்த்தி விற்றால் முதல் தர உயர் விலை கிடைக்கும்."
                t2_b3 = "<strong>சிறந்த விற்பனை நேரம்:</strong> அறுவடை முடிந்தவுடன் அவசரப்பட்டு விற்காமல், 4 முதல் 6 வாரங்கள் கழித்து விற்றால் கூடுதல் விலை கிடைக்கும்."
            elif current_lang == "हिन्दी":
                st.markdown("#### 🏪 मंडी भाव एवं अधिकतम लाभ के लिए बिक्री मार्गदर्शन")
                t2_c1_t, t2_c1_s = "वर्तमान मंडी भाव", "पंजीकृत एपीएमसी मंडियों में प्रति क्विंटल"
                t2_c2_t, t2_c2_s = "सरकारी न्यूनतम समर्थन मूल्य (MSP)", "सरकार द्वारा निर्धारित न्यूनतम सुरक्षित मूल्य"
                t2_c3_t, t2_c3_v, t2_c3_s = "बाज़ार मांग का रुझान", "📈 भारी मांग", "भाव बढ़ने की प्रबल संभावना"
                t2_adv_h = f"💡 {dist_sp} के किसानों के लिए प्रमुख बिक्री सुझाव"
                t2_b1 = f"<strong>सरकारी मंडी या e-NAM पोर्टल पर बेचें:</strong> बिचौलियों से बचें और पूरा उचित भाव (₹{base_p:,.0f}/क्विंटल) प्राप्त करें।"
                t2_b2 = "<strong>सुखाना एवं ग्रेडिंग:</strong> फसल को मंडी ले जाने से पहले नमी 12% से कम रखें ताकि 'ए' ग्रेड का उच्चतम भाव मिले।"
                t2_b3 = "<strong>उचित बिक्री समय:</strong> कटाई के तुरंत बाद भारी आवक होती है, 4 से 6 सप्ताह बाद बेचने पर अधिक भाव मिल सकता है।"
            elif current_lang == "తెలుగు":
                st.markdown("#### 🏪 మార్కెట్ ధరలు & గరిష్ట లాభం కోసం అమ్మకపు గైడ్")
                t2_c1_t, t2_c1_s = "ప్రస్తుత మార్కెట్ ధర", "రిజిస్టర్డ్ ఏపీఎంసీ మార్కెట్లలో ప్రతి క్వింటాలుకు"
                t2_c2_t, t2_c2_s = "ప్రభుత్వ కనీస మద్దతు ధర (MSP)", "ప్రభుత్వం నిర్ణయించిన కనీస రక్షణ ధర"
                t2_c3_t, t2_c3_v, t2_c3_s = "మార్కెట్ డిమాండ్ ట్రెండ్", "📈 అధిక డిమాండ్", "ధరలు పెరిగే అవకాశం ఉంది"
                t2_adv_h = f"💡 {dist_sp} రైతులకు ముఖ్యమైన అమ్మకపు సూచనలు"
                t2_b1 = f"<strong>ఏపీఎంసీ మార్కెట్ లేదా e-NAM పోర్టల్ ద్వారా అమ్మండి:</strong> దళారులను ఆశ్రయించకుండా పూర్తి మార్కెట్ ధరను (₹{base_p:,.0f}/క్వింటాలు) పొందండి."
                t2_b2 = "<strong>ఆరబెట్టడం & గ్రేడింగ్:</strong> మార్కెట్‌కు తీసుకెళ్లే ముందు పంటలో తేమను 12% కంటే తక్కువ ఉండేలా చూసుకుంటే గ్రేడ్-A ధర లభిస్తుంది."
                t2_b3 = "<strong>సరైన అమ్మకపు సమయం:</strong> కోత పూర్తయిన వెంటనే కాకుండా, 4 నుండి 6 వారాల తర్వాత అమ్మితే మంచి ధర వస్తుంది."
            elif current_lang == "മലയാളം":
                st.markdown("#### 🏪 വിപണി വിലയും കൂടുതൽ ലാഭത്തിന് എവിടെ വിൽക്കണം എന്ന വിവരങ്ങളും")
                t2_c1_t, t2_c1_s = "നിലവിലെ വിപണി വില", "രജിസ്റ്റർ ചെയ്ത എപിഎംസി വിപണിയിൽ ക്വിന്റലിന്"
                t2_c2_t, t2_c2_s = "സർക്കാർ താങ്ങുവില (MSP)", "സർക്കാർ ഉറപ്പുനൽകുന്ന കുറഞ്ഞ വില"
                t2_c3_t, t2_c3_v, t2_c3_s = "വിപണി ഡിമാൻഡ്", "📈 ഉയർന്ന ഡിമാൻഡ്", "വില ഉയരുന്ന പ്രവണത"
                t2_adv_h = f"💡 {dist_sp} കർഷകർക്കുള്ള പ്രധാന വിപണന ഉപദേശങ്ങൾ"
                t2_b1 = f"<strong>എപിഎംസി മാർക്കറ്റ് അല്ലെങ്കിൽ e-NAM പോർട്ടൽ വഴി വിൽക്കുക:</strong> ഇടനിലക്കാരെ ഒഴിവാക്കി മുഴുവൻ വിലയും (₹{base_p:,.0f}/ക്വിന്റൽ) ഉറപ്പാക്കുക."
                t2_b2 = "<strong>ഉണക്കലും തരംതിരിക്കലും:</strong> ഈർപ്പം 12 ശതമാനത്തിൽ താഴെയാക്കി തരംതിരിച്ച് വിറ്റാൽ ഒന്നാംതരം ഉയർന്ന വില ലഭിക്കും."
                t2_b3 = "<strong>വിൽപ്പനയ്ക്കുള്ള മികച്ച സമയം:</strong> വിളവെടുപ്പ് തിരക്ക് കഴിഞ്ഞ് 4 മുതൽ 6 ആഴ്ചകൾക്ക് ശേഷം വിറ്റാൽ കൂടുതൽ വില ലഭിക്കും."
            else:
                st.markdown("#### 🏪 Market Price & Where to Sell for Maximum Profit")
                t2_c1_t, t2_c1_s = "CURRENT MANDI PRICE", "per quintal in registered APMC mandis"
                t2_c2_t, t2_c2_s = "GOVERNMENT MINIMUM PRICE (MSP)", "Guaranteed minimum support floor"
                t2_c3_t, t2_c3_v, t2_c3_s = "MARKET DEMAND TREND", "📈 High Demand", "Prices trending upwards"
                t2_adv_h = f"💡 Top Selling Advice for {dist_sp} Farmers"
                t2_b1 = f"<strong>Sell at APMC Mandi or e-NAM Portal:</strong> Avoid unauthorized middlemen to secure full mandi benchmark rates (₹{base_p:,.0f}/q)."
                t2_b2 = "<strong>Drying & Grading:</strong> Dry grains to under 12% moisture content before taking to market to receive Grade-A pricing."
                t2_b3 = "<strong>Best Selling Window:</strong> Market prices generally peak 4 to 6 weeks after initial harvest rush."

            mp_col1, mp_col2, mp_col3 = st.columns(3)
            with mp_col1:
                st.markdown(
                    f"""
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:18px; text-align:center;">
                        <div style="color:#64748b; font-size:0.85rem; font-weight:700;">{t2_c1_t}</div>
                        <div style="font-size:1.8rem; font-weight:900; color:#059669; margin:4px 0;">₹{base_p:,.0f}</div>
                        <div style="color:#475569; font-size:0.8rem;">{t2_c1_s}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with mp_col2:
                st.markdown(
                    f"""
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:18px; text-align:center;">
                        <div style="color:#64748b; font-size:0.85rem; font-weight:700;">{t2_c2_t}</div>
                        <div style="font-size:1.8rem; font-weight:900; color:#2563eb; margin:4px 0;">₹{msp_val:,.0f}</div>
                        <div style="color:#475569; font-size:0.8rem;">{t2_c2_s}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with mp_col3:
                st.markdown(
                    f"""
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:18px; text-align:center;">
                        <div style="color:#64748b; font-size:0.85rem; font-weight:700;">{t2_c3_t}</div>
                        <div style="font-size:1.8rem; font-weight:900; color:#059669; margin:4px 0;">{t2_c3_v}</div>
                        <div style="color:#475569; font-size:0.8rem;">{t2_c3_s}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style="background:#f8fafc; border-left:4px solid #059669; padding:16px 20px; border-radius:8px;">
                    <h5 style="margin:0 0 6px 0; color:#065f46;">{t2_adv_h}</h5>
                    <ul style="margin:0; padding-left:20px; color:#334155; font-size:0.92rem; line-height:1.6;">
                        <li>{t2_b1}</li>
                        <li>{t2_b2}</li>
                        <li>{t2_b3}</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

        # ── TAB 3: WATER & IRRIGATION PLANNER ──────────────────────
        with tab3:
            req_w = float(best_rec.get("required_water_litres", 50000))
            avail_w = float(farmer_water)
            diff_w = avail_w - req_w

            if current_lang == "தமிழ்":
                st.markdown("#### 💧 நீர் மேலாண்மை: உங்கள் தண்ணீர் அளவு போதுமானதா?")
                t3_c1_t = f"தேவைப்படும் நீர் ({farmer_land:.1f} ஏக்கருக்கு)"
                t3_c2_t = "உங்களிடம் உள்ள நீர் அளவு"
                t3_c3_t = "நீர் இருப்பு நிலை"
                t3_stat = "✅ போதுமான நீர் உள்ளது (பாதுகாப்பானது)" if diff_w >= 0 else "⚠️ நீர் பற்றாக்குறை (சிக்கனமாக பயன்படுத்தவும்)"
                t3_sub_h = "🚿 3 கட்ட ஸ்மார்ட் பாசன வழிகாட்டுதல்"
                t3_s1_t, t3_s1_d = "விதைத்தல் மற்றும் முளைக்கும் பருவம் (மிதமான பாசனம்)", "விதைத்தவுடன் நிலம் ஈரமாக இருக்கும்படி மிதமான நீர் பாய்ச்சவும். அதிக நீர் தேங்க விடாதீர்கள்."
                t3_s2_t, t3_s2_d = "வளர்ச்சிப் பருவம் (8-10 நாட்களுக்கு ஒருமுறை)", "பயிரின் வளர்ச்சி காலத்தில் மண் காய்ந்து போகாமல் சீரான இடைவெளியில் நீர் பாய்ச்சவும்."
                t3_s3_t, t3_s3_d = "பூக்கும் மற்றும் கதிர் வரும் பருவம் (மிகவும் முக்கியமானது)", "இந்த பருவத்தில் தண்ணீர் பற்றாக்குறை ஏற்படக்கூடாது. கட்டாயம் நீர் பாய்ச்ச வேண்டும்."
            elif current_lang == "हिन्दी":
                st.markdown("#### 💧 जल संतुलन: क्या आपके पास पर्याप्त पानी है?")
                t3_c1_t = f"कुल आवश्यक जल ({farmer_land:.1f} एकड़)"
                t3_c2_t = "उपलब्ध जल"
                t3_c3_t = "जल सुरक्षा स्थिति"
                t3_stat = "✅ पर्याप्त जल उपलब्ध (सुरक्षित)" if diff_w >= 0 else "⚠️ जल कमी (संरक्षण आवश्यक)"
                t3_sub_h = "🚿 3-चरणीय स्मार्ट सिंचाई नियम"
                t3_s1_t, t3_s1_d = "बुवाई एवं अंकुरण (हल्की सिंचाई)", "बुवाई के समय हल्की सिंचाई करें ताकि बीज आसानी से अंकुरित हों। पानी जमा न होने दें।"
                t3_s2_t, t3_s2_d = "वानस्पतिक वृद्धि (हर 8–10 दिन में)", "पौधे की बढ़वार के समय मिट्टी की नमी अनुसार नियमित पानी दें।"
                t3_s3_t, t3_s3_d = "फूल व दाना बनने की अवस्था (अति महत्वपूर्ण)", "इस अवस्था में पानी की कमी न होने दें, यह पैदावार के लिए सबसे जरूरी है।"
            elif current_lang == "తెలుగు":
                st.markdown("#### 💧 నీటి బడ్జెట్: మీ వద్ద ఉన్న నీరు సరిపోతుందా?")
                t3_c1_t = f"అవసరమైన మొత్తం నీరు ({farmer_land:.1f} ఎకరాలకు)"
                t3_c2_t = "అందుబాటులో ఉన్న నీరు"
                t3_c3_t = "నీటి భద్రత"
                t3_stat = "✅ సరిపడా నీరు ఉంది (సురక్షితం)" if diff_w >= 0 else "⚠️ నీటి కొరత (పొదుపుగా వాడండి)"
                t3_sub_h = "🚿 3 దశల సమర్థవంతమైన నీటి పారుదల విధానం"
                t3_s1_t, t3_s1_d = "విత్తడం & మొలకెత్తడం (తేలికపాటి తడి)", "విత్తిన వెంటనే నేల తేమగా ఉండేలా స్వల్పంగా నీరు పెట్టండి."
                t3_s2_t, t3_s2_d = "పైరు ఎదుగుదల దశ (ప్రతి 8-10 రోజులకు)", "మొక్క ఎదుగుతున్న సమయంలో క్రమం తప్పకుండా తడులు ఇవ్వండి."
                t3_s3_t, t3_s3_d = "పూత & గింజ పాలుపోసుకునే దశ (చాలా ముఖ్యం)", "ఈ దశలో నీటి కొరత రానివ్వవద్దు, ఇది దిగుబడికి అత్యంత కీలకం."
            elif current_lang == "മലയാളം":
                st.markdown("#### 💧 ജല ലഭ്യത: ആവശ്യത്തിന് ജലം ലഭ്യമാണോ?")
                t3_c1_t = f"ആവശ്യമായ ആകെ ജലം ({farmer_land:.1f} ഏക്കറിന്)"
                t3_c2_t = "ലഭ്യമായ ജലം"
                t3_c3_t = "ജല സുരക്ഷ"
                t3_stat = "✅ ആവശ്യത്തിന് ജലമുണ്ട് (സുരക്ഷിതം)" if diff_w >= 0 else "⚠️ ജലക്ഷാമം (ശ്രദ്ധയോടെ ഉപയോഗിക്കുക)"
                t3_sub_h = "🚿 3 ഘട്ടങ്ങളായുള്ള ശാസ്ത്രീയ ജലസേചന രീതി"
                t3_s1_t, t3_s1_d = "വിതയ്ക്കലും മുളയ്ക്കലും (നേരിയ നന)", "വിത്ത് മുളയ്ക്കാൻ പാകത്തിന് നേരിയ നന നൽകുക."
                t3_s2_t, t3_s2_d = "വളർച്ചാ ഘട്ടം (8-10 ദിവസത്തിൽ ഒരിക്കൽ)", "ചെടിയുടെ വളർച്ചാ ഘട്ടത്തിൽ ആവശ്യാനുസരണം നനയ്ക്കുക."
                t3_s3_t, t3_s3_d = "പൂവിടലും ധാന്യ രൂപീകരണവും (ഏറ്റവും പ്രധാനം)", "ഈ സമയത്ത് നന മുടങ്ങരുത്, ഇത് ഉയർന്ന വിളവിന് അത്യന്താപേക്ഷിതമാണ്."
            else:
                st.markdown("#### 💧 Water Balance: Is Your Water Supply Enough?")
                t3_c1_t = f"WATER NEEDED ({farmer_land:.1f} ACRES)"
                t3_c2_t = "YOUR AVAILABLE WATER"
                t3_c3_t = "WATER STATUS"
                t3_stat = "✅ Surplus (Safe & Fully Sufficient)" if diff_w >= 0 else "⚠️ Deficit (Drip / Conservation Recommended)"
                t3_sub_h = "🚿 3-Stage Smart Irrigation Guidelines"
                t3_s1_t, t3_s1_d = "Sowing & Germination (Light Watering)", "Keep soil lightly moist so seeds sprout easily without waterlogging."
                t3_s2_t, t3_s2_d = "Vegetative Growth (Every 8–10 Days)", "Irrigate in morning or late evening depending on weather."
                t3_s3_t, t3_s3_d = "Flowering & Grain Filling (CRITICAL STAGE)", "Water shortage at this time reduces yield. Ensure timely watering."

            w_col1, w_col2, w_col3 = st.columns(3)
            with w_col1:
                st.markdown(
                    f"""
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:18px; text-align:center;">
                        <div style="color:#64748b; font-size:0.85rem; font-weight:700;">{t3_c1_t}</div>
                        <div style="font-size:1.8rem; font-weight:900; color:#0284c7; margin:4px 0;">{req_w:,.0f} L</div>
                        <div style="color:#475569; font-size:0.8rem;">Full season estimate</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with w_col2:
                st.markdown(
                    f"""
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:18px; text-align:center;">
                        <div style="color:#64748b; font-size:0.85rem; font-weight:700;">{t3_c2_t}</div>
                        <div style="font-size:1.8rem; font-weight:900; color:#059669; margin:4px 0;">{avail_w:,.0f} L</div>
                        <div style="color:#475569; font-size:0.8rem;">From borewell/canal</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with w_col3:
                status_color = "#059669" if diff_w >= 0 else "#d97706"
                st.markdown(
                    f"""
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:18px; text-align:center;">
                        <div style="color:#64748b; font-size:0.85rem; font-weight:700;">{t3_c3_t}</div>
                        <div style="font-size:1.15rem; font-weight:900; color:{status_color}; margin:8px 0;">{t3_stat}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"##### {t3_sub_h}")
            st.markdown(
                f"""
                <div style="display:flex; flex-direction:column; gap:10px; margin-top:8px;">
                    <div style="background:#f0fdf4; border-left:4px solid #10b981; padding:12px 16px; border-radius:6px;">
                        <strong>🌱 1. {t3_s1_t}:</strong> {t3_s1_d}
                    </div>
                    <div style="background:#eff6ff; border-left:4px solid #3b82f6; padding:12px 16px; border-radius:6px;">
                        <strong>🌿 2. {t3_s2_t}:</strong> {t3_s2_d}
                    </div>
                    <div style="background:#fefce8; border-left:4px solid #eab308; padding:12px 16px; border-radius:6px;">
                        <strong>🌾 3. {t3_s3_t}:</strong> {t3_s3_d}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # ── TAB 4: WEATHER & MONSOON SAFETY ────────────────────────
        with tab4:
            if current_lang == "தமிழ்":
                st.markdown(f"#### 🌦️ {dist_sp} மாவட்டத்திற்கான வானிலை மற்றும் காலநிலை பாதுகாப்பு ஆலோசனை")
                t4_c1_t, t4_c1_v, t4_c1_s = "வானிலை அபாய நிலை", "குறைந்த அபாயம் (பாதுகாப்பானது)", "இயல்பான மழைப்பொழிவு எதிர்பார்க்கப்படுகிறது"
                t4_c2_t, t4_c2_s = "கனமழை & வெள்ளப் பாதுகாப்பு", "வயலில் வடிகால் வாய்க்கால்களைச் சீரமைத்து நீர் தேங்காமல் பார்த்துக் கொள்ளவும்."
                t4_c3_t, t4_c3_s = "வெப்ப அலை & வறட்சி பாதுகாப்பு", "மண்ணின் ஈரப்பதத்தைக் காக்க மூடாக்கு இடவும், மாலையில் நீர் பாய்ச்சவும்."
            elif current_lang == "हिन्दी":
                st.markdown(f"#### 🌦️ {dist_sp} के लिए मौसम सुरक्षा एवं कृषि परामर्श")
                t4_c1_t, t4_c1_v, t4_c1_s = "मौसम जोखिम स्तर", "कम जोखिम (सुरक्षित)", "सामान्य बारिश की संभावना"
                t4_c2_t, t4_c2_s = "भारी वर्षा से बचाव", "खेत में जल निकासी की नालियां साफ रखें ताकि पानी का जमाव न हो।"
                t4_c3_t, t4_c3_s = "तेज धूप व सूखे से बचाव", "नमी बनाए रखने के लिए मल्चिंग करें एवं शाम के समय ही सिंचाई करें।"
            elif current_lang == "తెలుగు":
                st.markdown(f"#### 🌦️ {dist_sp} జిల్లాకు వాతావరణ భద్రత మరియు రక్షణ సలహాలు")
                t4_c1_t, t4_c1_v, t4_c1_s = "వాతావరణ ప్రమాద స్థాయి", "తక్కువ ప్రమాదం (రక్షితం)", "సాధారణ వర్షపాతం అంచనా"
                t4_c2_t, t4_c2_s = "భారీ వర్షాల రక్షణ", "పొలంలో నీరు నిల్వ ఉండకుండా మురుగు కాలువలను సిద్ధంగా ఉంచండి."
                t4_c3_t, t4_c3_s = "ఎండ & కరువు రక్షణ", "తేమ ఆవిరి కాకుండా మల్చింగ్ వాడండి, సాయంత్రం వేళల్లో నీరు పెట్టండి."
            elif current_lang == "മലയാളം":
                st.markdown(f"#### 🌦️ {dist_sp} ജില്ലയ്ക്കായുള്ള കാലാവസ്ഥാ സുരക്ഷാ നിർദ്ദേശങ്ങൾ")
                t4_c1_t, t4_c1_v, t4_c1_s = "കാലാവസ്ഥാ ഭീഷണി", "കുറഞ്ഞ ഭീഷണി (സുരക്ഷിതം)", "സാധാരണ മഴ പ്രതീക്ഷിക്കാം"
                t4_c2_t, t4_c2_s = "കനത്ത മഴ മുന്നറിയിപ്പ്", "കൃഷിയിടത്തിൽ വെള്ളം കെട്ടിക്കിടക്കാതെ ഡ്രെയിനേജ് സൗകര്യം ഉറപ്പാക്കുക."
                t4_c3_t, t4_c3_s = "കടുത്ത വേനൽ / വരൾച്ച പ്രതിരോധം", "മണ്ണിലെ ഈർപ്പം നിലനിർത്താൻ പുതയിടുക, വൈകുന്നേരങ്ങളിൽ നനയ്ക്കുക."
            else:
                st.markdown(f"#### 🌦️ Climate Safety & Weather Advisory for {dist_sp}")
                t4_c1_t, t4_c1_v, t4_c1_s = "WEATHER RISK LEVEL", "Low Risk (Safe)", "Normal rainfall pattern expected"
                t4_c2_t, t4_c2_s = "Heavy Monsoon & Flood Defense", "Clear drainage trenches around your field perimeter so excess rainwater runs off rapidly without waterlogging."
                t4_c3_t, t4_c3_s = "Heatwave & Drought Defense", "Spread straw or dry leaves (mulch) between crop rows to trap soil moisture. Irrigate strictly after 4:00 PM."

            we_col1, we_col2 = st.columns(2)
            with we_col1:
                st.markdown(
                    f"""
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:20px; box-shadow:0 2px 6px rgba(0,0,0,0.03);">
                        <div style="color:#059669; font-weight:800; font-size:1.1rem;">🛡️ {t4_c1_t}</div>
                        <div style="font-size:1.8rem; font-weight:900; color:#059669; margin:8px 0;">{t4_c1_v}</div>
                        <div style="color:#64748b; font-size:0.85rem;">{t4_c1_s}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with we_col2:
                st.markdown(
                    f"""
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:20px; box-shadow:0 2px 6px rgba(0,0,0,0.03);">
                        <div style="color:#0284c7; font-weight:800; font-size:1.1rem;">🌧️ {t4_c2_t}</div>
                        <p style="color:#475569; font-size:0.88rem; margin:8px 0 0 0; line-height:1.5;">{t4_c2_s}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:20px; box-shadow:0 2px 6px rgba(0,0,0,0.03);">
                    <div style="color:#d97706; font-weight:800; font-size:1.1rem;">☀️ {t4_c3_t}</div>
                    <p style="color:#475569; font-size:0.88rem; margin:8px 0 0 0; line-height:1.5;">{t4_c3_s}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        # ── TAB 5: FERTILIZER & SOIL NUTRIENTS ──────────────────────
        with tab5:
            if current_lang == "தமிழ்":
                st.markdown(f"#### 🧪 {best_crop_translated} பயிருக்கான உர மேலாண்மை (ஒரு ஏக்கருக்கு)")
                st.caption("மண்ணின் வளத்தைக் காத்து அதிக மகசூல் பெற பரிந்துரைக்கப்பட்ட உர அளவு.")
                t5_f1_t, t5_f1_d = "யூரியா (நைட்ரஜன் - N)", "45 – 55 கிலோ / ஏக்கர்"
                t5_f2_t, t5_f2_d = "டி.ஏ.பி (பாஸ்பரஸ் - P)", "35 – 40 கிலோ / ஏக்கர்"
                t5_f3_t, t5_f3_d = "பொட்டாஷ் (பொட்டாசியம் - K)", "25 – 30 கிலோ / ஏக்கர்"
                t5_f4_t, t5_f4_d = "இயற்கை தொழுவுரம் (FYM)", "4 – 5 டன் / ஏக்கர்"
                t5_how_h = "🧪 உரம் இடும் முறை:"
                t5_how_d = "விதைக்கும் போது முழு அளவு டி.ஏ.பி, பொட்டாஷ் மற்றும் பாதி அளவு யூரியாவை அடியுரமாக இடவும். மீதமுள்ள யூரியாவை பயிர் நட்ட 25 மற்றும் 45-ஆம் நாட்களில் இரண்டு முறை பிரித்து மேலுரமாக இடவும்."
            elif current_lang == "हिन्दी":
                st.markdown(f"#### 🧪 {best_crop_translated} के लिए प्रति एकड़ अनुशंसित खाद एवं उर्वरक")
                st.caption("मिट्टी की उर्वरता बनाए रखते हुए अधिकतम उपज के लिए सही मात्रा।")
                t5_f1_t, t5_f1_d = "यूरिया (नाइट्रोजन - N)", "45 – 55 किग्रा / एकड़"
                t5_f2_t, t5_f2_d = "डीएपी (फास्फोरस - P)", "35 – 40 किग्रा / एकड़"
                t5_f3_t, t5_f3_d = "पोटाश (एमओपी - K)", "25 – 30 किग्रा / एकड़"
                t5_f4_t, t5_f4_d = "जैविक गोबर खाद (FYM)", "4 – 5 टन / एकड़"
                t5_how_h = "🧪 खाद डालने की सही विधि:"
                t5_how_d = "बुवाई के समय पूरा डीएपी, पोटाश एवं आधी यूरिया बेसल डोज के रूप में डालें। बची हुई यूरिया को 25वें और 45वें दिन दो बार में खड़ी फसल में दें।"
            elif current_lang == "తెలుగు":
                st.markdown(f"#### 🧪 {best_crop_translated} పంటకు ఎకరానికి సిఫార్సు చేసిన ఎరువుల ప్రణాళిక")
                st.caption("భూసారాన్ని కాపాడుతూ అధిక దిగుబడిని సాధించేందుకు ఎరువుల మోతాదు.")
                t5_f1_t, t5_f1_d = "యూరియా (నత్రజని - N)", "45 – 55 కిలోలు / ఎకరం"
                t5_f2_t, t5_f2_d = "డి.ఎ.పి (భాస్వరం - P)", "35 – 40 కిలోలు / ఎకరం"
                t5_f3_t, t5_f3_d = "పొటాష్ (పొటాషియం - K)", "25 – 30 కిలోలు / ఎకరం"
                t5_f4_t, t5_f4_d = "పశువుల ఎరువు (FYM)", "4 – 5 టన్నులు / ఎకరం"
                t5_how_h = "🧪 ఎరువులు వేసే సరైన పద్ధతి:"
                t5_how_d = "విత్తే సమయంలో మొత్తం డి.ఎ.పి, పొటాష్ మరియు సగం యూరియాను ఆఖరి దుక్కిలో వేయండి. మిగిలిన యూరియాను 25 మరియు 45 రోజుల వ్యవధిలో రెండు దఫాలుగా పైపాటుగా వేయండి."
            elif current_lang == "മലയാളം":
                st.markdown(f"#### 🧪 {best_crop_translated} വിളയ്ക്കുള്ള വളപ്രയോഗ നിർദ്ദേശം (ഒരു ഏക്കറിന്)")
                st.caption("മണ്ണിന്റെ ഫലഭൂയിഷ്ഠത നിലനിർത്തി ഉയർന്ന വിളവ് നേടാനുള്ള വളങ്ങൾ.")
                t5_f1_t, t5_f1_d = "യൂറിയ (നൈട്രജൻ - N)", "45 – 55 കിലോഗ്രാം / ഏക്കർ"
                t5_f2_t, t5_f2_d = "ഡി.എ.പി (ഫോസ്ഫറസ് - P)", "35 – 40 കിലോഗ്രാം / ഏക്കർ"
                t5_f3_t, t5_f3_d = "പൊട്ടാഷ് (പൊട്ടാസ്യം - K)", "25 – 30 കിലോഗ്രാം / ഏക്കർ"
                t5_f4_t, t5_f4_d = "ജൈവ വളം / ചാണകപ്പൊടി", "4 – 5 ടൺ / ഏക്കർ"
                t5_how_h = "🧪 വളപ്രയോഗ രീതി:"
                t5_how_d = "വിതയ്ക്കുമ്പോൾ മുഴുവൻ ഡി.എ.പിയും പൊട്ടാഷും പകുതി യൂറിയയും അടിവളമായി നൽകുക. ബാക്കി യൂറിയ 25, 45 ദിവസങ്ങളിൽ മേൽവളമായി നൽകുക."
            else:
                st.markdown(f"#### 🧪 Recommended Fertilizer Plan (Per Acre) for {best_crop_translated}")
                st.caption("Apply these doses per acre for healthy crops and high yield without wasting money.")
                t5_f1_t, t5_f1_d = "Urea (Nitrogen N)", "45 – 55 kg / acre"
                t5_f2_t, t5_f2_d = "DAP (Phosphorus P)", "35 – 40 kg / acre"
                t5_f3_t, t5_f3_d = "MOP (Potassium K)", "25 – 30 kg / acre"
                t5_f4_t, t5_f4_d = "Farmyard Manure (FYM)", "4 – 5 tons / acre"
                t5_how_h = "🧪 How to Apply Fertilizer Step-by-Step:"
                t5_how_d = "Apply all DAP, Potash, and 50% Urea as basal dose at time of sowing. Apply the remaining 50% Urea in two split doses during active growth (day 25 and day 45)."

            fert_c1, fert_c2, fert_c3, fert_c4 = st.columns(4)
            with fert_c1:
                st.markdown(
                    f"""
                    <div style="background:#ffffff; border:1.5px solid #e2e8f0; border-top:4px solid #10b981; border-radius:12px; padding:16px; text-align:center;">
                        <div style="font-weight:700; color:#0f172a;">{t5_f1_t}</div>
                        <div style="font-size:1.5rem; font-weight:900; color:#059669; margin:6px 0;">{t5_f1_d.split('/')[0].strip()}</div>
                        <div style="color:#64748b; font-size:0.78rem;">Leaf growth & green color</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with fert_c2:
                st.markdown(
                    f"""
                    <div style="background:#ffffff; border:1.5px solid #e2e8f0; border-top:4px solid #3b82f6; border-radius:12px; padding:16px; text-align:center;">
                        <div style="font-weight:700; color:#0f172a;">{t5_f2_t}</div>
                        <div style="font-size:1.5rem; font-weight:900; color:#2563eb; margin:6px 0;">{t5_f2_d.split('/')[0].strip()}</div>
                        <div style="color:#64748b; font-size:0.78rem;">Strong root development</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with fert_c3:
                st.markdown(
                    f"""
                    <div style="background:#ffffff; border:1.5px solid #e2e8f0; border-top:4px solid #f59e0b; border-radius:12px; padding:16px; text-align:center;">
                        <div style="font-weight:700; color:#0f172a;">{t5_f3_t}</div>
                        <div style="font-size:1.5rem; font-weight:900; color:#d97706; margin:6px 0;">{t5_f3_d.split('/')[0].strip()}</div>
                        <div style="color:#64748b; font-size:0.78rem;">Grain weight & disease resistance</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with fert_c4:
                st.markdown(
                    f"""
                    <div style="background:#ffffff; border:1.5px solid #e2e8f0; border-top:4px solid #8b5cf6; border-radius:12px; padding:16px; text-align:center;">
                        <div style="font-weight:700; color:#0f172a;">{t5_f4_t}</div>
                        <div style="font-size:1.5rem; font-weight:900; color:#7c3aed; margin:6px 0;">{t5_f4_d.split('/')[0].strip()}</div>
                        <div style="color:#64748b; font-size:0.78rem;">Improves soil health & water holding</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style="background:#f0fdf4; border-left:4px solid #10b981; padding:16px 20px; border-radius:8px;">
                    <h5 style="margin:0 0 6px 0; color:#065f46;">{t5_how_h}</h5>
                    <p style="margin:0; color:#334155; font-size:0.9rem; line-height:1.5;">{t5_how_d}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        # ── TAB 6: PEST & DISEASE REMEDIES ─────────────────────────
        with tab6:
            if current_lang == "தமிழ்":
                st.markdown(f"#### 🛡️ {best_crop_translated} பயிருக்கான பூச்சி மற்றும் நோய் பாதுகாப்பு வழிகாட்டி")
                st.caption("முக்கிய பூச்சி-நோய்கள் மற்றும் எளிய இயற்கை/வேதியியல் தீர்வுகள்.")
                p1_name = "🐛 சாறு உறிஞ்சும் பூச்சிகள் / அசுவினி"
                p1_sym = "இலைகள் சுருங்குதல், மஞ்சள் நிறமாதல், இலைகளில் பிசுபிசுப்பு தன்மை."
                p1_rem = "ஒரு லிட்டர் தண்ணீருக்கு 5 மிலி வேப்பெண்ணெய் கலந்து அதிகாலையில் தெளிக்கவும், அல்லது இமிடாகுளோப்ரிட் (0.5 மிலி/லிட்டர்) தெளிக்கவும்."
                p2_name = "🍂 இலைப்புள்ளி நோய் / பூஞ்சாண கருகல்"
                p2_sym = "கீழ்ப்பகுதி இலைகளில் பழுப்பு அல்லது கருப்பு வட்ட வடிவ புள்ளிகள் தோன்றுதல்."
                p2_rem = "ஒரு லிட்டர் தண்ணீருக்கு 2 கிராம் மான்கோசெப் (Mancozeb) கலந்து தெளிக்கவும். 12 நாட்கள் கழித்து மீண்டும் தெளிக்கவும்."
                p3_name = "🌱 வேரழுகல் நோய்"
                p3_sym = "வயலில் நீர் தேங்குவதால் இளம் நாற்றுகளின் வேர் அழுகி வாடுதல்."
                p3_rem = "வயலில் நீர் தேங்காமல் வடிகால் அமைக்கவும். விதைக்கும் முன் ட்ரைக்கோடெர்மா விரிடி (4 கிராம்/கிலோ விதை) கொண்டு விதை நேர்த்தி செய்யவும்."
                sym_lbl, rem_lbl = "அறிகுறிகள்:", "💊 எளிய தீர்வு:"
            elif current_lang == "हिन्दी":
                st.markdown(f"#### 🛡️ {best_crop_translated} के लिए कीट एवं रोग नियंत्रण समाधान")
                st.caption("सामान्य रोग, उनके लक्षण एवं त्वरित सरल उपचार।")
                p1_name = "🐛 रस चूसक कीट / माहू (एफिड्स)"
                p1_sym = "पत्तियां मुड़ना, पीली पड़ना और पत्तियों पर चिपचिपापन।"
                p1_rem = "प्रति लीटर पानी में 5 मिली नीम का तेल मिलाकर सुबह के समय छिड़काव करें, अथवा इमिडाक्लोप्रिड (0.5 मिली/लीटर) डालें।"
                p2_name = "🍂 पत्ती धब्बा / फफूंद जनित झुलसा"
                p2_sym = "निचली पत्तियों पर भूरे या काले गोल धब्बे दिखाई देना।"
                p2_rem = "प्रति लीटर पानी में 2 ग्राम मैंकोजेब (Mancozeb) मिलाकर छिड़काव करें।"
                p3_name = "🌱 जड़ गलन / डैम्पिंग ऑफ"
                p3_sym = "पानी जमा होने से पौधों की जड़ें सड़ना व पौधे मुरझाना।"
                p3_rem = "खेत में जल निकासी अच्छी रखें। बुवाई से पहले ट्राइकोडर्मा से बीज उपचार अवश्य करें।"
                sym_lbl, rem_lbl = "लक्षण:", "💊 सरल उपचार:"
            elif current_lang == "తెలుగు":
                st.markdown(f"#### 🛡️ {best_crop_translated} పంటకు పురుగులు మరియు తెగుళ్ల నివారణ మార్గదర్శి")
                st.caption("ముఖ్యమైన తెగుళ్లు, లక్షణాలు మరియు సులభమైన నివారణ పద్ధతులు.")
                p1_name = "🐛 రసం పీల్చే పురుగులు / పేనుబంక"
                p1_sym = "ఆకులు ముడుచుకుపోవడం, పసుపు రంగులోకి మారడం."
                p1_rem = "లీటరు నీటికి 5 మి.లీ వేపనూనె కలిపి ఉదయం వేళ పిచికారీ చేయండి."
                p2_name = "🍂 ఆకుమచ్చ తెగులు / శిలీంధ్ర తెగులు"
                p2_sym = "ఆకులపై గోధుమ లేదా నలుపు రంగు మచ్చలు ఏర్పడటం."
                p2_rem = "లీటరు నీటికి 2 గ్రాముల మ్యాంకోజెబ్ (Mancozeb) కలిపి పిచికారీ చేయండి."
                p3_name = "🌱 వేరుకుళ్లు తెగులు"
                p3_sym = "నీరు నిల్వ ఉండటం వల్ల వేర్లు కుళ్ళిపోయి మొక్కలు వాడిపోవడం."
                p3_rem = "మురుగునీటి పారుదల సౌకర్యం కల్పించండి. విత్తన శుద్ధి కోసం ట్రైకోడెర్మా వాడండి."
                sym_lbl, rem_lbl = "లక్షణాలు:", "💊 సులభ నివారణ:"
            elif current_lang == "മലയാളം":
                st.markdown(f"#### 🛡️ {best_crop_translated} വിളയിലെ കീട-രോഗ നിയന്ത്രണ മാർഗ്ഗങ്ങൾ")
                st.caption("പ്രധാന രോഗങ്ങളും അവയ്ക്കുള്ള ലളിതമായ പ്രതിവിധികളും.")
                p1_name = "🐛 നീരൂറ്റിക്കുടിക്കുന്ന പ്രാണികൾ / മുഞ്ഞ"
                p1_sym = "ഇലകൾ ചുരുളുക, മഞ്ഞനിറം പടരുക."
                p1_rem = "ഒരു ലിറ്റർ വെള്ളത്തിൽ 5 മില്ലി വേപ്പെണ്ണ കലക്കി രാവിലെ തളിക്കുക."
                p2_name = "🍂 ഇലപ്പുള്ളി രോഗം / കുമിൾബാധ"
                p2_sym = "ഇലകളിൽ തവിട്ടുനിറത്തിലുള്ള പുള്ളികൾ കാണപ്പെടുക."
                p2_rem = "ഒരു ലിറ്റർ വെള്ളത്തിൽ 2 ഗ്രാം മാങ്കോസെബ് (Mancozeb) തളിക്കുക."
                p3_name = "🌱 വേരുചീയൽ രോഗം"
                p3_sym = "വെള്ളക്കെട്ട് കാരണം ചെടികളുടെ വേരുകൾ ചീഞ്ഞ് ഉണങ്ങിപ്പോകുക."
                p3_rem = "നീർവാർച്ച ഉറപ്പാക്കുക. ട്രൈക്കോഡെർമ ഉപയോഗിച്ച് വിത്തുചികിത്സ നടത്തുക."
                sym_lbl, rem_lbl = "ലക്ഷണങ്ങൾ:", "💊 പരിഹാരം:"
            else:
                st.markdown(f"#### 🛡️ Crop Health & Pest Protection for {best_crop_translated}")
                st.caption("Common problems and their easy organic & chemical solutions.")
                p1_name = "🐛 Sucking Pests / Aphids"
                p1_sym = "Curled leaves, yellowing tips, sticky substance on foliage."
                p1_rem = "Spray Neem Oil (5ml per litre of water) early morning, or Imidacloprid (0.5ml/L) if infestation is severe."
                p2_name = "🍂 Leaf Spot / Fungal Blight"
                p2_sym = "Small brown or black circular spots appearing on lower leaves."
                p2_rem = "Spray Mancozeb (2g per litre of water) or Copper Oxychloride at first sign of spots. Repeat after 12 days."
                p3_name = "🌱 Root Rot / Damping Off"
                p3_sym = "Seedlings collapse at ground level due to water stagnation."
                p3_rem = "Ensure good drainage. Treat seeds with Trichoderma viride (4g/kg seed) before planting."
                sym_lbl, rem_lbl = "Symptoms:", "💊 Easy Remedy:"

            st.markdown(
                f"""
                <div style="display:flex; flex-direction:column; gap:14px; margin-top:10px;">
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:16px; box-shadow:0 2px 6px rgba(0,0,0,0.03);">
                        <div style="color:#dc2626; font-weight:800; font-size:1.0rem;">{p1_name}</div>
                        <p style="color:#64748b; font-size:0.85rem; margin:6px 0;"><strong>{sym_lbl}</strong> {p1_sym}</p>
                        <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:8px; padding:10px; font-size:0.85rem; color:#065f46;">
                            <strong>{rem_lbl}</strong> {p1_rem}
                        </div>
                    </div>
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:16px; box-shadow:0 2px 6px rgba(0,0,0,0.03);">
                        <div style="color:#dc2626; font-weight:800; font-size:1.0rem;">{p2_name}</div>
                        <p style="color:#64748b; font-size:0.85rem; margin:6px 0;"><strong>{sym_lbl}</strong> {p2_sym}</p>
                        <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:8px; padding:10px; font-size:0.85rem; color:#065f46;">
                            <strong>{rem_lbl}</strong> {p2_rem}
                        </div>
                    </div>
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:16px; box-shadow:0 2px 6px rgba(0,0,0,0.03);">
                        <div style="color:#dc2626; font-weight:800; font-size:1.0rem;">{p3_name}</div>
                        <p style="color:#64748b; font-size:0.85rem; margin:6px 0;"><strong>{sym_lbl}</strong> {p3_sym}</p>
                        <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:8px; padding:10px; font-size:0.85rem; color:#065f46;">
                            <strong>{rem_lbl}</strong> {p3_rem}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # ── TAB 7: 4-STEP FARMING TIMELINE ─────────────────────────
        with tab7:
            if current_lang == "தமிழ்":
                st.markdown(f"#### 📅 **{best_crop_translated}** பயிருக்கான 4 கட்ட விவசாய கால அட்டவணை")
                st.caption("உழவு நாள் முதல் அறுவடை மற்றும் சந்தை விற்பனை வரையிலான முழுமையான கால அட்டவணை.")
                ph1_t = "படி 1: நிலம் தயாரித்தல் மற்றும் விதைத்தல் (நாட்கள் 1 – 15)"
                ph1_d = "நிலத்தை 2–3 முறை நன்கு உழுது பண்படுத்தவும். இயற்கை தொழுவுரம் மற்றும் அடியுரம் இடவும். தரமான விதைகளை விதைத்து மிதமான முதல் பாசனம் செய்யவும்."
                ph2_t = "படி 2: பயிர் வளர்ச்சி மற்றும் களையெடுத்தல் (நாட்கள் 20 – 40)"
                ph2_d = "20-ஆம் நாளில் முதல் களை எடுக்கவும். யூரியா மேலுரம் இட்டு 8–10 நாட்களுக்கு ஒருமுறை பாசனம் செய்யவும். இலைகளின் அடிப்பகுதியில் பூச்சிகள் உள்ளதா என கண்காணிக்கவும்."
                ph3_t = "படி 3: பூ பூத்தல் மற்றும் கதிர் உருவாதல் (நாட்கள் 45 – 75)"
                ph3_d = "பூக்கும் காலத்தில் நீர் பற்றாக்குறை வராமல் கட்டாயம் நீர் பாய்ச்சவும். பூச்சிகள் தென்பட்டால் வேப்பெண்ணெய் தெளிக்கவும்."
                ph4_t = "படி 4: அறுவடை மற்றும் சந்தை விற்பனை (நாட்கள் 80 – 100)"
                ph4_d = "அறுவடைக்கு 15 நாட்களுக்கு முன் நீர் பாய்ச்சுவதை நிறுத்தவும். நன்கு காய்ந்த பிறகு அறுவடை செய்து 12% ஈரப்பதத்திற்குள் உலர்த்தி மண்டியில் விற்கவும்."
            elif current_lang == "हिन्दी":
                st.markdown(f"#### 📅 **{best_crop_translated}** के लिए 4-चरणीय फसल चक्र समय-सारणी")
                st.caption("जुताई से लेकर मंडी बिक्री तक का पूरा चरणबद्ध कार्यक्रम।")
                ph1_t = "चरण 1: खेत की तैयारी एवं बुवाई (दिन 1 – 15)"
                ph1_d = "खेत की 2–3 बार जुताई करें, गोबर खाद एवं बेसल खाद मिलाएं। उपचारित बीजों की बुवाई कर हल्की सिंचाई करें।"
                ph2_t = "चरण 2: वानस्पतिक वृद्धि एवं निराई (दिन 20 – 40)"
                ph2_d = "20वें दिन पहली निराई-गुड़ाई करें। यूरिया की खुराक दें और 8-10 दिनों में सिंचाई करें।"
                ph3_t = "चरण 3: फूल व दाना भराव (दिन 45 – 75)"
                ph3_d = "फूल आने पर समय पर पानी दें। कीड़े दिखने पर नीम तेल का छिड़काव करें।"
                ph4_t = "चरण 4: कटाई एवं मंडी बिक्री (दिन 80 – 100)"
                ph4_d = "कटाई से 15 दिन पहले पानी बंद करें। फसल पकने पर धूप में कटाई कर 12% नमी पर मंडी में बेचें।"
            elif current_lang == "తెలుగు":
                st.markdown(f"#### 📅 **{best_crop_translated}** కొరకు 4 దశల పంట కాలక్రమం")
                st.caption("దుక్కి నుండి పంట కోసి మార్కెట్‌లో అమ్మే వరకు పూర్తి కాలక్రమం.")
                ph1_t = "దశ 1: నేల తయారీ మరియు విత్తడం (రోజులు 1 – 15)"
                ph1_d = "పొలాన్ని 2-3 సార్లు దున్నండి, పశువుల ఎరువు వేయండి. విత్తన శుద్ధి చేసిన విత్తనాలను నాటి తేలికపాటి తడి ఇవ్వండి."
                ph2_t = "దశ 2: ఎదుగుదల మరియు కలుపు నివారణ (రోజులు 20 – 40)"
                ph2_d = "20వ రోజు మొదటి కలుపు తీయండి. యూరియా వేసి 8-10 రోజులకు ఒకసారి నీరు పెట్టండి."
                ph3_t = "దశ 3: పూత మరియు గింజ కట్టే దశ (రోజులు 45 – 75)"
                ph3_d = "పూత దశలో నీటి ఎద్దడి రాకుండా చూసుకోండి. పురుగులు కనిపిస్తే వేపనూనె పిచికారీ చేయండి."
                ph4_t = "దశ 4: కోత మరియు మార్కెట్ అమ్మకం (రోజులు 80 – 100)"
                ph4_d = "కోతకు 15 రోజుల ముందు నీరు ఆపండి. ధాన్యాన్ని 12% తేమతో ఆరబెట్టి మార్కెట్‌లో అమ్మండి."
            elif current_lang == "മലയാളം":
                st.markdown(f"#### 📅 **{best_crop_translated}** വിളയ്ക്കുള്ള 4 ഘട്ട കൃഷി കലണ്ടർ")
                st.caption("നിലമൊരുക്കൽ മുതൽ വിപണി വിൽപ്പന വരെയുള്ള കൃത്യമായ സമയക്രമം.")
                ph1_t = "ഘട്ടം 1: നിലമൊരുക്കലും വിതയ്ക്കലും (ദിവസം 1 – 15)"
                ph1_d = "നിലം 2-3 തവണ ഉഴുതുമറിച്ച് ജൈവവളം ചേർക്കുക. വിത്തുവിതച്ച് നേരിയ നന നൽകുക."
                ph2_t = "ഘട്ടം 2: വളർച്ചയും കളനിയന്ത്രണവും (ദിവസം 20 – 40)"
                ph2_d = "20-ാം ദിവസം കള പറിക്കുക. യൂറിയ ചേർത്ത് ആവശ്യാനുസരണം നനയ്ക്കുക."
                ph3_t = "ഘട്ടം 3: പൂവിടലും ധാന്യ രൂപീകരണവും (ദിവസം 45 – 75)"
                ph3_d = "പൂവിടുന്ന സമയത്ത് കൃത്യമായി നനയ്ക്കുക. കീടങ്ങളെ നിയന്ത്രിക്കാൻ വേപ്പെണ്ണ തളിക്കുക."
                ph4_t = "ഘട്ടം 4: വിളവെടുപ്പും വിപണനവും (ദിവസം 80 – 100)"
                ph4_d = "വിളവെടുപ്പിന് 15 ദിവസം മുൻപ് നന നിർത്തുക. ധാന്യം ഉണക്കി വിപണിയിൽ എത്തിക്കുക."
            else:
                st.markdown(f"#### 📅 4-Step Crop Lifecycle Timeline for **{best_crop_translated}**")
                st.caption("Follow this chronological timeline from plowing day to market sale day.")
                ph1_t = "Phase 1: Land Preparation & Sowing (Days 1 – 15)"
                ph1_d = "Plow the field 2–3 times to fine tilth. Apply organic manure (FYM) and basal fertilizers. Sow treated seeds at recommended row spacing. Give a light first irrigation."
                ph2_t = "Phase 2: Vegetative Growth & Weeding (Days 20 – 40)"
                ph2_d = "Perform first hand-weeding or hoeing around day 20. Apply the second dose of Urea. Irrigate every 8–10 days based on soil moisture. Inspect under leaves for early aphid signs."
                ph3_t = "Phase 3: Flowering & Grain Formation (Days 45 – 75)"
                ph3_d = "Ensure timely watering during flowering (most critical stage). Spray preventive neem oil if insects appear. Avoid harsh chemical sprays during active bee pollination."
                ph4_t = "Phase 4: Harvesting & Market Sale (Days 80 – 100)"
                ph4_d = "Stop watering 15 days before harvest. Harvest when 85% of pods/ears turn golden-brown on a sunny day. Thresh, winnow, and dry grains to 12% moisture before taking to APMC mandi."

            st.markdown(
                f"""
                <div style="display:flex; flex-direction:column; gap:14px; margin-top:12px;">
                    <div style="display:flex; gap:16px; background:#ffffff; border:1.5px solid #e2e8f0; border-left:6px solid #10b981; border-radius:12px; padding:16px;">
                        <div style="font-size:2rem; font-weight:900; color:#10b981; min-width:40px;">1</div>
                        <div>
                            <div style="font-weight:800; font-size:1.05rem; color:#0f172a;">{ph1_t}</div>
                            <div style="color:#475569; font-size:0.9rem; margin-top:4px;">{ph1_d}</div>
                        </div>
                    </div>
                    <div style="display:flex; gap:16px; background:#ffffff; border:1.5px solid #e2e8f0; border-left:6px solid #3b82f6; border-radius:12px; padding:16px;">
                        <div style="font-size:2rem; font-weight:900; color:#3b82f6; min-width:40px;">2</div>
                        <div>
                            <div style="font-weight:800; font-size:1.05rem; color:#0f172a;">{ph2_t}</div>
                            <div style="color:#475569; font-size:0.9rem; margin-top:4px;">{ph2_d}</div>
                        </div>
                    </div>
                    <div style="display:flex; gap:16px; background:#ffffff; border:1.5px solid #e2e8f0; border-left:6px solid #f59e0b; border-radius:12px; padding:16px;">
                        <div style="font-size:2rem; font-weight:900; color:#f59e0b; min-width:40px;">3</div>
                        <div>
                            <div style="font-weight:800; font-size:1.05rem; color:#0f172a;">{ph3_t}</div>
                            <div style="color:#475569; font-size:0.9rem; margin-top:4px;">{ph3_d}</div>
                        </div>
                    </div>
                    <div style="display:flex; gap:16px; background:#ffffff; border:1.5px solid #e2e8f0; border-left:6px solid #059669; border-radius:12px; padding:16px;">
                        <div style="font-size:2rem; font-weight:900; color:#059669; min-width:40px;">4</div>
                        <div>
                            <div style="font-weight:800; font-size:1.05rem; color:#0f172a;">{ph4_t}</div>
                            <div style="color:#475569; font-size:0.9rem; margin-top:4px;">{ph4_d}</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
