"""
Load and clean `all_show_info.json` --> save to `all_show_info_cleaned.json`
"""

# Import the usuals
import os
import re
import sys
import json
import pandas as pd
from IPython.display import display

from pathlib import Path
sys.path.append('..')

# Set pandas display options
pd.options.display.max_rows = 20
pd.options.display.max_columns = 150
pd.options.display.width = 1500



# Load the current data
curr_data_path = Path(os.path.join("data","all_show_info.json"))

if not os.path.isfile(curr_data_path):
    raise AssertionError(f"file doesn't exist for '{curr_data_path}'")
    sys.exit()

with open(curr_data_path,"r") as f:
    all_data = json.load(f)

# -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# Load to a dataframe
df = pd.DataFrame.from_records(all_data)

# Convert relevant datetime columns
date_col = ["Opening", "Closing", "Previews"]
for col in date_col:
    df[col] = pd.to_datetime(df[col], cache=True, errors="coerce")


# -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# Production type
production_type_dict = {"Return Engagement":"Revival", "American Premiere":"Premiere"}
df["Production Type"] = df["Production Type"].map(production_type_dict)

# Categorical columns:
cat_cols = ["Production Type", "Run Type", "Market", "Show type", "Version"]
for col in cat_cols:
    df[col] = df[col].astype("category")

# Numeric cols
num_cols = ["show_id","year"]
for col in num_cols:
    df[col] = df[col].astype(int)

# -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# Clean up Intermissions



# -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# Clean up Running Time



# -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# Clean up # Performances


# -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# Clean up Theatres


# ------------------------------------------------------------------------------
# Save here when finished
print(f"saving data for {len(df):,} records")

save_data_path = Path(os.path.join("data","all_show_info_cleaned.json"))
df.to_json(save_data_path, orient="records")
