'''
model.py

Contains the logic for:
- Embedding vendor features and user queries using Sentence Transformers
- Building and querying a FAISS index
- Calculating final scores by combining similarity with vendor ratings

Used by app.py to retrieve the top matching vendors based on semantic similarity.

Author: Kanika Saxena
'''

from sentence_transformers import SentenceTransformer
import faiss
import pandas as pd
import numpy as np

class VendorMatcher:
    def __init__(self, vendors_df):
        self.df = vendors_df.reset_index(drop=True)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Encode and normalize vendor features
        self.embeddings = self.model.encode(self.df['parsed_features'].tolist(), show_progress_bar=True)
        self.embeddings = self.embeddings / np.linalg.norm(self.embeddings, axis=1, keepdims=True)

        # Build FAISS index
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(self.embeddings)

    def match(self, category, capabilities, top_k=10):
        # Filter vendors by category
        candidates = self.df[self.df['main_category'].str.lower() == category.lower()]
        candidate_indices = candidates.index.tolist()

        if not candidate_indices:
            print("⚠️ No vendors found for this category.")
            return pd.DataFrame()

        # Filter embeddings
        candidate_embeddings = self.embeddings[candidate_indices]
        faiss_index = faiss.IndexFlatIP(candidate_embeddings.shape[1])
        faiss_index.add(candidate_embeddings)

        # Embed and normalize query
        query_text = " ".join(capabilities)
        query_embedding = self.model.encode([query_text])
        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        # Search using FAISS
        D, I = faiss_index.search(query_embedding, top_k)
        matched_indices = [candidate_indices[idx] for idx in I.flatten()]
        matched_vendors = self.df.iloc[matched_indices].copy()
        matched_vendors['similarity'] = D.flatten()

        # Identify matched features
        matched_vendors['matched_features'] = matched_vendors['parsed_features'].apply(
            lambda x: self.extract_matched_features(x, capabilities)
        )

        # Only include vendors with at least one feature match
        matched_vendors = matched_vendors[matched_vendors['matched_features'].apply(lambda x: len(x) > 0)]

        if matched_vendors.empty:
            print("⚠️ No vendors matched the given capabilities.")
            return pd.DataFrame()

        # Calculate and round final score (as float with 2 decimal places)
        matched_vendors['final_score'] = matched_vendors.apply(
            lambda row: float(f"{self.compute_final_score(row['similarity'], row['rating']):.2f}"),
            axis=1
        )

        return matched_vendors.sort_values(by='final_score', ascending=False)

    def extract_matched_features(self, vendor_text, query_features):
        return [q for q in query_features if q.lower() in vendor_text.lower()]

    def compute_final_score(self, similarity, rating):
        normalized_rating = rating / 5.0 if pd.notna(rating) else 0.0
        score = (0.7 * similarity + 0.3 * normalized_rating) * 10
        return score
