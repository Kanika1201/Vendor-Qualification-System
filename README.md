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

## How It Works

1. Load software vendor data from CSV
2. Parse the feature column into a searchable format
3. Use **Sentence Transformers** (`all-MiniLM-L6-v2`) to embed features
4. Build a **FAISS index** to enable fast semantic search
5. At query time:
   - Filter vendors by category
   - Compute similarity between user query and vendor features
   - Combine similarity score (70%) with vendor rating (30%) for ranking

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
└── test_app.py             # Tests
```

---

## API Usage

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
    "product_name": "EspoCRM",
    "similarity": 0.34,
    "rating": 4.6,
    "final_score": 0.51
  },
  ...
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

## Solution Architecture

- `app.py`: FastAPI web application that exposes the `/vendor_qualification` endpoint.
- `utils.py`: Handles data loading and preprocessing from the CSV file.
- `model.py`: Builds and queries the FAISS index. Encodes both vendor features and user queries using Sentence Transformers.
- `Dockerfile`: Packages the entire app with its dependencies for portable deployment.
- `tests/`: Includes unit tests to validate API response behavior.

### 🔁 Data Flow:

1. On startup, the CSV is loaded, and vendor features are embedded using SBERT.
2. A **FAISS index** is built for fast semantic search.
3. When a POST request is received:
   - The system filters vendors by category
   - Embeds the user’s capabilities
   - Uses FAISS to find the most similar vendors
   - Applies a similarity threshold (≥ 0.6)
   - Ranks the remaining vendors based on final score = 0.7 * similarity + 0.3 * rating
4. Returns the **top 10 vendors** in ranked order via the API.

---

### 🔎 Why use a threshold of ≥ 0.6?

I chose a similarity threshold of ≥ 0.6 because, in semantic vector space (e.g., SBERT embeddings), values above 0.6 typically indicate strong contextual relevance.
Lower thresholds (e.g., 0.4–0.5) returned weaker or irrelevant matches, and higher ones (> 0.7) filtered out too many candidates.
0.6 struck a good balance during testing, ensuring vendors had at least one semantically relevant feature.

---

## Challenges Faced

Initially, I experimented with TF-IDF and cosine similarity for matching capabilities. But this approach produced low and misleading similarity scores, especially when different vendors described similar features with different words. Since TF-IDF relies on exact token overlap, semantically similar phrases like "Lead Tracking" and "Lead Management" scored poorly.

I resolved this by switching to Sentence Transformers (SBERT) for semantic embeddings and FAISS for scalable vector similarity search, which gave me more meaningful results.

Another limitation is that the dataset provided contains only vendors under the "CRM Software" category. This limited the diversity of the results and meant the system couldn't be fully tested across multiple software categories (e.g., ERP or Finance Software). My architecture, however, is fully extendable if more categories are added later.

---

## Potential Improvements
If I am given more time to work on this project, I will implement the following functionality:
- Add vector quantization (e.g., IVF, PQ) for large-scale vendor databases
- Extend scoring logic with more metadata (pricing, integrations)
- Add OpenAI or GPT-based reasoning to generate natural language recommendations (make it RAG!)
- Deploy to a cloud service (e.g., AWS EC2 + Docker)
- Add simple frontend UI for category/capability selection
