# Vendor Qualification System

This project implements a **Vendor Qualification System** that intelligently evaluates software vendors based on semantic feature similarity and user ratings. It uses **FastAPI**, **Sentence Transformers**, and **FAISS** to return the top vendors for a given software category and set of capabilities.

---

## Features

- Intelligent capability matching using semantic embeddings and not just keywords
- Fast similarity search with FAISS
- Ranking based on combined similarity + vendor rating
- Dockerized for easy deployment
- Unit tested with Pytest
- REST API with interactive Swagger docs

---

## Solution Architecture

- `app.py`: FastAPI web application that exposes the `/vendor_qualification` endpoint.
- `utils.py`: Handles data loading and preprocessing from the CSV file.
- `model.py`: Builds and queries the FAISS index. Encodes both vendor features and user queries using Sentence Transformers.
- `Dockerfile`: Packages the entire app with its dependencies for portable deployment.
- `tests/`: Includes unit tests to validate API response behavior.

### Data Flow:

1. On startup, the CSV is loaded, and vendor features are embedded using SBERT.
2. A **FAISS index** is built for fast semantic search.
3. When a POST request is received:
   - The system filters vendors by category
   - Embeds the user’s capabilities
   - Uses FAISS to find the most similar vendors
   - Applies a similarity threshold (≥ 0.6)
   - Ranks the remaining vendors based on final score = (0.7 * similarity + 0.3 * rating )*10
   - The response also highlights the matched capabilities for each vendor. 
4. Returns the **top 10 vendors** in ranked order via the API.
*final_score* is a scaled score (out of 10) based on both semantic similarity and vendor rating.
*matched_features* shows which of the requested capabilities were found in the vendor's feature set

---

### Why use a threshold of ≥ 0.6?

I chose a similarity threshold of ≥ 0.6 because, in semantic vectors (e.g., SBERT embeddings), values above 0.6 typically indicate strong contextual relevance.
Lower thresholds (e.g., 0.4–0.5) returned weak and irrelevant matches, and higher ones (> 0.7) filtered out too many candidates.
0.6 struck a good balance during testing, ensuring vendors had at least one semantically relevant feature.

---

## Tech Stack

- Python 3.9
- FastAPI
- Sentence Transformers
- FAISS (Facebook AI Similarity Search)
- Pandas
- Docker
- Pytest

---

## Project Structure

```
vendor-qualification-system/
├── app.py                  # FastAPI application
├── model.py                # Semantic search + FAISS logic
├── utils.py                # CSV loading and preprocessing
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker config
├── vendors.csv             # Sample vendor data CSV - renamed to vendors.csv
├── README.md               # Project documentation
├── .gitignore              # Git ignore file for temp/cache/system files
└── test_app.py             # Tests
```

---

## API Usage

To run locally, we can use uvicorn:

Start the app:

```bash
uvicorn app:app --reload
```

Then open:  
`http://localhost:8000/docs`

### Example Request:

```json
POST /vendor_qualification
{
  "software_category": "CRM Software",
  "capabilities": ["Lead Management"]
}
```

### Example Response:

```json
[
  {
    "product_name": "Efficy CRM",
    "main_category": "CRM Software",
    "rating": 4.5,
    "final_score": 5.32,
    "matched_features": ["Lead Management", "Email Marketing"]
  }
]
```

---

## Running Tests

Install pytest if not already:

```bash
pip install pytest
```

Then run:

```bash
pytest
```

Tests verify that the API responds correctly to example inputs.

---

## Docker Usage

### 1. Build the Docker Image

```bash
docker build -t vendor-qualification-system .
```

### 2. Run the Container

```bash
docker run -d -p 8000:8000 vendor-qualification-system
```

Then, Visit: `http://localhost:8000/docs`

---

### 3. Export as Portable `.tar` Image

```bash
docker save -o vendor-qualification-system.tar vendor-qualification-system
```

Transfer this `.tar` file to another machine, then load and run:

```bash
docker load -i vendor-qualification-system.tar
docker run -d -p 8000:8000 vendor-qualification-system
```

Then visit: `http://localhost:8000/docs`
Works on any system with Docker installed.

---

## Challenges Faced

Initially, I experimented with TF-IDF and cosine similarity for matching capabilities. But this approach produced low and misleading similarity scores, especially when different vendors described similar features with different words. Since TF-IDF relies on exact token overlap, semantically similar phrases like "Lead Tracking" and "Lead Management" scored poorly.

I resolved this by switching to Sentence Transformers (SBERT) for semantic embeddings and FAISS for scalable vector similarity search, which gave me more meaningful results.

The Features column in the CSV was a nested JSON-like string that had to be parsed safely. Due to this, entries can cause evaluation errors due to malformed data or missing fields. I handled this using ast.literal_eval() with error catching and fallback logic to prevent crashes.

Another limitation is that the dataset provided contains only vendors under the "CRM Software" category. This limited the diversity of the results and meant the system couldn't be fully tested across multiple software categories (e.g., ERP or Finance Software). My architecture, however, is fully extendable if more categories are added later. 
The dataset also contained mostly highly rated vendors. This biased the ranking scores upward and reduced contrast. The model architecture, however, is prepared to scale and generalize if a larger and more varied dataset is used.

---

## Potential Improvements
If given more time, I will implement the following enhancements:

 - Scalable Search with Vector Quantization: I will incorporate advanced FAISS indexing strategies such as IVF (Inverted File Index) or PQ (Product Quantization) to efficiently handle large-scale vendor databases and enable faster similarity searches.

 - Enhanced Scoring with Additional Metadata: I will extend the ranking logic by including other important vendor attributes such as pricing models, integration capabilities, or support options to provide more relevant recommendations.

 - Natural Language Recommendations (RAG-style): I will integrate OpenAI/GPT-based language models to generate human-readable explanations for each recommendation. This would move the system closer to a Retrieval-Augmented Generation architecture.

 - Cloud Deployment (e.g., AWS EC2 + Docker): I will deploy the project using Docker on a cloud platform like AWS EC2, or Render for real-time API access and easier demonstration in production-like environments.

 - Frontend UI: I will create a web interface that allows users to select categories and capabilities via dropdowns or text input, and view results in an interactive format. This will significantly improve usability for non-technical users.
