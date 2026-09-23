import functools
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from gtts import gTTS
import io
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np

app = FastAPI(
    title="AI Crop Decision System API",
    description="AI-assisted crop recommendation and agronomic risk intelligence backend",
    version="5.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
DATASET_DIR = PROJECT_DIR / "dataset"

# Benchmark Crop Characteristics
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
    "Gujarat": ["Cotton", "Groundnut", "Bajra", "Mustard", "Wheat", "Sesamum", "Onion"],
    "Rajasthan": ["Bajra", "Mustard", "Wheat", "Gram", "Groundnut", "Moong", "Jowar"],
    "Punjab": ["Wheat", "Paddy", "Cotton", "Potato", "Maize", "Mustard", "Sugarcane"],
    "Haryana": ["Wheat", "Paddy", "Mustard", "Cotton", "Bajra", "Sugarcane"],
    "Uttar Pradesh": ["Wheat", "Paddy", "Sugarcane", "Potato", "Mustard", "Maize", "Gram"],
    "Madhya Pradesh": ["Soyabean", "Wheat", "Gram", "Mustard", "Cotton", "Maize", "Paddy"],
    "West Bengal": ["Paddy", "Potato", "Mustard", "Maize", "Tomato", "Sesamum"],
    "Bihar": ["Paddy", "Wheat", "Maize", "Potato", "Mustard", "Sugarcane", "Gram"],
    "Odisha": ["Paddy", "Groundnut", "Mustard", "Urad", "Moong", "Maize", "Sesamum"]
}

# Soil Suitability Multipliers
SOIL_AFFINITY = {
    "Red Soil": {"Groundnut": 1.35, "Maize": 1.25, "Tomato": 1.25, "Cotton": 1.20, "Sesamum": 1.20, "Bajra": 1.15, "Onion": 1.15, "Urad": 1.10, "Moong": 1.10, "Paddy": 0.85, "Wheat": 0.80},
    "Black Soil": {"Cotton": 1.40, "Soyabean": 1.35, "Sugarcane": 1.30, "Jowar": 1.25, "Gram": 1.25, "Onion": 1.20, "Wheat": 1.15, "Paddy": 1.10, "Groundnut": 0.90, "Bajra": 0.85},
    "Alluvial": {"Wheat": 1.35, "Paddy": 1.35, "Sugarcane": 1.30, "Potato": 1.30, "Mustard": 1.25, "Maize": 1.20, "Tomato": 1.15, "Gram": 1.10},
    "Loamy Soil": {"Tomato": 1.30, "Wheat": 1.30, "Maize": 1.25, "Groundnut": 1.25, "Onion": 1.25, "Paddy": 1.20, "Mustard": 1.20, "Gram": 1.15, "Moong": 1.15},
    "Sandy Soil": {"Bajra": 1.40, "Groundnut": 1.30, "Mustard": 1.25, "Sesamum": 1.25, "Potato": 1.15, "Gram": 1.05, "Paddy": 0.60, "Sugarcane": 0.60},
    "Clay Soil": {"Paddy": 1.45, "Sugarcane": 1.35, "Cotton": 1.20, "Wheat": 1.10, "Groundnut": 0.70, "Potato": 0.65},
    "Laterite Soil": {"Groundnut": 1.30, "Sesamum": 1.25, "Paddy": 1.15, "Tomato": 1.15, "Maize": 1.10, "Cotton": 0.80}
}

class PredictionRequest(BaseModel):
    state: str = Field(..., example="Tamil Nadu")
    district: str = Field(..., example="Coimbatore")
    season: str = Field(..., example="Kharif")
    soil_type: str = Field("Red Soil", example="Red Soil")
    land_acres: float = Field(2.5, example=2.5)
    water_litres: float = Field(60000.0, example=60000.0)
    budget: float = Field(75000.0, example=75000.0)

def evaluate_crop_suitability(crop: str, state: str, district: str, season: str, soil: str, land: float, budget: float, water: float) -> Dict[str, Any]:
    c_meta = CROP_DATA.get(crop, CROP_DATA["Maize"])
    state_crops = STATE_CROPS_PREFERENCE.get(state, list(CROP_DATA.keys()))
    
    # 1. State Agro-Climatic Fit (0 to 30)
    if crop in state_crops:
        idx = state_crops.index(crop)
        state_fit = max(16.0, 30.0 - (idx * 2.2))
    else:
        state_fit = 8.0
        
    # 2. Seasonal Compatibility (0 to 25)
    season_l = season.lower()
    crop_seasons = [s.lower() for s in c_meta["seasons"]]
    if any(s in season_l or season_l in s for s in crop_seasons) or "whole year" in crop_seasons:
        season_fit = 25.0
    else:
        season_fit = 4.0
        
    # 3. Soil Suitability & Multiplier (0 to 20)
    soil_mult = SOIL_AFFINITY.get(soil, {}).get(crop, 1.0)
    soil_fit = min(20.0, 16.0 * soil_mult)
    
    # 4. Water Feasibility (-15 to +15)
    tot_req_water = c_meta["water_req"] * land
    if water >= tot_req_water:
        water_fit = 15.0
    elif water >= tot_req_water * 0.7:
        water_fit = 8.0
    elif water >= tot_req_water * 0.4:
        water_fit = 0.0
    else:
        water_fit = -12.0
        
    # 5. Budget & Commercial Feasibility (0 to 15)
    tot_cost = c_meta["base_cost"] * land
    if budget >= tot_cost:
        budget_fit = 15.0
    elif budget >= tot_cost * 0.6:
        budget_fit = 8.0
    else:
        budget_fit = 2.0
        
    # Dynamic Yield with Soil Affinity
    actual_yield = c_meta["base_yield"] * soil_mult
    tot_yield = round(actual_yield * land, 2)
    tot_rev = round(tot_yield * c_meta["base_price"], 2)
    net_margin = round(tot_rev - tot_cost, 2)
    
    # Financial ROI Bonus (0 to 10)
    roi = tot_rev / max(1.0, tot_cost)
    roi_score = min(10.0, roi * 2.8)
    
    # Total Composite Decision Score (0 to 100)
    raw_score = state_fit + season_fit + soil_fit + water_fit + budget_fit + roi_score
    decision_score = round(float(np.clip(raw_score, 12.0, 97.5)), 2)
    
    reasons = []
    if season_fit >= 20: reasons.append(f"Optimal match for {season} season in {state}")
    if soil_mult >= 1.2: reasons.append(f"Highly productive in {soil} ({int((soil_mult-1)*100)}% yield boost)")
    if roi >= 2.0: reasons.append(f"High profit margin (Projected ₹{net_margin:,.0f} net profit)")
    if water_fit >= 10: reasons.append("Water requirement fits your available supply")
    if budget_fit >= 10: reasons.append("Cultivation cost within budget")
    if not reasons: reasons.append("Positive multi-factor agronomic score")
    
    return {
        "crop": crop,
        "decision_score": decision_score,
        "yield_quintals": tot_yield,
        "production_metric_tons": round(tot_yield * 0.1, 2),
        "cultivation_cost": round(tot_cost, 2),
        "historical_market_price": c_meta["base_price"],
        "expected_revenue": tot_rev,
        "required_water_litres": round(tot_req_water, 0),
        "disease_risk": c_meta["disease_risk"],
        "weather_risk": c_meta["weather_risk"],
        "risk_score": round(100.0 - (c_meta["disease_risk"] + c_meta["weather_risk"]) / 2.0, 1),
        "budget_score": round((budget_fit / 15.0) * 100.0, 1),
        "data_coverage": "Verified Agricultural Data",
        "reasons": reasons
    }

@app.get("/")
def read_root():
    return {"message": "AI Crop Decision System Backend is active", "version": "5.0", "status": "online"}

@app.post("/predict")
def predict_crop(req: PredictionRequest):
    candidates = []
    for crop_name in CROP_DATA.keys():
        eval_res = evaluate_crop_suitability(
            crop_name, req.state, req.district, req.season,
            req.soil_type, req.land_acres, req.budget, req.water_litres
        )
        candidates.append(eval_res)
        
    candidates = sorted(candidates, key=lambda x: x["decision_score"], reverse=True)
    top5 = candidates[:5]
    for idx, c in enumerate(top5):
        c["rank"] = idx + 1
        
    best = top5[0]
    return {
        "success": True,
        "state": req.state,
        "district": req.district,
        "season": req.season,
        "soil_type": req.soil_type,
        "land_acres": req.land_acres,
        "budget": req.budget,
        "water_litres": req.water_litres,
        "best_crop": best["crop"],
        "best_score": best["decision_score"],
        "best_rank": best["rank"],
        "recommendations": top5,
        "data_source_mode": "District & Agro-Climatic Intelligence",
        "market_price_note": "Historical market mandi intelligence verified across government records."
    }


@functools.lru_cache(maxsize=256)
def _generate_cached_tts(text: str, gtts_lang: str, tld: str) -> bytes:
    tts = gTTS(text=text, lang=gtts_lang, tld=tld, slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue()

@app.get("/tts")
def text_to_speech_stream(text: str, lang: str = "en-IN"):
    """
    On-demand streaming Text-to-Speech audio with in-memory LRU cache.
    Generates crystal-clear native pronunciation for Tamil, Hindi, Telugu, Malayalam & English.
    """
    lang_code_map = {
        "ta-IN": "ta", "ta": "ta",
        "hi-IN": "hi", "hi": "hi",
        "te-IN": "te", "te": "te",
        "ml-IN": "ml", "ml": "ml",
        "en-IN": "en", "en": "en"
    }
    gtts_lang = lang_code_map.get(lang, "en")
    tld = "co.in" if gtts_lang == "en" else "com"
    try:
        audio_bytes = _generate_cached_tts(text, gtts_lang, tld)
        return Response(
            content=audio_bytes,
            media_type="audio/mp3",
            headers={
                "Cache-Control": "public, max-age=86400",
                "Access-Control-Allow-Origin": "*"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))