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
├── vendors.csv             # Sample vendor data
├── README.md               # Project documentation
└── tests/
    └── test_app.py         # Basic unit test
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

## Challenges Faced

Initially, I experimented with TF-IDF and cosine similarity for matching capabilities. But this approach produced low and misleading similarity scores, especially when different vendors described similar features with different words. Since TF-IDF relies on exact token overlap, semantically similar phrases like "Lead Tracking" and "Lead Management" scored poorly.

I resolved this by switching to Sentence Transformers (SBERT) for semantic embeddings and FAISS for scalable vector similarity search, which gave me more meaningful results.

Another limitation is that the dataset provided contains only vendors under the "CRM Software" category. This limited the diversity of the results and meant the system couldn't be fully tested across multiple software categories (e.g., ERP or Finance Software). My architecture, however, is fully extendable if more categories are added later.

---

## Potential Improvements

- Add vector quantization (e.g., IVF, PQ) for large-scale vendor databases
- Extend scoring logic with more metadata (pricing, integrations)
- Add OpenAI or GPT-based reasoning to generate natural language recommendations (make it RAG!)
- Deploy to a cloud service (e.g., AWS EC2 + Docker)
- Add simple frontend UI for category/capability selection
