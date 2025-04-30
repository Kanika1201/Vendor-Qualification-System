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
        self.df = vendors_df

        self.model = SentenceTransformer('all-MiniLM-L6-v2')  
        self.df = self.df.reset_index(drop=True)

        # Encode vendor features
        self.embeddings = self.model.encode(self.df['parsed_features'].tolist(), show_progress_bar=True)

        # Normalize embeddings for cosine similarity
        self.embeddings = self.embeddings / np.linalg.norm(self.embeddings, axis=1, keepdims=True)

        # Build FAISS index using cosine similarity 
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

        # Build FAISS index only for the filtered category
        candidate_embeddings = self.embeddings[candidate_indices]
        faiss_index = faiss.IndexFlatIP(candidate_embeddings.shape[1])
        faiss_index.add(candidate_embeddings)

        # Encode and normalize the query
        query_text = " ".join(capabilities)
        query_embedding = self.model.encode([query_text])
        query_embedding = query_embedding / np.linalg.norm(query_embedding)  

        # Search for top matches
        D, I = faiss_index.search(query_embedding, top_k)

        matched_indices = [candidate_indices[idx] for idx in I.flatten()]
        matched_vendors = self.df.iloc[matched_indices].copy()
        matched_vendors['similarity'] = D.flatten()

        # Compute final score combining similarity and rating
        matched_vendors['final_score'] = matched_vendors.apply(
            lambda row: self.compute_final_score(row['similarity'], row['rating']),
            axis=1
        )

        return matched_vendors.sort_values(by='final_score', ascending=False)

    def compute_final_score(self, similarity, rating):
        normalized_rating = rating / 5.0 if pd.notna(rating) else 0.0
        return 0.7 * similarity + 0.3 * normalized_rating
