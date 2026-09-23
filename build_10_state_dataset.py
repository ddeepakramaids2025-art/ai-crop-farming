import pandas as pd
import os

BASE = "dataset"

# =========================================================
# 10 STATES
# =========================================================

TARGET_STATES = [
    "Assam",
    "Bihar",
    "Gujarat",
    "Haryana",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Odisha",
    "Punjab",
    "Tamil Nadu"
]

# =========================================================
# LOAD EXISTING DATA
# =========================================================

production = pd.read_csv(
    os.path.join(BASE, "crop_production_data.csv")
)

price = pd.read_csv(
    os.path.join(BASE, "crop_price_data.csv")
)

soil = pd.read_csv(
    os.path.join(BASE, "soil_analysis_data.csv")
)

disease = pd.read_csv(
    os.path.join(BASE, "Indian_Crop_Disease_Dataset_English_1500.csv.xls")
)

# =========================================================
# SHOW CURRENT DATA
# =========================================================

print("=" * 60)
print("BUILDING 10-STATE DATASET")
print("=" * 60)

print("\nTarget states:")
for state in TARGET_STATES:
    print("-", state)

print("\nExisting production rows:", len(production))
print("Existing price rows:", len(price))
print("Existing soil rows:", len(soil))
print("Existing disease rows:", len(disease))

# =========================================================
# IMPORTANT:
# Your production/price/soil datasets currently contain
# Rajasthan districts only.
# Therefore we cannot honestly assign those Rajasthan
# records to other states.
# =========================================================

print("\nChecking state coverage...")

print("\nProduction columns:")
print(list(production.columns))

print("\nPrice columns:")
print(list(price.columns))

print("\nSoil columns:")
print(list(soil.columns))

print("\nDisease state coverage:")
print(
    disease["indian_state(major)"]
    .dropna()
    .astype(str)
    .str.strip()
    .value_counts()
    .head(20)
)

# =========================================================
# EXTRACT STATES FROM COST EXCEL
# =========================================================

excel_file = os.path.join(
    BASE,
    "Crop-year-wise-2020-21-2.xlsx"
)

excel = pd.ExcelFile(excel_file)

print("\nExcel sheets:", len(excel.sheet_names))

# =========================================================
# CREATE COST TABLE
# =========================================================

cost_rows = []

for sheet in excel.sheet_names:

    try:

        data = pd.read_excel(
            excel_file,
            sheet_name=sheet,
            header=None
        )

        if len(data) < 5:
            continue

        # Row 3 contains state names
        state_row = data.iloc[3]

        # Row containing C2 cost
        c2_rows = data[
            data.apply(
                lambda row:
                row.astype(str)
                .str.contains(
                    "C2",
                    case=False,
                    na=False
                ).any(),
                axis=1
            )
        ]

        if c2_rows.empty:
            continue

        c2_row = c2_rows.iloc[0]

        for col in range(4, len(data.columns)):

            state = state_row.iloc[col]

            if pd.isna(state):
                continue

            state = str(state).strip()

            if state not in TARGET_STATES:
                continue

            value = pd.to_numeric(
                c2_row.iloc[col],
                errors="coerce"
            )

            if pd.notna(value):

                cost_rows.append({
                    "State": state,
                    "Crop": sheet,
                    "Cost_of_Cultivation": float(value)
                })

    except Exception as e:

        print(
            "Skipping sheet:",
            sheet,
            "|",
            str(e)
        )

# =========================================================
# SAVE COST DATA
# =========================================================

cost_df = pd.DataFrame(cost_rows)

print("\nCost rows created:", len(cost_df))

if not cost_df.empty:

    print(
        "\nStates found in cost dataset:"
    )

    print(
        sorted(
            cost_df["State"]
            .unique()
            .tolist()
        )
    )

    print(
        "\nCrop count:",
        cost_df["Crop"].nunique()
    )

# =========================================================
# SAVE INTERMEDIATE COST DATA
# =========================================================

cost_output = os.path.join(
    BASE,
    "10_state_crop_costs.csv"
)

cost_df.to_csv(
    cost_output,
    index=False
)

print(
    "\nSaved:",
    cost_output
)

# =========================================================
# FINAL STATUS
# =========================================================

print("\n" + "=" * 60)
print("STEP 1 COMPLETE")
print("=" * 60)

print(
    "\nWe have extracted genuine state/crop cost data."
)

print(
    "\nNext we will connect this with:"
)

print("1. Production")
print("2. Market price")
print("3. Disease")
print("4. Soil")
print("5. Weather")

print(
    "\nDo NOT modify main.py yet."
)