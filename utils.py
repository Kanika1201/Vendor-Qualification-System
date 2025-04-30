'''
utils.py

Handles data loading and preprocessing tasks:
- Loads vendor dataset from CSV
- Extracts relevant columns (product_name, category, features, rating)
- Cleans and flattens feature data for embedding

Helps prepare data for the model to process effectively.

Author: Kanika Saxena
'''

import pandas as pd
import ast

def load_data(filepath): 
    df = pd.read_csv(filepath)
    df = df[['product_name', 'main_category', 'Features', 'rating']]
    df = df.dropna(subset=['Features'])
    df['parsed_features'] = df['Features'].apply(extract_features)
    return df

def extract_features(features_json):
    if pd.isna(features_json):
        return ""
    try:
        features_list = ast.literal_eval(features_json)
        extracted_features = []
        for item in features_list:
            if "features" in item:
                extracted_features.extend([f['description'] for f in item['features'] if 'description' in f])
        return " ".join(extracted_features)
    except Exception as e:
        print(f"Error parsing features: {e}")
        return ""
