'''
app.py

This is the main FastAPI application that exposes the `/vendor_qualification` endpoint.
It receives user input, interacts with the FAISS-based model to retrieve and rank vendors, and returns the top 10 results via a REST API.

Run the app with:
    uvicorn app:app --reload

Author: Kanika Saxena
'''

from fastapi import FastAPI
from pydantic import BaseModel
from utils import load_data
from model import VendorMatcher
import uvicorn

app = FastAPI()

# Load data and model at startup
vendors_df = load_data('vendors.csv')
matcher = VendorMatcher(vendors_df)

class Query(BaseModel):
    software_category: str
    capabilities: list

@app.post("/vendor_qualification")
def vendor_qualification(query: Query):
    results = matcher.match(query.software_category, query.capabilities)
    if results.empty:
        return {"message": "No vendors found matching the criteria."}
    return results[['product_name', 'main_category', 'rating', 'final_score', 'matched_features']].head(10).to_dict(orient='records')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
