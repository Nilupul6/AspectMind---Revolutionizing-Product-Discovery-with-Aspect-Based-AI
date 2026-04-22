# AspectMind — Full Technical Report
### Revolutionizing Product Discovery with Aspect-Based AI
**Report Date:** March 19, 2026  
**Version:** 1.0.0  
**Status:** Production Ready  

---

## TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [Project Purpose & Problem Statement](#2-project-purpose--problem-statement)
3. [System Architecture Overview](#3-system-architecture-overview)
4. [Complete Directory & File Structure](#4-complete-directory--file-structure)
5. [Technology Stack — Full Breakdown](#5-technology-stack--full-breakdown)
6. [Backend — server/](#6-backend--server)
   - 6.1 [main.py — API Gateway](#61-mainpy--api-gateway)
   - 6.2 [recommender.py — Core AI Engine](#62-recommenderpy--core-ai-engine)
   - 6.3 [setup_offline.py — Model Bootstrapper](#63-setup_offlinepy--model-bootstrapper)
   - 6.4 [requirements.txt — Python Dependencies](#64-requirementstxt--python-dependencies)
7. [AI Models — What, Why, When & How](#7-ai-models--what-why-when--how)
8. [Data Pipeline — How Data Flows](#8-data-pipeline--how-data-flows)
9. [API Endpoints — Complete Reference](#9-api-endpoints--complete-reference)
10. [Frontend — client/](#10-frontend--client)
    - 10.1 [Entry Point: index.html & main.jsx](#101-entry-point-indexhtml--mainjsx)
    - 10.2 [App.jsx — Root Orchestrator](#102-appjsx--root-orchestrator)
    - 10.3 [ProductCard.jsx](#103-productcardjsx)
    - 10.4 [Dashboard.jsx](#104-dashboardjsx)
    - 10.5 [FilterPanel.jsx](#105-filterpaneljsx)
    - 10.6 [ProductModal.jsx](#106-productmodaljsx)
    - 10.7 [Comparison.jsx](#107-comparisonjsx)
    - 10.8 [Styling System (CSS Files)](#108-styling-system-css-files)
11. [Scripts — Data Maintenance Suite](#11-scripts--data-maintenance-suite)
12. [Embeddings & Index Files](#12-embeddings--index-files)
13. [Dataset Details](#13-dataset-details)
14. [Startup & Deployment](#14-startup--deployment)
15. [Caching Strategy](#15-caching-strategy)
16. [Recommendation Algorithm — Step-by-Step](#16-recommendation-algorithm--step-by-step)
17. [Aspect-Based Sentiment Analysis (ABSA) — Deep Dive](#17-aspect-based-sentiment-analysis-absa--deep-dive)
18. [Performance Optimizations](#18-performance-optimizations)
19. [Error Handling & Fallbacks](#19-error-handling--fallbacks)
20. [Known Limitations & Future Work](#20-known-limitations--future-work)
21. [Backend Source Code — Annotated Deep Dive](#21-backend-source-code--annotated-deep-dive)

---

## 1. Executive Summary

**AspectMind** is an end-to-end intelligent product recommendation and discovery system built from scratch. It combines three categories of Artificial Intelligence — **Semantic Search**, **Cross-Encoder Re-ranking**, and **Aspect-Based Sentiment Analysis (ABSA)** — into a single cohesive pipeline that answers the question: *"Which products truly match what the user cares about?"*

Unlike traditional keyword search or simple rating-based filtering, AspectMind understands _what_ the user wants and matches it against _what_ previous buyers specifically praised or criticized in product reviews. For example, a query like `"tasty milk but cool design"` is not just searched as keywords — the system extracts the aspects ("taste", "design"), determines the user's sentiment towards each, and filters results to show only products where reviews confirm those specific aspects were positive.

The system processes a dataset of **134,520+ Amazon products**, stores pre-computed vector embeddings, and serves results via a **FastAPI** REST API consumed by a **React 19** SPA frontend — all capable of running completely **offline** after initial model downloads.

---

## 2. Project Purpose & Problem Statement

### The Problem
Traditional e-commerce search:
- Returns products based on keyword overlap alone
- Shows star ratings but not **why** a product is rated the way it is
- Cannot distinguish between a product praised for "battery life" vs "camera quality"
- Forces users to read hundreds of reviews manually

### The Solution — AspectMind
AspectMind answers targeted questions automatically:
- **What** specific aspects (features) of a product do reviewers praise or criticize?
- **How confident** is the model in that assessment?
- **Which products** best match the aspects the *user* cares about in their query?

### Who It's Built For
- Consumers who want evidence-based product discovery
- Researchers studying NLP-powered recommendation systems
- Developers learning full-stack AI systems

---

## 3. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      USER BROWSER                           │
│           React 19 SPA  (http://localhost:5173)             │
│  App.jsx → ProductCard / Dashboard / FilterPanel / Modal    │
└───────────────────────┬─────────────────────────────────────┘
                        │  HTTP (axios)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI SERVER                              │
│             (http://localhost:8000)                         │
│   Endpoints: /search  /feedback  /analyze  /analytics       │
│              /compare                                       │
└───────────────────────┬─────────────────────────────────────┘
                        │  Python calls
                        ▼
┌─────────────────────────────────────────────────────────────┐
│             ProductRecommender (recommender.py)             │
│                                                             │
│  ┌──────────┐  ┌───────────┐  ┌────────────────────────┐  │
│  │  spaCy   │  │  SBERT    │  │  DeBERTa-v3 ABSA       │  │
│  │NLP/POS   │  │Embeddings │  │  Sentiment Analysis    │  │
│  └──────────┘  └───────────┘  └────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FAISS Index (130K+ vectors, cosine similarity)      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ms-marco Cross-Encoder Re-ranker                    │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
    ┌──────────────┐    ┌──────────────────┐
    │  data/       │    │  embeddings/     │
    │  CSV + .pkl  │    │  .npy .bin .pkl  │
    └──────────────┘    └──────────────────┘
```

**Communication Protocol:** The frontend communicates exclusively via HTTP GET/POST requests to the FastAPI backend using `axios`. No WebSockets, no GraphQL — pure REST.

**Deployment:** Both services run locally on Windows, launched via `start_app.bat`.

---

## 4. Complete Directory & File Structure

```
AspectMind/
│
├── start_app.bat                    # Windows dual-boot launcher
├── README.md                        # Quick-start guide
├── fixed_image_urls.csv             # Root source image URL dataset (~318 MB)
├── product_search_result.txt        # Debug search result sample
│
├── server/                          # Python FastAPI backend
│   ├── main.py                      # API gateway, route definitions
│   ├── recommender.py               # Core AI class (851 lines)
│   ├── setup_offline.py             # Model download/cache setup
│   ├── requirements.txt             # Python dependencies
│   └── __pycache__/                 # Python bytecode cache
│
├── client/                          # React 19 frontend
│   ├── index.html                   # HTML shell
│   ├── vite.config.js               # Vite bundler config
│   ├── package.json                 # Node.js dependencies
│   ├── package-lock.json            # Locked dependency tree
│   ├── eslint.config.js             # ESLint rules
│   ├── .gitignore                   # Git ignore rules
│   ├── README.md                    # Client-specific notes
│   ├── public/                      # Static public assets
│   └── src/
│       ├── main.jsx                 # React DOM mount point
│       ├── App.jsx                  # Root component (217 lines)
│       ├── App.css                  # Root layout styles (189 lines)
│       ├── index.css                # Global design system / variables
│       ├── assets/                  # Static image assets
│       └── components/
│           ├── ProductCard.jsx      # Product card UI (214 lines)
│           ├── ProductCard.css      # Card styles (7 KB)
│           ├── Dashboard.jsx        # Analytics modal (216 lines)
│           ├── Dashboard.css        # Dashboard styles (4.5 KB)
│           ├── FilterPanel.jsx      # Search filters (131 lines)
│           ├── FilterPanel.css      # Filter styles (6.6 KB)
│           ├── ProductModal.jsx     # Detail modal (116 lines)
│           ├── ProductModal.css     # Modal styles (5.6 KB)
│           ├── Comparison.jsx       # Side-by-side compare (216 lines)
│           └── Comparison.css       # Comparison styles (8 KB)
│
├── data/                            # Dataset storage
│   ├── Second_fixed_image_urls.csv           # Main dataset (~403 MB, 134K+ rows)
│   ├── Second_fixed_image_urls.csv_processed.pkl  # Pandas cache (~343 MB)
│   ├── Second_fixed_image_urls_backup_ames.csv    # Ames product backup
│   ├── Second_fixed_image_urls_backup_bulk.csv    # Bulk repair backup
│   └── Second_fixed_image_urls_backup_svg.csv     # SVG URL repair backup
│
├── embeddings/                      # Pre-computed AI indices
│   ├── enriched_item_descriptions_embeddings.npy  # All 384-dim vectors (~147 MB)
│   ├── faiss_index.bin              # FAISS flat inner product index (~147 MB)
│   ├── hnsw_index.bin               # HNSW approximate index (~162 MB)
│   └── knn_model.pkl                # Scikit-learn KNN fallback (~147 MB)
│
├── models/                          # Offline HuggingFace model cache
│   ├── all-MiniLM-L6-v2/            # SBERT semantic embedding model
│   ├── deberta-v3-base-absa/        # ABSA sentiment model
│   └── ms-marco-MiniLM-L-6-v2/     # Cross-encoder re-ranking model
│
├── scripts/                         # Data maintenance utilities
│   ├── quick_check.py               # Fast image URL health check (34 lines)
│   ├── diagnose_images.py           # Full URL diagnostic report (126 lines)
│   ├── repair_images_fixed.py       # URL cleaning & repair (191 lines)
│   ├── fix_ames_product.py          # AMES-specific product fixer (3 KB)
│   ├── fix_all_missing_images.py    # Bulk image restoration (2.2 KB)
│   ├── fix_placeholder_urls.py      # Placeholder URL converter (3 KB)
│   ├── find_product.py              # Product search utility (1.9 KB)
│   ├── test_data_loading.py         # Server compatibility tester (2.7 KB)
│   └── verify_ames_fix.py           # AMES repair verifier (1.1 KB)
│
└── docs/                            # Documentation
    ├── TECHNICAL_DOCUMENTATION.md   # Previous technical doc
    └── FULL_TECHNICAL_REPORT.md     # This document
```

---

## 5. Technology Stack — Full Breakdown

### 5.1 Backend (Python)

| Library | Version | Purpose | When Used |
|---|---|---|---|
| `fastapi` | Latest | REST API framework | Every HTTP request |
| `uvicorn` | Latest | ASGI server | Serving FastAPI |
| `pydantic` | (via fastapi) | Request/response validation | All POST body parsing |
| `torch` (PyTorch) | Latest | Deep learning tensors | ABSA, SBERT inference |
| `transformers` | Latest | HuggingFace model loader | Loading DeBERTa ABSA |
| `sentence-transformers` | Latest | SBERT + CrossEncoder | Semantic search + re-ranking |
| `spacy` | Latest | NLP / POS tagging | Aspect noun extraction |
| `faiss-cpu` | Latest | Vector similarity search | ANN lookup over 130K embeddings |
| `pandas` | Latest | DataFrame manipulation | CSV loading, data prep |
| `numpy` | Latest | Numerical arrays | Embeddings, reshaping |
| `scikit-learn` | Latest | KNN fallback | Alternative to FAISS |
| `joblib` | Latest | PKL serialization | Cache read/write |
| `scipy` | Latest | Mathematical ops | Sigmoid normalization |
| `tqdm` | Latest | Progress bars | Batch ABSA iteration |
| `accelerate` | Latest | Model acceleration | HuggingFace model loading |
| `sentencepiece` | Latest | Tokenizer backend | DeBERTa tokenization |
| `protobuf` | Latest | Model serialization | Transformer checkpoint loading |
| `tf-keras` | Latest | TensorFlow backend compatibility | Some transformer ops |
| `python-multipart` | Latest | Form data parsing | FastAPI form support |
| `threading` | stdlib | Background threads | Non-blocking feedback saves |
| `hashlib` | stdlib | MD5 hashing | Query cache keys |
| `functools.lru_cache` | stdlib | LRU caching | Repeated function calls |
| `gc` | stdlib | Garbage collection | GPU/CPU memory cleanup |

### 5.2 Frontend (JavaScript/React)

| Library | Version | Purpose | When Used |
|---|---|---|---|
| `react` | ^19.2.0 | UI rendering engine | All component rendering |
| `react-dom` | ^19.2.0 | DOM mounting | Root app mount |
| `axios` | ^1.13.5 | HTTP client | All API calls to backend |
| `framer-motion` | ^12.34.0 | Animation engine | Card entrances, modal transitions |
| `react-tilt` | ^1.0.2 | 3D hover tilt effect | ProductCard tilt interaction |
| `recharts` | ^3.7.0 | Chart library | Pie charts, bar charts in Dashboard |
| `lucide-react` | ^0.563.0 | SVG icon pack | UI icons throughout |
| `react-is` | ^19.2.4 | React type checking | Internal React utility |
| `vite` (rolldown) | 7.2.5 | Build tool / dev server | HMR, bundling |
| `@vitejs/plugin-react` | ^5.1.1 | Vite React plugin | JSX transforms |
| `eslint` | ^9.39.1 | Code linting | Development quality |

### 5.3 AI Models

| Model | Size | Task | Hosted At |
|---|---|---|---|
| `all-MiniLM-L6-v2` | ~80 MB | Sentence embeddings (384-dim) | `models/all-MiniLM-L6-v2/` |
| `yangheng/deberta-v3-base-absa-v1.1` | ~700 MB | Aspect sentiment classification | `models/deberta-v3-base-absa/` |
| `cross-encoder/ms-marco-MiniLM-L-6-v2` | ~80 MB | Query-document relevance scoring | `models/ms-marco-MiniLM-L-6-v2/` |
| `en_core_web_sm` (spaCy) | ~12 MB | NLP POS tagging | spaCy install location |

---

## 6. Backend — server/

### 6.1 `main.py` — API Gateway

**File size:** 133 lines, 3,949 bytes  
**Purpose:** Defines the FastAPI application, registers HTTP routes, handles CORS, and manages the global `ProductRecommender` singleton.

#### Key Design Decisions

**Offline Mode Enforcement (Lines 10–11):**
```python
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'
```
These two environment variables are set **before** any imports from HuggingFace. This forces the `transformers` library to never attempt network calls and always load from local disk. This is critical because the models are stored in `models/` and the system must work without internet.

**CORS Middleware (Lines 20–26):**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
Allows the React frontend running on `localhost:5173` to call the API on `localhost:8000` without cross-origin errors. The wildcard `*` is used since this is a local development system.

**Startup Event (Lines 32–41):**
```python
@app.on_event("startup")
def startup_event():
    global recommender, startup_error
    recommender = ProductRecommender()
```
The `ProductRecommender` is instantiated **once** at server startup. This is crucial because initialization loads ~1 GB of models and data into RAM — it cannot happen per-request. If initialization fails, the error is captured in `startup_error` and returned on every subsequent API call.

**Pydantic Request Models (Lines 75–83):**
```python
class FeedbackRequest(BaseModel):
    product_id: str
    feedback: str

class AnalysisRequest(BaseModel):
    text: str

class CompareRequest(BaseModel):
    product_ids: list[str]
```
These Pydantic models automatically validate incoming JSON POST bodies. If a required field is missing or wrong type, FastAPI returns a `422 Unprocessable Entity` error automatically — no manual validation needed.

#### API Routes Summary

| Method | Route | Handler | Description |
|---|---|---|---|
| GET | `/` | `read_root()` | Health check |
| GET | `/search` | `search()` | Main product search |
| POST | `/feedback` | `submit_feedback()` | Submit user feedback |
| POST | `/analyze` | `analyze_text()` | Real-time ABSA analysis |
| GET | `/analytics` | `get_analytics()` | Dashboard statistics |
| POST | `/compare` | `compare_products()` | Side-by-side comparison |

---

### 6.2 `recommender.py` — Core AI Engine

**File size:** 851 lines, 37,267 bytes  
**Purpose:** The single most important file in the project. Contains the `ProductRecommender` class that orchestrates all AI models and implements the recommendation pipeline.

#### Class Constructor `__init__` (Lines 26–69)

```python
def __init__(
    self,
    dataframe_name="Second_fixed_image_urls.csv",
    max_dataset_size=200000,
    absa_chunk_size=400,
    absa_batch_size=16,
    top_n=10
):
```

**Parameters explained:**
- `dataframe_name` — The CSV file to load from `data/`
- `max_dataset_size` — Cap on how many rows to process (200,000 max). Prevents OOM on large CSVs
- `absa_chunk_size` — How many reviews to process per ABSA batch loop (400 at a time)
- `absa_batch_size` — How many ABSA inference pairs to send to the model GPU/CPU simultaneously (16)
- `top_n` — Default number of recommendations to return

**Initialization sequence:**
1. `torch.set_grad_enabled(False)` — Disables gradient tracking globally. Since we only do inference (not training), this saves memory and speeds up every tensor operation.
2. Device detection: `"cuda"` if GPU available, else `"cpu"`
3. Path construction for all data/embedding/model directories
4. Load CSV into `df_original`
5. `_load_models()` — Load all three AI models
6. `_prepare_data()` — Process CSV with ABSA or load from cache
7. `_prepare_embeddings_and_index()` — Load/build FAISS index
8. Initialize in-memory query cache (dict with TTL)

#### `_load_models()` (Lines 87–161)

This method loads all three AI models in sequence. Each model has a **local path check** before attempting any download.

**spaCy Loading:**
```python
self.nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
```
The `ner` (named entity recognition) and `lemmatizer` components are disabled because only POS tagging and noun chunk extraction are needed. Disabling unused components makes spaCy ~2x faster.

**SBERT Loading:**
```python
sbert_path = os.path.join(MODEL_DIR, "all-MiniLM-L6-v2")
self.sbert = SentenceTransformer(sbert_path, device=self.device)
```
Loads the sentence embedding model from local disk. The `device` parameter places the model on GPU if available.

**Cross-Encoder Loading + Quantization:**
```python
self.cross_encoder = CrossEncoder(ce_path, device=self.device)
# CPU quantization for 2x speedup:
self.cross_encoder.model = torch.quantization.quantize_dynamic(
    self.cross_encoder.model, {torch.nn.Linear}, dtype=torch.qint8
)
```
When running on CPU, the cross-encoder is quantized using **dynamic INT8 quantization**. This converts all `Linear` layers from 32-bit float to 8-bit integer weights, providing approximately **2x speedup** with minimal accuracy loss.

**ABSA Model Loading:**
```python
tokenizer = AutoTokenizer.from_pretrained(self.absa_model_path, use_fast=False)
model = AutoModelForSequenceClassification.from_pretrained(self.absa_model_path)
self.absa_pipe = pipeline("text-classification", model=model, tokenizer=tokenizer, truncation=True)
```
`use_fast=False` is **critical** — DeBERTa-v3 uses SentencePiece tokenization which has a known incompatibility with the fast Rust tokenizer in `transformers`. Using `use_fast=True` causes a `convert_slow_tokenizer` error.

#### `_extract_aspects_batch()` (Lines 163–172)

```python
def _extract_aspects_batch(self, texts):
    for doc in self.nlp.pipe(texts, batch_size=128):
        for chunk in doc.noun_chunks:
            a = chunk.text.lower().strip()
            if len(a) > 2 and a not in {"it","this","that","product","item"}:
                aspects.append(a)
        aspects_list.append(list(set(aspects))[:3] or ["general"])
```

**How it works:**
1. `nlp.pipe()` processes text in batches of 128 (faster than one-by-one)
2. `doc.noun_chunks` extracts grammatical noun phrases (e.g., "battery life", "camera quality", "overall design")
3. Stopwords like "it", "this", "product" are excluded — they carry no aspect meaning
4. Each review is limited to **3 aspects max** for performance
5. Falls back to `["general"]` if no aspects found

#### `_extract_multi_aspects()` (Lines 199–238) — Batch ABSA

This is the most computationally expensive method. Called once at startup to pre-compute sentiment for all 134K+ product reviews.

```python
for i in tqdm(range(0, len(reviews), self.absa_chunk_size)):
    batch_reviews = reviews[i:i + self.absa_chunk_size]
    batch_aspects = self._extract_aspects_batch(batch_reviews)
    
    texts, meta = [], []
    for review, aspects in zip(batch_reviews, batch_aspects):
        for aspect in aspects:
            texts.append(f"[CLS] {review} [SEP] {aspect} [SEP]")
            meta.append((review, aspect))
    
    with torch.inference_mode():
        outputs = self.absa_pipe(texts, batch_size=self.absa_batch_size)
```

**The ABSA input format `"[CLS] review [SEP] aspect [SEP]"`** is the standard format for ABSA classification with DeBERTa. The model was fine-tuned to classify these pairs as Positive, Negative, or Neutral.

#### `_prepare_data()` (Lines 240–268)

Implements a **three-tier data strategy:**

1. **Cache hit** → Load `.pkl` file (sub-second)
2. **Cache miss** → Process CSV from scratch:
   - Filter rows where review text ≤ 15 characters (too short to be meaningful)
   - Cap at `max_dataset_size` rows
   - Fill null `description` and `feature` columns
   - Compute `item_unique_id` = concatenation of name + category + description + feature
   - Run ABSA on all reviews (may take many minutes first run)
3. **Save cache** → Write `.pkl` for next startup

#### `_prepare_embeddings_and_index()` (Lines 270–328)

**Enriched text construction:**
```python
self.df["enriched_text"] = (
    df["itemName"] + " " + df["category"] + " " +
    df["description"] + " " + df["feature"] + " " +
    df.apply(enrich, axis=1)  # adds aspect sentiment labels
)
```
The `enrich()` function appends aspect sentiment words (e.g., "battery Positive taste Negative") to the product text. This means the FAISS embeddings encode **both product metadata AND sentiment information**, making semantic search sentiment-aware.

**FAISS index construction:**
```python
d = embeddings.shape[1]  # 384 dimensions
self.index = faiss.IndexFlatIP(d)  # Inner Product = Cosine Sim on normalized vectors
self.index.add(embeddings)
faiss.write_index(self.index, self.index_path)
```
`IndexFlatIP` is a flat (brute-force) inner product index. When vectors are L2-normalized first (using `faiss.normalize_L2()`), inner product equals cosine similarity. This index is exact (no approximation) and supports 130K+ vectors efficiently.

#### `recommend()` (Lines 330–535)

The main recommendation function. Called on every `/search` request.

**Step 1 — Cache check:**
```python
cache_key = hashlib.md5(f"{user_query}_{category_filter}_{min_sentiment_score}_{sort_by}".encode()).hexdigest()
if cache_key in self.query_cache:
    result, timestamp = self.query_cache[cache_key]
    if time.time() - timestamp < self.cache_ttl:  # 1 hour TTL
        return result
```
Identical queries within 1 hour return instantly from memory.

**Step 2 — Query aspect inference:**
```python
query_aspects = self._infer_user_aspects(user_query)
```
Extracts aspects from the user's query and runs ABSA on them. So for "good battery life" → aspect="battery life", sentiment=Positive.

**Step 3 — FAISS vector search:**
```python
query_emb = self.sbert.encode(user_query, convert_to_numpy=True).reshape(1, -1)
faiss.normalize_L2(query_emb)
distances, indices = self.index.search(query_emb, cands_count)  # top 30 candidates
```

**Step 4 — Sentiment boost calculation:**
```python
for qa_name in query_aspect_names:
    if qa_name in aspects:
        if aspects[qa_name].get("sentiment") == "Positive":
            boost += 0.15   # reward aspect match
        elif aspects[qa_name].get("sentiment") == "Negative":
            boost -= 0.05   # penalize negative match
```
Products whose reviews confirm the user's desired aspects get a score boost.

**Step 5 — Cross-Encoder re-ranking (top 30 only):**
```python
ce_pairs = [[user_query, c["text_for_ce"]] for c in top_candidates_for_rerank]
ce_scores = self.cross_encoder.predict(ce_pairs)
```
The cross-encoder computes a relevance score for each (query, product) pair. This is more accurate than cosine similarity but slower, so it's only applied to the top 30 candidates.

**Step 6 — Sorting:**
- `relevance` → sort by combined FAISS + cross-encoder + boost score
- `sentiment` → sort by `sentiment_score` (positive ratio)
- `name` → alphabetical

**Step 7 — Response assembly:**
For each top-N result, builds the structured response including `top_pos_aspects`, `top_neg_aspects`, `matched_aspects`, and `reason`.

#### `add_feedback()` (Lines 538–639)

Handles user-submitted product feedback with a **non-blocking architecture**:

1. Run ABSA on feedback text (fast path, max 3 aspects, threshold 0.7)
2. Update `unique_df` and `df` in-memory **immediately** (microseconds)
3. Launch a **background daemon thread** to save to `.pkl` and `.csv` (seconds, doesn't block response)
4. Return to frontend with analysis results — user sees feedback results instantly

```python
save_thread = threading.Thread(target=save_all_background, daemon=True)
save_thread.start()
# Return IMMEDIATELY — no waiting for file I/O
return self._sanitize_for_json({...})
```

#### `get_analytics()` (Lines 707–767)

Iterates all unique products, aggregates:
- Total unique aspect count
- Sentiment distribution (Positive/Negative/Neutral count)
- Per-category product count and positive/negative aspect counts
- Top-15 most frequent aspects
- Top-10 categories by product count

#### `compare_products()` (Lines 769–849)

Accepts 2–4 product IDs. For each:
- Fetches the product row from `unique_df`
- Separates positive and negative aspects, sorted by confidence
- Builds an **aspect matrix**: a grid where rows = aspect names, columns = products, cells = sentiment + confidence

#### `_sanitize_for_json()` (Lines 650–665)

NumPy types (`np.int64`, `np.float32`, etc.) are **not JSON-serializable** by default. This recursive utility converts them to Python native types. Without it, every API response would crash with a serialization error.

---

### 6.3 `setup_offline.py` — Model Bootstrapper

**File size:** 85 lines, 3,632 bytes  
**Purpose:** A one-time setup script that downloads all three AI models from HuggingFace Hub and saves them to the local `models/` directory.

**Run once with internet, then offline forever.**

Functions:
- `setup_absa()` — Downloads `yangheng/deberta-v3-base-absa-v1.1`, saves tokenizer + model weights to `models/deberta-v3-base-absa/`
- `setup_sbert()` — Downloads `all-MiniLM-L6-v2`, saves to `models/all-MiniLM-L6-v2/`
- `setup_cross_encoder()` — Downloads `cross-encoder/ms-marco-MiniLM-L-6-v2`, saves to `models/ms-marco-MiniLM-L-6-v2/`
- `setup_spacy()` — Downloads `en_core_web_sm` via spaCy CLI

Each function checks if `config.json` exists in the target folder before downloading — avoiding redundant re-downloads.

---

### 6.4 `requirements.txt` — Python Dependencies

```
fastapi          # Web framework
uvicorn          # ASGI server
pandas           # DataFrames
numpy            # Numerical computing
torch            # Deep learning
transformers     # HuggingFace models
sentence-transformers  # SBERT + CrossEncoder
spacy            # NLP
scikit-learn     # KNN fallback
joblib           # PKL serialization
scipy            # Math utilities
tqdm             # Progress bars
python-multipart # FastAPI form parsing
accelerate       # HuggingFace model acceleration
sentencepiece    # DeBERTa tokenizer backend
protobuf         # Model checkpoint serialization
tf-keras         # TensorFlow/Keras compatibility
faiss-cpu        # Vector similarity search
```

---

## 7. AI Models — What, Why, When & How

### 7.1 `all-MiniLM-L6-v2` — Semantic Embedder

| Attribute | Value |
|---|---|
| **What** | Sentence-BERT model, produces 384-dimensional dense vectors |
| **Why** | Converts text to vectors where semantically similar texts are close in vector space |
| **When** | At startup: encodes all 130K product descriptions. At query time: encodes the user's search query |
| **How** | `self.sbert.encode(text)` → returns `np.ndarray` of shape `(384,)` |
| **Architecture** | 6-layer transformer, distilled from BERT |
| **Training** | Fine-tuned on MS MARCO + NLI datasets for sentence similarity |

### 7.2 `yangheng/deberta-v3-base-absa-v1.1` — ABSA Classifier

| Attribute | Value |
|---|---|
| **What** | DeBERTa-v3 fine-tuned specifically for Aspect-Based Sentiment Analysis |
| **Why** | Determines sentiment (Positive/Negative/Neutral) for a specific aspect within a review |
| **When** | At startup: runs on all product reviews. At feedback time: runs on user-submitted text. At query time: infers aspect sentiments from the user query |
| **How** | Input: `"[CLS] review text [SEP] aspect [SEP]"` → Output: `{label: "Positive", score: 0.94}` |
| **Architecture** | DeBERTa-v3-base with classification head |
| **Labels** | Positive, Negative, Neutral |

### 7.3 `cross-encoder/ms-marco-MiniLM-L-6-v2` — Re-ranker

| Attribute | Value |
|---|---|
| **What** | Cross-encoder that scores relevance between a query and a document jointly |
| **Why** | More accurate than cosine similarity — considers full interaction between query and product |
| **When** | After FAISS retrieves top 30 candidates, re-ranks them by true relevance |
| **How** | Input: `[query, product_text]` pair → Output: scalar relevance score |
| **Architecture** | 6-layer MiniLM, fine-tuned on MS MARCO passage ranking |

### 7.4 `en_core_web_sm` (spaCy) — NLP Engine

| Attribute | Value |
|---|---|
| **What** | Small English NLP model with POS tagger and noun chunk parser |
| **Why** | Extracts grammatical noun phrases (aspects) from text |
| **When** | Every time product reviews or user queries need aspect extraction |
| **How** | `nlp(text).noun_chunks` → list of noun phrases |
| **Disabled** | `ner` and `lemmatizer` (not needed, disabled for speed) |

---

## 8. Data Pipeline — How Data Flows

### 8.1 Cold Start (First Run)

```
CSV file (134K rows)
    ↓ pandas.read_csv()
Raw DataFrame
    ↓ Filter: reviewText > 15 chars
    ↓ Cap at 200K rows
    ↓ Fill nulls in description, feature
    ↓ Compute item_unique_id
Cleaned DataFrame
    ↓ _extract_multi_aspects() for ALL reviews
    ↓   └→ spaCy: extract noun chunks per review
    ↓   └→ DeBERTa ABSA: classify each (review, aspect) pair
    ↓   └→ Store as JSON string per row
DataFrame with aspects_sentiments column
    ↓ joblib.dump() → .pkl cache
Cached DataFrame
    ↓ Build enriched_text (name + category + desc + feature + aspect labels)
    ↓ Drop duplicates by item_unique_id
    ↓ SBERT.encode() all enriched texts → embeddings.npy
    ↓ faiss.normalize_L2() + faiss.IndexFlatIP.add()
    ↓ faiss.write_index() → faiss_index.bin
System Ready
```

### 8.2 Warm Start (Subsequent Runs)

```
.pkl cache exists? → pandas.read_pickle() → DataFrame (sub-second)
faiss_index.bin exists? → faiss.read_index() → FAISS Index (sub-second)
Models already in models/ → load from local disk (seconds, not minutes)
System Ready ~30-60 seconds (vs hours cold start)
```

### 8.3 Per-Request Flow (/search)

```
User Query: "good battery life camera quality"
    ↓
_infer_user_aspects() → [("battery life", "Positive", 0.92), ("camera quality", "Positive", 0.88)]
    ↓
SBERT.encode(query) → query_vector [384 dims]
    ↓
faiss.normalize_L2(query_vector)
    ↓
FAISS.search(query_vector, top_30) → 30 candidate products
    ↓
Apply category_filter, min_sentiment_score filters
    ↓
Apply aspect boost: +0.15 per positive match, -0.05 per negative match
    ↓
Cross-Encoder.predict([(query, product_text)] × 30) → 30 relevance scores
    ↓
sigmoid(ce_score) + boost → final_score
    ↓
Sort by final_score → top 10 results
    ↓
Enrich top 10: fallback ABSA if needed, build pos/neg aspect lists
    ↓
_sanitize_for_json() → JSON response → axios → React UI
```

---

## 9. API Endpoints — Complete Reference

### `GET /`
**Purpose:** Health check  
**Response:**
```json
{"status": "active", "message": "Product Recommender API is running"}
```

### `GET /search`
**Purpose:** Main search + recommendation  
**Query Parameters:**
| Param | Type | Default | Description |
|---|---|---|---|
| `q` | `str` | required | Natural language search query |
| `category` | `str` | `None` | Filter by product category |
| `min_sentiment` | `float` | `None` | Minimum sentiment score [-1.0, 1.0] |
| `sort_by` | `str` | `"relevance"` | "relevance", "sentiment", or "name" |

**Response Shape:**
```json
{
  "query_analysis": {
    "battery life": {"sentiment": "Positive", "polarity": "positive", "confidence": 0.92}
  },
  "overall_sentiment": {"label": "Positive", "confidence": 0.87},
  "results": [
    {
      "product": "Duracell AA Batteries",
      "matched_aspects": ["battery life"],
      "top_pos_aspects": [{"name": "battery life", "score": 0.96}],
      "top_neg_aspects": [],
      "reason": "Winner for: battery life",
      "all_aspects": {...}
    }
  ],
  "raw_recs": [
    {
      "id": "DuracellAA...",
      "name": "Duracell AA Batteries",
      "category": "Electronics",
      "image": "https://images-na.ssl-images-amazon.com/...",
      "score": 0.93,
      "sentiment_score": 0.8,
      "aspects": {...}
    }
  ],
  "available_categories": ["Electronics", "Kitchen", ...]
}
```

### `POST /feedback`
**Purpose:** Submit user review/feedback to update product ABSA data  
**Body:**
```json
{"product_id": "DuracellAABatteries...", "feedback": "The battery life is amazing but packaging is flimsy"}
```
**Response:**
```json
{
  "status": "success",
  "message": "Feedback analyzed and product updated.",
  "feedback_analysis": {
    "battery life": {"sentiment": "Positive", "confidence": 0.97},
    "packaging": {"sentiment": "Negative", "confidence": 0.91}
  }
}
```

### `POST /analyze`
**Purpose:** Real-time ABSA analysis (no saving) — used for live feedback preview  
**Body:** `{"text": "The taste is great but packaging is terrible"}`  
**Response:** `{"taste": {"sentiment": "Positive", "confidence": 0.94}, "packaging": {"sentiment": "Negative", "confidence": 0.89}}`

### `GET /analytics`
**Purpose:** Returns aggregate statistics for the Dashboard  
**Response includes:**
- `total_products` — unique product count
- `total_aspects` — unique aspect term count
- `sentiment_distribution` — `{Positive: N, Negative: N, Neutral: N}`
- `top_aspects` — top 15 by frequency with pos/neg/neutral counts
- `top_categories` — top 10 by product count
- `dataset_info` — total reviews and unique product counts

### `POST /compare`
**Purpose:** Side-by-side product comparison  
**Body:** `{"product_ids": ["id1", "id2", "id3"]}`  
**Response includes:**
- `products` — array of product details with `positive_aspects`, `negative_aspects`, counts
- `aspect_matrix` — grid of aspects × products with sentiment + confidence per cell
- `comparison_count` — number of products in comparison



---

## 10. Frontend — client/

The frontend is a React 19 Single Page Application (SPA) scaffolded with Vite. It runs at `http://localhost:5173` and communicates entirely with the FastAPI backend at `http://localhost:8000`.

### Global axios Configuration
In `App.jsx` line 13:
```js
axios.defaults.baseURL = 'http://localhost:8000';
```
This sets a global base URL so all axios calls use relative paths (`/search`, `/feedback`, etc.) without repeating the server URL.

---

### 10.1 Entry Point: `index.html` & `main.jsx`

**`index.html` (14 lines)**
The HTML shell. Contains a single `<div id="root">` and loads `/src/main.jsx` as an ES module. This is the entry point Vite bundles from.

**`main.jsx` (11 lines)**
```jsx
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>
)
```
Mounts the React app into the DOM using React 19's `createRoot` API. `StrictMode` enables extra development warnings and double-invokes functions to detect side effects.

---

### 10.2 `App.jsx` — Root Orchestrator (217 lines)

The top-level component that manages all global application state and coordinates which modals are shown.

**State Management (Lines 16–35):**

| State Variable | Type | Purpose |
|---|---|---|
| `query` | string | Current search input value |
| `results` | object/null | Full API response from `/search` |
| `loading` | boolean | Shows "Analyzing..." during API call |
| `error` | string/null | Error message display |
| `showDashboard` | boolean | Toggle analytics modal |
| `selectedProduct` | object/null | Product to show in detail modal |
| `selectedForComparison` | array | Product IDs selected for comparison |
| `showComparison` | boolean | Toggle comparison modal |
| `filterOpen` | boolean | Toggle filter panel visibility |
| `selectedCategory` | string/null | Active category filter |
| `minSentiment` | float/null | Active sentiment minimum filter |
| `sortBy` | string | Active sort mode |

All state lives in `App.jsx`. No external state manager (Redux/Zustand) — React's built-in `useState` is sufficient given the app scope.

**`handleSearch()` (Lines 37–64):**
- Validates query is not empty
- Records `performance.now()` timestamp
- Builds params object: `{q, category?, min_sentiment?, sort_by?}`
- Calls `axios.get('/search', {params})`
- On success: sets `results` state → React re-renders ProductCards
- On error: sets `error` state → error message displayed
- Uses `finally` block to always clear loading state

**Comparison logic (Lines 66–86):**
Limits selection to maximum 4 products (backend constraint). When 2+ products are selected, a glowing "Compare" button appears with a CSS pulse-glow animation.

**`AnimatePresence`** from Framer Motion wraps `ProductModal` — when the modal is dismissed, it plays its `exit` animation (fade + scale) before being removed from the DOM. Without `AnimatePresence`, the `exit` animation would be skipped.

---

### 10.3 `ProductCard.jsx` (214 lines)

The most complex frontend component. Renders a single product card with animations, tilt, images, aspect bars, and inline feedback.

**Framer Motion stagger animation (Lines 86–93):**
```jsx
<motion.div
    initial={{ opacity: 0, y: 30 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ duration: 0.5, delay: index * 0.1 }}
>
```
Each card fades in from below when entering the viewport. `delay: index * 0.1` creates a cascade effect — card 1 at 0ms, card 2 at 100ms, card 3 at 200ms, etc. `viewport: { once: true }` means the animation only plays once.

**React-Tilt wrapper (Line 94):**
```jsx
<Tilt options={{ max: 15, scale: 1.02, speed: 400, glare: true, "max-glare": 0.5 }}>
```
The card tilts up to 15 degrees following the cursor. Glare effect simulates a light reflection. Scale 1.02 gives hover growth.

**Image handling (Lines 39–58):**
- Inline base64 SVG placeholder — works offline, no external URL needed
- Validates URL: must start with `http`, not be `"nan"` or empty
- Skeleton loader shown while image loads (`imageLoading` state)
- `onError` → replaces broken images with SVG placeholder
- Score badge overlaid on image: `(rawRecs.score * 100).toFixed(0)% Match`

**Aspect visualization (Lines 140–168):**
Two columns — Top Strengths (green) and Concerns (red). Each aspect shows a confidence bar: `width: ${score * 100}%`.

**Real-time feedback debounce (Lines 17–37):**
```jsx
useEffect(() => {
    const timer = setTimeout(async () => {
        const res = await axios.post('/analyze', { text: feedback });
        setFeedbackResult(res.data);
    }, 800); // 800ms debounce
    return () => clearTimeout(timer);
}, [feedback]);
```
As the user types, a debounced call to `/analyze` shows live detected aspects as colored chips — before the user even submits. Debounce prevents excessive API calls.

---

### 10.4 `Dashboard.jsx` (216 lines)

Analytics overview modal. Fetches `/analytics` once on mount.

**Recharts components used:**
1. **PieChart** — Overall sentiment distribution (Positive=green #10b981, Negative=red #ef4444, Neutral=gray #6b7280)
2. **BarChart (stacked, vertical)** — Top 10 aspects by positive/negative count
3. **BarChart (horizontal layout)** — Top 10 categories by product count

**ResponsiveContainer**: All charts wrapped in `<ResponsiveContainer width="100%" height={300}>` for fluid layout.

**4 Stats Cards:**

| Stat | Color | Icon |
|---|---|---|
| Total Products | Purple gradient | Package |
| Unique Aspects | Pink-red gradient | Tag |
| Total Reviews | Blue-cyan gradient | TrendingUp |
| Categories | Green-teal gradient | BarChart3 |

**Aspect Breakdown Table (15 rows):**
Shows aspect name, total count, positive count, negative count, neutral count, and sentiment ratio `(pos-neg)/total*100%` — color-coded green/red.

---

### 10.5 `FilterPanel.jsx` (131 lines)

Slide-in filter panel displayed after search results load.

**3 controls:**
1. **Category dropdown** — Select from `results.available_categories` list returned by backend
2. **Sentiment slider** — Range input from -1.0 to +1.0, step 0.1. Value -1 = "No Filter" (null). Passes `min_sentiment` query param
3. **Sort buttons** — Three toggle buttons: Relevance / Sentiment / Name. Active button highlighted via `.active` CSS class

**Active filter indicator** — When any filter is non-default, a dot badge `●` appears on the toggle button and a "Clear All Filters" button appears inside the panel.

**Overlay close** — A semi-transparent overlay behind the panel captures outside clicks to close it.

---

### 10.6 `ProductModal.jsx` (116 lines)

Detailed product view with spring entrance/exit animation.

**Framer Motion spring (Lines 43–46):**
```jsx
initial={{ opacity: 0, scale: 0.9, y: 20 }}
animate={{ opacity: 1, scale: 1, y: 0 }}
exit={{ opacity: 0, scale: 0.9, y: 20 }}
transition={{ type: "spring", stiffness: 300, damping: 25 }}
```
Spring physics: opens with a slight bounce. Exit animation enabled by `AnimatePresence` parent.

**Body scroll lock** — `document.body.style.overflow = 'hidden'` on mount, restored on unmount.

**Four content sections:**
1. Header: image + category badge + product name + match score (Zap icon)
2. Description: rendered via `dangerouslySetInnerHTML` (descriptions may contain HTML)
3. Key Features: text split by `|` or `.` delimiters, shown as bullet list
4. Aspect Analysis Grid: all detected aspects as cards sorted by confidence, color-coded

---

### 10.7 `Comparison.jsx` (216 lines)

Side-by-side comparison for 2–4 selected products.

**Four sections:**

**1. Product Overview Cards** — Image, name, category, strength/concern/total aspect counts.

**2. Aspect Matrix Table** — Grid where rows=aspects, columns=products. Each cell shows:
- Icon: CheckCircle (Positive) / XCircle (Negative) / MinusCircle (Neutral) / `—` (N/A)
- Sentiment label + confidence percentage
- Background color: green/red/gray/dim

**3. Top Strengths Comparison** — Per product: top 5 positive aspects with confidence progress bars.

**4. Winner Summary** — Net score `= positive_count - negative_count`. Highest net score = `🏆 Best Overall` badge. Shows net score and positive ratio.

---

### 10.8 Styling System

**Global CSS variables (`index.css`):**
```css
:root {
  --accent-primary, --accent-secondary  /* gradient colors */
  --positive: #22c55e   /* green  */
  --negative: #ef4444   /* red    */
  --neutral:  #6b7280   /* gray   */
  --text-secondary      /* muted text */
}
```

**Glass morphism (`.glass-panel`):**
```css
background: rgba(255, 255, 255, 0.05);
backdrop-filter: blur(10px);
border: 1px solid rgba(255, 255, 255, 0.1);
border-radius: 16px;
```
Applied to: search box, product cards, modals, filter panel, stat cards, charts.

**Key CSS techniques:**
- `grid-template-columns: repeat(auto-fill, minmax(300px, 1fr))` — responsive product grid
- `@keyframes pulse-glow` — Compare button glowing animation
- `backdrop-filter: blur()` — glassmorphism
- `transform: scale() translateY()` — hover feedback on buttons
- `transition: all 0.2s/0.3s` — smooth state transitions

---

## 11. Scripts — Data Maintenance Suite

### `quick_check.py` (34 lines)
Fast validation of image URL quality. Counts: null images, corrupted URLs (multiple `https://`), missing protocol URLs. Takes ~5 seconds. Recommended before every server start.

### `diagnose_images.py` (126 lines)
Deep diagnostic. Categorizes every URL as: VALID, MISSING, EMPTY, CORRUPTED_MULTIPLE_PROTOCOL, INVALID_NO_PROTOCOL, INVALID_NO_EXTENSION, INVALID_SPECIAL_CHARS. Shows samples of each problem type and gives a RECOMMENDATION.

### `repair_images_fixed.py` (191 lines)
Active URL repair using three strategies:

1. **Regex extraction:** `re.search(r'(https?://[^\s\'"<>]+\.(jpg|jpeg|png|gif))', url)` — extracts valid URLs from corrupted strings
2. **Amazon path reconstruction:** `https://images-na.ssl-images-amazon.com/images/I/{filename}`
3. **Root CSV lookup:** Builds `itemName → image_url` dictionary from `fixed_image_urls.csv` and uses it to restore missing images

Always creates backup before modifying. This is why 3 backup CSVs exist (`_backup_ames`, `_backup_bulk`, `_backup_svg`).

### Other Scripts

| Script | Lines | Purpose |
|---|---|---|
| `fix_ames_product.py` | ~80 | Targeted fix for AMES brand URL corruption |
| `fix_all_missing_images.py` | ~60 | Bulk null image restoration |
| `fix_placeholder_urls.py` | ~80 | Replace stub placeholder URLs with CDN URLs |
| `find_product.py` | ~50 | Search CSV by product name for debugging |
| `test_data_loading.py` | ~70 | Validate CSV can be loaded by server |
| `verify_ames_fix.py` | ~30 | Confirm AMES fix was applied correctly |

---

## 12. Embeddings & Index Files

| File | Size | Format | Contents |
|---|---|---|---|
| `enriched_item_descriptions_embeddings.npy` | ~147 MB | NumPy binary | Shape `(N_unique, 384)` float32 embeddings |
| `faiss_index.bin` | ~147 MB | FAISS binary | IndexFlatIP, L2-normalized cosine similarity index |
| `hnsw_index.bin` | ~162 MB | HNSW binary | Approximate NN index (built as alternative) |
| `knn_model.pkl` | ~147 MB | joblib pickle | sklearn NearestNeighbors fallback |

**Embedding dimensions:** 384-dim float32 (output of `all-MiniLM-L6-v2`). L2-normalized for cosine similarity via inner product.

**To rebuild:** Delete `.npy` and `.bin` files and restart server. `_prepare_embeddings_and_index()` auto-rebuilds.

---

## 13. Dataset Details

**File:** `data/Second_fixed_image_urls.csv` | ~403 MB | 134,520+ rows | Source: Amazon product reviews

### CSV Columns

| Column | Type | Description |
|---|---|---|
| `itemName` | string | Full product name |
| `category` | string | Product category |
| `description` | string | Product description (may have HTML) |
| `feature` | string | Features (pipe-delimited or free text) |
| `reviewText` | string | Customer review |
| `image` | string | Amazon CDN image URL |
| `aspects_sentiments` | string (JSON) | Pre-computed ABSA results |

**Key preprocessing:**
- Rows with `reviewText` <= 15 chars dropped (too short)
- `item_unique_id` = `itemName + category + description + feature`
- `aspects_sentiments` stored as JSON string in CSV

**Stats:**
- Unique products: ~50,000–60,000 (post de-duplication)
- Valid image URLs: ~82% (~110,330)
- Categories: 50+ unique

---

## 14. Startup & Deployment

### `start_app.bat`
```batch
start "Backend Server"  cmd /k "cd server & pip install -r requirements.txt & python main.py"
start "Frontend Client" cmd /k "cd client & npm install & npm install axios & npm run dev"
```

Opens two terminal windows simultaneously. Backend on port 8000, frontend on port 5173.

### Manual Startup
```bash
# Terminal 1
cd server
pip install -r requirements.txt
python main.py

# Terminal 2
cd client
npm install
npm run dev
```

### Access URLs
| Service | URL |
|---|---|
| Frontend (React) | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

---

## 15. Caching Strategy

### Layer 1 — Processed DataFrame `.pkl`
- **File:** `data/Second_fixed_image_urls.csv_processed.pkl` (~343 MB)
- **Benefit:** Avoids re-running ABSA on 134K reviews (hours of computation)
- **Invalidate:** Delete `.pkl` file and restart server

### Layer 2 — FAISS Index `.bin`
- **File:** `embeddings/faiss_index.bin` (~147 MB)
- **Benefit:** Avoids re-encoding 130K texts with SBERT (10-30 min)
- **Invalidate:** Delete `.npy` and `.bin` files

### Layer 3 — In-Memory Query Cache
- **Storage:** Python dict in RAM
- **Key:** MD5 of `"{query}_{category}_{min_sentiment}_{sort_by}"`
- **TTL:** 1 hour (3600 seconds)
- **Max entries:** 100 (oldest 20 evicted when full)
- **Benefit:** Identical queries return instantly with zero model inference

---

## 16. Recommendation Algorithm — Step-by-Step

Example query: **"good battery life but flimsy packaging"**

| Step | Action | Detail |
|---|---|---|
| 1 | Cache check | MD5 computed, no hit |
| 2 | Aspect extraction | spaCy: ["battery life", "packaging"] |
| 3 | Query ABSA | battery life=Positive(0.91), packaging=Negative(0.88) |
| 4 | SBERT encode | 384-dim query vector |
| 5 | FAISS search | Top 30 by cosine similarity |
| 6 | Category filter | Exclude non-matching categories |
| 7 | Sentiment filter | Exclude if sentiment_score < min_sentiment |
| 8 | Aspect boost | +0.15 per positive match, -0.05 per negative |
| 9 | Cross-encoder | Re-rank top 30 with ms-marco |
| 10 | Sigmoid normalize | CE scores mapped to (0,1) |
| 11 | Final sort | By `sigmoid(ce) + boost`, descending |
| 12 | Top-10 select | First 10 results |
| 13 | Enrich results | Build pos/neg lists, matched_aspects, reason |
| 14 | Fallback ABSA | Run on-the-fly if product lacks pos AND neg aspects |
| 15 | JSON sanitize | NumPy types → Python native |
| 16 | Cache store | Save result with timestamp |
| 17 | Return | JSON to frontend via axios |

### 16.1 Dynamic Scoring & Aspect Boosting Mathematics

The core innovation of AspectMind is how it mathematically combines *semantic relevance* and *sentiment alignment*. When products are retrieved, their ranking score is dynamically altered based on how previous reviews align with the user's query:

**1. Initial Base Score (Semantic Vector Space)**
- `Base Score = FAISS Inner Product (Normalized Cosine Similarity)`
- Measures how closely the product description matches the query text conceptually.

**2. First-Stage Aspect Boost**
- For every aspect the user cares about (e.g., "strength"), the algorithm checks the product's pre-computed ABSA profile.
- **Positive Match (+0.15):** If a previous reviewer praised this aspect, the product receives a heavy +0.15 flat boost to its semantic score.
- **Negative Match (-0.05):** If a reviewer criticized this aspect, the product's score is penalized by -0.05.
- *Why it matters:* A conceptually similar product with terrible reviews on the exact feature the user wants will be artificially pushed down, while a product proven to have that feature will leap to the top.

**3. Second-Stage Cross-Encoder Scaling**
- The top 30 candidates are passed to the Cross-Encoder for deep contextual re-ranking.
- `Cross-Encoder Score = sigmoid(CE_Raw_Logit)` Maps the raw score to a smooth `[0, 1]` curve.
- The aspect boost (+0.1 / -0.1) is re-applied to this sigmoid curve to ensure sentiment alignment strongly influences the final, highly accurate Top 10 sort.

### 16.2 The Continuous Learning Loop (Real-Time Feedback Integration)

A critical architectural feature of AspectMind is its capacity for continuous, real-time learning without requiring a full model retrain. 

When an early customer submits feedback (e.g., "This table has great strength"):
1. The `add_feedback` endpoint instantly runs a fast-path ABSA inference on the feedback text.
2. The product's `aspects_sentiments` dictionary is immediately injected with the new data (`"strength": {"sentiment": "Positive"}`).
3. This update happens **in-memory instantly** (microseconds) while a background daemon thread persists it to disk.

Because the ranking mathematics (detailed in 16.1) evaluate the product's aspect dictionary dynamically at query time, **early customer feedback instantaneously alters future search results.** The next time a subsequent user searches for "strong table," the system detects the newly added "strength" aspect, applies the mathematical boost, and elevates that product in the search results ahead of competitors.

---

## 17. Aspect-Based Sentiment Analysis (ABSA) — Deep Dive

### What is ABSA?
Standard SA: "Is this review positive?" → Mixed  
ABSA: "Is 'battery' positive? Is 'camera' negative?" → Targeted, granular

### AspectMind ABSA Pipeline

**1. Extract aspects (spaCy noun chunks):**
```
"Battery lasts 3 days but camera is disappointing"
→ ["battery", "camera"]
```

**2. Format for DeBERTa:**
```
"[CLS] Battery lasts 3 days but camera is disappointing [SEP] battery [SEP]"
"[CLS] Battery lasts 3 days but camera is disappointing [SEP] camera [SEP]"
```

**3. Model inference:**
```python
outputs = self.absa_pipe(inputs)
# [{"label": "Positive", "score": 0.96}, {"label": "Negative", "score": 0.89}]
```

**4. Threshold filter:** Only keep `score > 0.6` (confidence threshold)

**5. Store as JSON string:**
```json
{"battery": {"sentiment": "Positive", "confidence": 0.96},
 "camera":  {"sentiment": "Negative", "confidence": 0.89}}
```

### ABSA Performance

| Hardware | Throughput | Time for 134K reviews |
|---|---|---|
| CPU (no GPU) | ~50-100 pairs/sec | 6–12 hours |
| GPU (CUDA) | ~500-1000 pairs/sec | 30–60 minutes |
| Warm start (cached) | Instant | 0 seconds |

This is why caching is critical. First run is expensive; every subsequent run is instant.

---

## 18. Performance Optimizations

| Optimization | Location | Technique | Benefit |
|---|---|---|---|
| Gradient disabled | `__init__` L34 | `torch.set_grad_enabled(False)` | Memory + speed |
| INT8 quantization | `_load_models()` L126 | `quantize_dynamic({Linear}, qint8)` | ~2x faster CPU CE |
| spaCy disabled pipes | `_load_models()` L91 | `disable=['ner','lemmatizer']` | ~2x faster NLP |
| Batch NLP | `_extract_aspects_batch()` | `nlp.pipe(texts, batch_size=128)` | Parallel text processing |
| ABSA chunking | `_extract_multi_aspects()` | 400-review chunks | Prevents OOM |
| `inference_mode()` | ABSA inference | More efficient than `no_grad()` | Additional memory savings |
| DataFrame cache | `_prepare_data()` | Pickle serialization | Avoids hours of ABSA |
| FAISS index cache | `_prepare_embeddings()` | Binary index file | Avoids SBERT re-encoding |
| FAISS vs KNN | `_prepare_embeddings()` | C++ FAISS | 10-100x faster search |
| CE on top-30 only | `recommend()` L430 | Limit candidates | Limits expensive inference |
| CE text truncation | `recommend()` L422 | `[:200]` chars | Faster CE input |
| Query cache | `recommend()` | MD5 dict + 1h TTL | Instant repeat queries |
| GC after ABSA chunks | `_extract_multi_aspects()` L235 | `gc.collect()` | RAM cleanup |
| CUDA cache clear | `_extract_multi_aspects()` L237 | `torch.cuda.empty_cache()` | GPU OOM prevention |
| Non-blocking saves | `add_feedback()` L623 | Daemon thread | Feedback responds <100ms |
| 3 aspects max | `_extract_aspects_batch()` L171 | `[:3]` | 3x fewer ABSA calls |
| Fallback ABSA only top-N | `recommend()` L471 | Only final 10 | Avoids all 30 candidates |
| High feedback threshold | `add_feedback()` L545 | `threshold=0.7, max_aspects=3` | Faster feedback ABSA |

---

## 19. Error Handling & Fallbacks

### Backend
- **Startup failure:** Full traceback captured in `startup_error`, returned on every API call
- **Missing local models:** Fallback to HuggingFace download (fails in offline, caught+reported)
- **ABSA failure:** Fallback to `{"general": {"sentiment": "Neutral", "confidence": 0.0}}`
- **Cache corruption:** `_load_data_cache()` catches exception, reprocesses from CSV
- **NumPy serialization:** `_sanitize_for_json()` recursively converts all NumPy/NaN/Inf types
- **Missing product in feedback:** Returns `{"status": "error", "message": "Product not found"}`
- **Comparison missing product:** Product silently skipped, others still compared

### Frontend
- **Image load failure:** `onError` → base64 SVG placeholder (offline-safe)
- **Invalid URL detection:** Pre-validated before render (`nan`, empty, non-http filtered)
- **API unreachable:** Error state shows "Failed to fetch recommendations. Ensure backend is running."
- **Dashboard load failure:** Error state shown inside modal with Close button
- **Comparison load failure:** Error state shown inside comparison overlay

---

## 20. Known Limitations & Future Work

### Current Limitations

| Limitation | Detail |
|---|---|
| Cold start time | First run: hours for ABSA on 134K reviews |
| RAM usage | 2-4 GB required for models + data |
| CPU-only default | No CUDA setup; GPU would accelerate 10x |
| Single user | No authentication; local dev only |
| Static dataset | No live Amazon data |
| CORS wildcard | `allow_origins=["*"]` — insecure for production |
| No persistent DB | Feedback in CSV/PKL; lost on PKL deletion |
| 18% invalid images | ~24K products have broken/missing image URLs |

### Potential Improvements

1. **GPU/CUDA setup** — FP16 mixed-precision inference
2. **Streaming API** — Server-Sent Events for progressive results
3. **User accounts** — Personalized history and preferences
4. **Live data** — Real-time product API integration
5. **Cloud vector DB** — Pinecone/Weaviate replacing FAISS files
6. **HNSW usage** — Approximate NN for larger scale
7. **Multi-language** — Multilingual SBERT + ABSA
8. **Reinforcement learning** — Feedback-driven ranking improvement
9. **Docker containerization** — Reproducible deployment
10. **Production CORS** — Whitelist specific frontend origins

---

## Appendix A — File Size Reference

| File | Size |
|---|---|
| `fixed_image_urls.csv` (root) | 318.5 MB |
| `data/Second_fixed_image_urls.csv` | 403 MB |
| `data/Second_fixed_image_urls.csv_processed.pkl` | 343 MB |
| `embeddings/enriched_item_descriptions_embeddings.npy` | 147 MB |
| `embeddings/faiss_index.bin` | 147 MB |
| `embeddings/hnsw_index.bin` | 162 MB |
| `embeddings/knn_model.pkl` | 147 MB |
| `server/recommender.py` | 37.3 KB |
| `server/main.py` | 3.9 KB |
| `server/setup_offline.py` | 3.6 KB |
| `client/src/components/Comparison.jsx` | 11.9 KB |
| `client/src/components/ProductCard.jsx` | 10.2 KB |
| `client/src/components/Dashboard.jsx` | 8.3 KB |

---

## Appendix B — Port Reference

| Service | Port | URL |
|---|---|---|
| React Frontend (Vite) | 5173 | http://localhost:5173 |
| FastAPI Backend (uvicorn) | 8000 | http://localhost:8000 |
| Swagger Auto-Docs | 8000 | http://localhost:8000/docs |
| ReDoc Auto-Docs | 8000 | http://localhost:8000/redoc |

---

## Appendix C — Key Coding Decisions Summary

| Decision | Why |
|---|---|
| FastAPI over Flask | Async support, automatic Pydantic validation, auto-generated Swagger docs |
| FAISS over sklearn KNN | 10-100x faster C++ vectorized search |
| DeBERTa over BERT for ABSA | DeBERTa-v3 uses disentangled attention, outperforms BERT on NLU tasks |
| MiniLM for SBERT | Balance of speed and quality; 6 layers vs BERT's 12 |
| Offline mode mandatory | Reproducible, no network dependency, secure in air-gapped environments |
| PKL cache for DataFrame | Pandas `.to_pickle()` preserves dtypes perfectly; faster than CSV re-read |
| `use_fast=False` for DeBERTa | DeBERTa-v3 SentencePiece tokenizer incompatible with fast Rust tokenizer |
| INT8 quantization for CE | ~2x CPU speedup with negligible accuracy loss for ranking |
| Daemon thread for feedback saves | User-facing response latency unaffected by disk I/O |
| React 19 + Vite (rolldown) | Latest stable React + Rust-based bundler for fastest HMR |
| CSS variables over TailwindCSS | Maximum CSS flexibility, no build dependency, easier runtime theming |
| Framer Motion for animations | Production-quality physics animations without raw CSS keyframe complexity |

---

## 21. Backend Source Code — Annotated Deep Dive

This section shows the **actual source code** of the most important backend files with detailed inline annotations explaining every critical decision.

---

### 21.1 `main.py` — Complete Source

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
import traceback

# ── OFFLINE MODE ─────────────────────────────────────────────────────────────
# These two lines MUST come before any HuggingFace import.
# They prevent transformers from ever making a network call.
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'
# ─────────────────────────────────────────────────────────────────────────────

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from recommender import ProductRecommender

app = FastAPI(title="Product Recommender API")

# Allow the React dev server on :5173 to call the API on :8000 without CORS errors.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # wildcard is safe for local-only dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globals — one recommender instance per server lifetime
recommender = None
startup_error = None  # captured traceback if init fails

@app.on_event("startup")
def startup_event():
    global recommender, startup_error
    print("Starting Server & Loading Models...")
    try:
        # Loads ~1 GB of models + data into RAM — happens ONCE at boot
        recommender = ProductRecommender()
        print("Model loaded successfully!")
    except Exception as e:
        # Capture error; don't crash server — return it on every API call instead
        startup_error = traceback.format_exc()
        print(f"Error loading recommender:\n{startup_error}")

@app.get("/")
def read_root():
    if startup_error:
        return {"status": "error", "message": "Server failed to start correctly",
                "detail": startup_error}
    return {"status": "active", "message": "Product Recommender API is running"}

@app.get("/search")
def search(
    q: str,                        # required — the user's natural-language query
    category: str = None,          # optional category filter
    min_sentiment: float = None,   # optional [-1.0, 1.0] sentiment floor
    sort_by: str = "relevance"     # "relevance" | "sentiment" | "name"
):
    if startup_error:
        raise HTTPException(status_code=500,
                            detail=f"Server startup failed: {startup_error}")
    if not recommender:
        raise HTTPException(status_code=503, detail="Model is still loading...")
    try:
        results = recommender.recommend(
            q,
            category_filter=category,
            min_sentiment_score=min_sentiment,
            sort_by=sort_by
        )
        return results
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Pydantic models auto-validate POST JSON bodies.
# Missing or wrong-type field → FastAPI returns 422 automatically.
class FeedbackRequest(BaseModel):
    product_id: str
    feedback: str

class AnalysisRequest(BaseModel):
    text: str

class CompareRequest(BaseModel):
    product_ids: list[str]   # 2–4 product IDs for side-by-side comparison

@app.post("/feedback")
def submit_feedback(data: FeedbackRequest):
    if not recommender:
        raise HTTPException(status_code=503, detail="Model service unavailable")
    return recommender.add_feedback(data.product_id, data.feedback)

@app.post("/analyze")
def analyze_text(data: AnalysisRequest):
    # Live ABSA preview — no DB write, just returns detected aspects
    if not recommender:
        raise HTTPException(status_code=503, detail="Model service unavailable")
    return recommender.analyze_text_only(data.text)

@app.get("/analytics")
def get_analytics():
    if startup_error:
        raise HTTPException(status_code=500,
                            detail=f"Server startup failed: {startup_error}")
    if not recommender:
        raise HTTPException(status_code=503, detail="Model is still loading...")
    try:
        return recommender.get_analytics()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compare")
def compare_products(data: CompareRequest):
    if not recommender:
        raise HTTPException(status_code=503, detail="Model service unavailable")
    try:
        return recommender.compare_products(data.product_ids)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Why `startup_error` instead of crashing?**  
If we let an exception propagate out of `startup_event`, FastAPI silently swallows it and the server stays up — returning cryptic 500 errors with no explanation. Capturing it in `startup_error` lets every endpoint return a *human-readable* message showing the exact traceback, making debugging far faster.

---

### 21.2 `recommender.py` — Constructor & Model Loading

#### Imports & Directory Constants

```python
import os, gc, json, torch, numpy as np, pandas as pd
from tqdm import tqdm
import spacy
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.neighbors import NearestNeighbors
import joblib, threading, time, hashlib
from functools import lru_cache

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # .../server/
DATA_DIR  = os.path.join(BASE_DIR, "../data")          # .../data/
EMB_DIR   = os.path.join(BASE_DIR, "../embeddings")    # .../embeddings/
MODEL_DIR = os.path.join(BASE_DIR, "../models")        # .../models/
```

Using `__file__`-relative paths means the server works regardless of the working directory the user runs it from.

#### `__init__` — Constructor

```python
def __init__(
    self,
    dataframe_name="Second_fixed_image_urls.csv",
    max_dataset_size=200000,   # hard cap prevents OOM on huge CSVs
    absa_chunk_size=400,       # reviews per outer ABSA loop iteration
    absa_batch_size=16,        # inference pairs sent to GPU/CPU per forward pass
    top_n=10                   # default result count
):
    # Disable gradient computation globally — inference only, saves RAM + time
    torch.set_grad_enabled(False)
    self.device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {self.device.upper()}")

    self.dataframe_name   = dataframe_name
    self.cache_path       = os.path.join(DATA_DIR, f"{dataframe_name}_processed.pkl")
    self.absa_chunk_size  = absa_chunk_size
    self.absa_batch_size  = absa_batch_size
    self.top_n            = top_n
    self.max_dataset_size = max_dataset_size
    self.dataframe_path   = os.path.join(DATA_DIR, dataframe_name)
    self.emb_path         = os.path.join(EMB_DIR, "enriched_item_descriptions_embeddings.npy")
    self.knn_path         = os.path.join(EMB_DIR, "knn_model.pkl")
    self.absa_model_path  = os.path.join(MODEL_DIR, "deberta-v3-base-absa")

    # Load raw CSV first (needed as fallback even on cache hit)
    self.df_original = pd.read_csv(self.dataframe_path)

    self._load_models()                    # Step 1 — load all AI models
    self.df = self._prepare_data()         # Step 2 — process CSV or restore cache
    self._prepare_embeddings_and_index()   # Step 3 — load/build FAISS index

    # In-memory query cache: {md5_hash: (result_dict, unix_timestamp)}
    self.query_cache   = {}
    self.cache_max_size = 100
    self.cache_ttl      = 3600  # 1 hour TTL
    print("Initialization Complete.")
```

#### `_load_models` — All Three AI Models

```python
def _load_models(self):
    # ── spaCy ──────────────────────────────────────────────────────────────
    try:
        # disable=['ner','lemmatizer'] skips unused pipeline stages → ~2x faster
        self.nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
    except OSError:
        # First-time fallback: download the model if not installed
        from spacy.cli import download
        download("en_core_web_sm")
        self.nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])

    # ── SBERT (all-MiniLM-L6-v2) ───────────────────────────────────────────
    sbert_path = os.path.join(MODEL_DIR, "all-MiniLM-L6-v2")
    if os.path.exists(sbert_path):
        self.sbert = SentenceTransformer(sbert_path, device=self.device)
    else:
        # Warning: this network call will fail when TRANSFORMERS_OFFLINE=1
        self.sbert = SentenceTransformer("all-MiniLM-L6-v2", device=self.device)

    # ── Cross-Encoder (ms-marco-MiniLM-L-6-v2) ────────────────────────────
    ce_path = os.path.join(MODEL_DIR, "ms-marco-MiniLM-L-6-v2")
    if os.path.exists(ce_path):
        self.cross_encoder = CrossEncoder(ce_path, device=self.device)
    else:
        self.cross_encoder = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2", device=self.device)

    # CPU-only: INT8 dynamic quantization for ~2x speed boost
    # Converts all nn.Linear weight tensors from float32 → int8
    # Activations stay float32 — hence "dynamic" (computed at runtime)
    if self.device == "cpu":
        try:
            self.cross_encoder.model = torch.quantization.quantize_dynamic(
                self.cross_encoder.model,
                {torch.nn.Linear},
                dtype=torch.qint8
            )
        except Exception as e:
            print(f"Quantization skipped: {e}")

    # ── DeBERTa-v3 ABSA ────────────────────────────────────────────────────
    if os.path.exists(self.absa_model_path):
        # use_fast=False is CRITICAL: DeBERTa-v3 uses SentencePiece tokenization
        # which is incompatible with the Rust fast tokenizer in transformers.
        # Using use_fast=True causes: LookupError: convert_slow_tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            self.absa_model_path, use_fast=False)
        model = AutoModelForSequenceClassification.from_pretrained(
            self.absa_model_path)
        model.to(self.device)
    else:
        raise FileNotFoundError(
            f"ABSA model not found at {self.absa_model_path}. "
            "Run setup_offline.py first.")

    # Wrap in HuggingFace pipeline for convenient batch inference
    # truncation=True: silently clips inputs > 512 tokens instead of erroring
    # device=0 places pipeline on GPU:0; device=-1 forces CPU
    self.absa_pipe = pipeline(
        "text-classification",
        model=model,
        tokenizer=tokenizer,
        truncation=True,
        device=0 if self.device == "cuda" else -1
    )
    print("Models Loaded.")
```

---

### 21.3 `recommender.py` — Aspect Extraction (spaCy)

#### `_extract_aspects_batch` — Noun Chunk Extraction

```python
def _extract_aspects_batch(self, texts):
    """
    Given a list of raw text strings, return a list of aspect lists.
    Each aspect list contains up to 3 noun phrases extracted by spaCy.
    """
    aspects_list = []
    # nlp.pipe() processes ALL texts in a single batch (batch_size=128)
    # which is 10-20x faster than calling nlp(text) in a Python loop.
    for doc in self.nlp.pipe(texts, batch_size=128):
        aspects = []
        for chunk in doc.noun_chunks:  # grammatical noun phrases
            a = chunk.text.lower().strip()
            # Filter noise: too-short tokens and meaningless generic nouns
            if len(a) > 2 and a not in {"it", "this", "that", "product", "item"}:
                aspects.append(a)
        # Deduplicate and cap at 3 aspects per text.
        # 3 aspects × N reviews = 3N ABSA calls instead of N*avg_nouns ABSA calls.
        aspects_list.append(list(set(aspects))[:3] or ["general"])
    return aspects_list
```

**Why noun chunks (not keywords)?**  
spaCy's noun chunk parser uses POS (Part-Of-Speech) tags to find grammatically coherent phrases like `"battery life"` or `"overall design quality"` rather than individual words. This preserves meaningful multi-word aspects that keyword extraction would split.

#### `_extract_multi_aspects_single` — Per-Text Fast Path

```python
def _extract_multi_aspects_single(self, text, threshold=0.6, max_aspects=None):
    """
    Run ABSA on a single text string (used for feedback & live query analysis).
    threshold: minimum confidence to accept a prediction
    max_aspects: cap on number of aspects (for faster feedback inference)
    """
    aspects = self._extract_aspects_batch([text])[0]

    if max_aspects and len(aspects) > max_aspects:
        aspects = aspects[:max_aspects]  # feedback uses max_aspects=3 for speed

    inputs, meta = [], []
    for aspect in aspects:
        # Standard ABSA input format for DeBERTa:
        # [CLS] review_text [SEP] aspect_term [SEP]
        inputs.append(f"[CLS] {text} [SEP] {aspect} [SEP]")
        meta.append(aspect)

    if not inputs:
        return {}

    with torch.no_grad():    # single text — no_grad() is fine here
        outputs = self.absa_pipe(inputs)

    results = {}
    for aspect, out in zip(meta, outputs):
        if out["score"] > threshold:
            results[aspect] = {
                "sentiment": out["label"].capitalize(),  # "positive" → "Positive"
                "confidence": out["score"]
            }
    return results
```

---

### 21.4 `recommender.py` — Batch ABSA Pipeline

#### `_extract_multi_aspects` — Bulk Inference Over 134K Reviews

This is the **most computationally expensive method** in the entire codebase. It is called exactly once on the first cold start and its output is cached as a `.pkl` file.

```python
def _extract_multi_aspects(self, reviews):
    """
    Run ABSA over all product reviews to pre-compute aspect sentiments.
    reviews: list of raw review strings (134,520 items in production)
    Returns: list of dicts, one per review
             e.g. {"battery life": {"sentiment": "Positive", "confidence": 0.94}}
    """
    results = []

    # Process in chunks of 400 reviews to avoid OOM on CPU.
    # Each chunk: extract spaCy aspects, then send (review, aspect) pairs to DeBERTa.
    for i in tqdm(range(0, len(reviews), self.absa_chunk_size), desc="ABSA"):
        batch_reviews = reviews[i : i + self.absa_chunk_size]

        # Step 1 — extract noun phrases from all 400 reviews in parallel
        batch_aspects = self._extract_aspects_batch(batch_reviews)

        # Step 2 — build (review, aspect) pairs as formatted ABSA inputs
        texts, meta = [], []
        for review, aspects in zip(batch_reviews, batch_aspects):
            for aspect in aspects:
                texts.append(f"[CLS] {review} [SEP] {aspect} [SEP]")
                meta.append((review, aspect))   # track which pair this is

        if not texts:
            # Edge case: all 400 reviews had no extractable aspects
            results.extend(
                [{"general": {"sentiment": "Neutral", "confidence": 0.0}}]
                * len(batch_reviews)
            )
            continue

        # Step 3 — batch inference
        # torch.inference_mode() is more memory-efficient than torch.no_grad():
        # it also disables version-counter tracking in autograd, saving more RAM.
        with torch.inference_mode():
            outputs = self.absa_pipe(texts, batch_size=self.absa_batch_size)

        # Step 4 — map predictions back to their source review
        # Each review may have multiple (aspect, prediction) entries.
        review_map = {}
        for (review, aspect), out in zip(meta, outputs):
            review_map.setdefault(review, {})
            if out["score"] > 0.6:   # confidence threshold: ignore weak predictions
                review_map[review][aspect] = {
                    "sentiment": out["label"].capitalize(),
                    "confidence": out["score"]
                }

        # Step 5 — collect results in original order
        for review in batch_reviews:
            results.append(
                review_map.get(
                    review,
                    {"general": {"sentiment": "Neutral", "confidence": 0.0}}
                )
            )

        # Step 6 — explicit memory cleanup after every chunk
        gc.collect()                              # Python garbage collect
        if self.device == "cuda":
            torch.cuda.empty_cache()              # release GPU memory fragmentation

    return results  # list of 134,520 aspect-sentiment dicts
```

**Key insight — the `[CLS] review [SEP] aspect [SEP]` format:**  
This is the exact input format `yangheng/deberta-v3-base-absa-v1.1` was fine-tuned on. The model was trained on the SemEval ABSA dataset using this token structure. Deviating from it (e.g., `aspect: review`) produces significantly worse accuracy.

---

### 21.5 `recommender.py` — Data Preparation & Caching

#### `_prepare_data` — Three-Tier Strategy

```python
def _prepare_data(self):
    # ── Tier 1: Try PKL cache (sub-second) ────────────────────────────────
    cached_df = self._load_data_cache()
    if cached_df is not None:
        return cached_df   # warm start: done here in <1 second

    # ── Tier 2: Process CSV from scratch ────────────────────────────────
    df = self.df_original.copy()

    # Drop rows where the review is too short to carry aspect information
    if "reviewText" in df.columns:
        df = df[df["reviewText"].astype(str).str.len() > 15]

    # Apply row cap to prevent OOM crashes on very large CSVs
    df = df.head(self.max_dataset_size).reset_index(drop=True)

    # Ensure description + feature columns always exist (some rows are NaN)
    for col in ["description", "feature"]:
        if col not in df.columns:
            df[col] = ""
        else:
            df[col] = df[col].fillna("")

    # item_unique_id deduplicates products that appear in multiple review rows.
    # Two rows with same name+category+description+feature = same product.
    df["item_unique_id"] = (
        df["itemName"].astype(str) + df["category"].astype(str)
        + df["description"] + df["feature"]
    )

    # Run bulk ABSA only if the column doesn't already exist in CSV
    # (CSV may have been pre-populated by a previous run)
    if "aspects_sentiments" not in df.columns:
        print("Extracting aspects (this may take a very long time)...")
        aspects = self._extract_multi_aspects(df["reviewText"].tolist())
        # Store as JSON string so pandas serializes it cleanly in PKL/CSV
        df["aspects_sentiments"] = [json.dumps(x) for x in aspects]

    # ── Tier 3: Write PKL cache for next startup ────────────────────────
    self._save_data_cache(df)
    return df

def _load_data_cache(self):
    if os.path.exists(self.cache_path):
        try:
            return pd.read_pickle(self.cache_path)   # ~343 MB, loads in ~3-5 sec
        except Exception as e:
            # Corrupted pickle (e.g. interrupted write) — fall back to CSV reprocess
            print(f"Cache corrupt: {e}. Reprocessing from CSV.")
    return None

def _save_data_cache(self, df):
    try:
        df.to_pickle(self.cache_path)   # preserves all dtypes, faster than CSV
    except Exception as e:
        print(f"Failed to save cache: {e}")
```

**Why Pickle over CSV for the cache?**  
Pandas `.to_pickle()` / `pd.read_pickle()` is ~5-10x faster than `to_csv()` / `read_csv()` for DataFrames with mixed types. It also perfectly preserves column dtypes (string columns stay string, not `object` with silent casting), which is critical for the JSON-encoded `aspects_sentiments` column.

---

*End of AspectMind Full Technical Report — March 19, 2026 (Page 1 of 2)*

---

### 21.6 `recommender.py` — Embeddings & FAISS Index

```python
def _prepare_embeddings_and_index(self):

    # ── Step 1: Build enriched text per product ────────────────────────────
    def enrich(row):
        # Append aspect+sentiment tokens to the product text so FAISS
        # embeddings encode BOTH product semantics AND review sentiment.
        # e.g.  "... battery Positive camera Negative"
        try:
            aspects = json.loads(row["aspects_sentiments"])
        except:
            aspects = {}
        return " ".join(
            f"{a} {v['sentiment']}"
            for a, v in aspects.items()
            if v["confidence"] > 0.6   # only high-confidence labels
        )

    # Concatenate: product name + category + description + feature + aspect labels
    self.df["enriched_text"] = (
        self.df["itemName"].astype(str) + " "
        + self.df["category"].astype(str) + " "
        + self.df["description"].astype(str) + " "
        + self.df["feature"].astype(str) + " "
        + self.df.apply(enrich, axis=1)
    )

    # ── Step 2: De-duplicate ───────────────────────────────────────────────
    # Multiple review rows may refer to the same product.
    # FAISS needs one vector per unique product, not one per review.
    unique_df = self.df.drop_duplicates("item_unique_id")
    self.item_ids = unique_df["item_unique_id"].tolist()  # index→id mapping
    self.unique_df = unique_df

    # ── Step 3: Load or compute SBERT embeddings ──────────────────────────
    if os.path.exists(self.emb_path):
        embeddings = np.load(self.emb_path)   # fast binary load (~147 MB)
        if len(embeddings) != len(unique_df): # shape mismatch = dataset changed
            print("Embeddings mismatch. Recomputing...")
            embeddings = None
    else:
        embeddings = None

    if embeddings is None:
        texts = unique_df["enriched_text"].tolist()
        # encode() with batch_size=64 processes 64 texts per GPU/CPU forward pass
        embeddings = self.sbert.encode(
            texts, batch_size=64,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        embeddings = embeddings.astype('float32')  # FAISS requires float32

        import faiss
        # L2-normalize each vector so inner product == cosine similarity.
        # After normalization: dot(a, b) = cos(a, b) since |a|=|b|=1.
        faiss.normalize_L2(embeddings)
        np.save(self.emb_path, embeddings)         # persist for next startup

    # ── Step 4: Build or load FAISS index ───────────────────────────────
    self.index_path = os.path.join(EMB_DIR, "faiss_index.bin")
    try:
        import faiss
        if os.path.exists(self.index_path):
            # Load pre-built index from disk in ~1 second
            self.index = faiss.read_index(self.index_path)
        else:
            d = embeddings.shape[1]   # 384 dimensions
            # IndexFlatIP = exact inner product search (brute force, no approximation)
            # On 50K-60K unique products it runs in <100ms per query
            self.index = faiss.IndexFlatIP(d)
            self.index.add(embeddings)             # add all ~50K vectors
            faiss.write_index(self.index, self.index_path)  # persist
    except ImportError:
        # FAISS not installed: fall back to sklearn KNN
        print("FAISS not available. Falling back to KNN.")
        if os.path.exists(self.knn_path):
            self.knn_index = joblib.load(self.knn_path)
        else:
            self.knn_index = NearestNeighbors(
                n_neighbors=50, metric='cosine', algorithm='auto')
            self.knn_index.fit(embeddings)
            joblib.dump(self.knn_index, self.knn_path)
        self.index = None   # flag: use knn_index branch in recommend()
```

**Why `IndexFlatIP` and not `IndexHNSW`?**  
`IndexFlatIP` is exact (no approximation errors). For 50K-60K unique products it runs in <100ms per query, making approximation unnecessary. HNSW would be needed only at millions of vectors.

---

### 21.7 `recommender.py` — `recommend()` Full Implementation

This is the core function called on every `/search` request.

```python
def recommend(self, user_query, top_n_results=10,
              category_filter=None, min_sentiment_score=None,
              sort_by="relevance"):

    # ───────────────────────────────────────────────────────────────
    # STEP 1 — QUERY CACHE CHECK
    # ───────────────────────────────────────────────────────────────
    # MD5 produces a 32-char hex string keying the entire query+filter state.
    cache_key = hashlib.md5(
        f"{user_query}_{category_filter}_{min_sentiment_score}_{sort_by}"
        .encode()
    ).hexdigest()

    if cache_key in self.query_cache:
        result, timestamp = self.query_cache[cache_key]
        if time.time() - timestamp < self.cache_ttl:   # 1-hour window
            return result   # instant return, zero model inference

    # Evict oldest 20 entries if cache is full (LRU-lite)
    if len(self.query_cache) > self.cache_max_size:
        sorted_items = sorted(self.query_cache.items(), key=lambda x: x[1][1])
        for key, _ in sorted_items[:20]:
            del self.query_cache[key]

    # ───────────────────────────────────────────────────────────────
    # STEP 2 — QUERY ANALYSIS (aspects + overall sentiment)
    # ───────────────────────────────────────────────────────────────
    # _infer_user_aspects() runs spaCy + ABSA on the query itself.
    # E.g. "good battery life" → [("battery life", "Positive", 0.91)]
    query_aspects = self._infer_user_aspects(user_query)
    user_comment_analysis = self._format_user_aspect_sentiment(query_aspects)
    overall_sentiment = self._compute_overall_sentiment(user_comment_analysis)

    # ───────────────────────────────────────────────────────────────
    # STEP 3 — FAISS VECTOR SEARCH (top-30 candidates)
    # ───────────────────────────────────────────────────────────────
    query_emb = self.sbert.encode(user_query, convert_to_numpy=True).reshape(1, -1)
    cands_count = min(top_n_results * 3, len(self.item_ids))  # e.g. 10*3=30

    if hasattr(self, 'index') and self.index is not None:
        import faiss
        faiss.normalize_L2(query_emb)  # must normalize for IP == cosine sim
        distances, indices = self.index.search(query_emb, cands_count)
        is_faiss = True
    else:
        distances, indices = self.knn_index.kneighbors(
            query_emb, n_neighbors=cands_count)
        is_faiss = False

    # ───────────────────────────────────────────────────────────────
    # STEP 4 — SCORE CANDIDATES + APPLY FILTERS + ASPECT BOOST
    # ───────────────────────────────────────────────────────────────
    candidates = []
    query_aspect_names = set(qa[0] for qa in query_aspects)

    for idx, dist in zip(indices[0], distances[0]):
        if idx >= len(self.item_ids):
            continue
        item_id = self.item_ids[idx]
        row = self.unique_df[self.unique_df["item_unique_id"] == item_id].iloc[0]

        # Category filter: skip non-matching categories
        if category_filter and \
           str(row["category"]).lower() != category_filter.lower():
            continue

        try:
            aspects = json.loads(row["aspects_sentiments"])
        except:
            aspects = {}

        # Aspect boost: reward products whose reviews confirm user's desired aspects
        boost = 0.0
        for qa_name in query_aspect_names:
            if qa_name in aspects:
                if aspects[qa_name].get("sentiment") == "Positive":
                    boost += 0.15   # strong reward for confirmed positive match
                elif aspects[qa_name].get("sentiment") == "Negative":
                    boost -= 0.05   # mild penalty for confirmed negative match

        # Sentiment score: (positives - negatives) / total, range [-1, 1]
        pos = sum(1 for v in aspects.values() if v.get("sentiment") == "Positive")
        neg = sum(1 for v in aspects.values() if v.get("sentiment") == "Negative")
        total = max(len(aspects), 1)
        sentiment_score = (pos - neg) / total

        # Sentiment filter: skip products below the user's minimum threshold
        if min_sentiment_score is not None and sentiment_score < min_sentiment_score:
            continue

        # Base score from FAISS (cosine sim) or KNN (1 - cosine dist)
        base = float(dist) if is_faiss else float(1 - dist)
        final_score = base + boost

        candidates.append({
            "id": item_id,
            "name": row["itemName"],
            "category": row["category"],
            "image": str(row["image"]) if pd.notna(row.get("image")) else "",
            "description": str(row.get("description", "")),
            "feature": str(row.get("feature", "")),
            "score": final_score,
            "sentiment_score": sentiment_score,
            "aspects": aspects,
            "row_ref": row,
            # Truncate to 200 chars before feeding to cross-encoder
            "text_for_ce": str(row["itemName"]) + " "
                           + str(row.get("description", ""))[:200]
        })

    # ───────────────────────────────────────────────────────────────
    # STEP 5 — CROSS-ENCODER RE-RANK (top 30 only)
    # ───────────────────────────────────────────────────────────────
    if candidates:
        candidates.sort(key=lambda x: x["score"], reverse=True)
        top30 = candidates[:min(30, len(candidates))]

        # Cross-encoder scores each (query, product) pair jointly.
        # Much more accurate than cosine sim but O(N) inference — limited to 30.
        ce_pairs = [[user_query, c["text_for_ce"]] for c in top30]
        ce_scores = self.cross_encoder.predict(ce_pairs)

        import math
        def sigmoid(x): return 1 / (1 + math.exp(-x))

        for i, c in enumerate(top30):
            # Re-apply aspect boost on top of sigmoid-normalised CE score
            boost = 0.0
            for qa_name in query_aspect_names:
                if qa_name in c["aspects"]:
                    if c["aspects"][qa_name].get("sentiment") == "Positive":
                        boost += 0.1
                    elif c["aspects"][qa_name].get("sentiment") == "Negative":
                        boost -= 0.1
            c["score"] = sigmoid(ce_scores[i]) + boost

    # ───────────────────────────────────────────────────────────────
    # STEP 6 — SORT + SELECT TOP N
    # ───────────────────────────────────────────────────────────────
    if sort_by == "sentiment":
        candidates.sort(key=lambda x: x["sentiment_score"], reverse=True)
    elif sort_by == "name":
        candidates.sort(key=lambda x: x["name"].lower())
    else:   # default: relevance
        candidates.sort(key=lambda x: x["score"], reverse=True)

    final_recs = candidates[:top_n_results]

    # ───────────────────────────────────────────────────────────────
    # STEP 7 — ENRICH RESULTS + BUILD EXPLANATIONS
    # ───────────────────────────────────────────────────────────────
    results = []
    for rec in final_recs:
        aspects = rec["aspects"]
        row = rec["row_ref"]

        # Fallback: if a product lacks BOTH positive AND negative aspects,
        # run live ABSA on its review text or description.
        # Only applied to final top-N, not all 30 candidates.
        has_pos = any(v.get("sentiment") == "Positive" for v in aspects.values())
        has_neg = any(v.get("sentiment") == "Negative" for v in aspects.values())
        if not has_pos or not has_neg:
            context = str(row.get("reviewText", ""))
            if len(context) < 20:
                context = f"{row['itemName']} {row['category']} {row['description']}"
            fresh = self._extract_multi_aspects_single(
                context[:1000], threshold=0.1)
            for k, v in fresh.items():
                if k not in aspects:
                    aspects[k] = v

        # Build sorted positive/negative lists
        pos_list = sorted(
            [{"name": a, "score": v["confidence"]}
             for a, v in aspects.items() if v.get("sentiment") == "Positive"],
            key=lambda x: x["score"], reverse=True
        )
        neg_list = sorted(
            [{"name": a, "score": v["confidence"]}
             for a, v in aspects.items() if v.get("sentiment") == "Negative"],
            key=lambda x: x["score"], reverse=True
        )

        matched = [a for a in query_aspect_names
                   if a in aspects and aspects[a].get("sentiment") == "Positive"]

        results.append({
            "product": rec["name"],
            "matched_aspects": matched,
            "top_pos_aspects": pos_list[:4],
            "top_neg_aspects": neg_list[:2],
            "reason": f"Winner for: {', '.join(matched)}" if matched
                      else "Highly recommended.",
            "all_aspects": aspects
        })

    # Remove internal row references before JSON serialization
    for rec in final_recs:
        if "row_ref" in rec:
            del rec["row_ref"]

    available_categories = sorted(
        list(set(self.unique_df["category"].astype(str).unique())))

    result = self._sanitize_for_json({
        "query_analysis": user_comment_analysis,
        "overall_sentiment": overall_sentiment,
        "results": results,
        "raw_recs": final_recs,
        "available_categories": available_categories
    })

    # ── CACHE STORE ──
    self.query_cache[cache_key] = (result, time.time())
    return result
```

---

---

### 21.8 `recommender.py` — Feedback Handler

```python
def add_feedback(self, product_id, feedback_text):
    start_time = time.time()

    # Run ABSA on feedback text.
    # Higher threshold (0.7) and max 3 aspects = faster than bulk ABSA.
    new_aspects = self._extract_multi_aspects_single(
        feedback_text, threshold=0.7, max_aspects=3)

    if not new_aspects:
        return {
            "status": "mid",
            "message": "No specific aspects confidently found, but recorded.",
            "feedback_analysis": {}
        }

    # Locate the product in unique_df
    mask = self.unique_df["item_unique_id"] == product_id
    if not mask.any():
        return {"status": "error", "message": "Product not found"}

    idx = self.unique_df.index[mask][0]

    # Merge new aspects into existing ones (overwrite if key conflicts)
    try:
        current_aspects = json.loads(self.unique_df.at[idx, "aspects_sentiments"])
    except:
        current_aspects = {}
    for k, v in new_aspects.items():
        current_aspects[k] = v

    updated_json = json.dumps(current_aspects)

    # ── Update in-memory DataFrames IMMEDIATELY ───────────────────────────
    # This is microsecond-speed — no I/O, just dict assignment.
    self.unique_df.at[idx, "aspects_sentiments"] = updated_json
    df_mask = self.df["item_unique_id"] == product_id
    if df_mask.any():
        self.df.loc[df_mask, "aspects_sentiments"] = updated_json

    # ── Persist to disk in a BACKGROUND DAEMON THREAD ─────────────────
    # daemon=True means this thread is destroyed when the main process exits.
    # If the server restarts before the write completes, the update is lost
    # (acceptable trade-off for <100ms response time).
    def save_all_background():
        # 1. Save processed PKL (fast reload on next startup)
        try:
            self._save_data_cache(self.df)
        except Exception as e:
            print(f"Failed to save cache: {e}")

        # 2. Update the raw CSV (source of truth for rebuilds)
        try:
            if "item_unique_id" not in self.df_original.columns:
                # Reconstruct ID column if missing from original df
                for col in ["description", "feature"]:
                    if col not in self.df_original.columns:
                        self.df_original[col] = ""
                    else:
                        self.df_original[col] = self.df_original[col].fillna("")
                self.df_original["item_unique_id"] = (
                    self.df_original["itemName"].astype(str)
                    + self.df_original["category"].astype(str)
                    + self.df_original["description"]
                    + self.df_original["feature"]
                )

            csv_mask = self.df_original["item_unique_id"] == product_id
            if csv_mask.any():
                self.df_original.loc[csv_mask, "aspects_sentiments"] = updated_json
                self.df_original.to_csv(self.dataframe_path, index=False)
        except Exception as e:
            print(f"Failed to save CSV: {e}")

    save_thread = threading.Thread(target=save_all_background, daemon=True)
    save_thread.start()
    # Return IMMEDIATELY — the client does not wait for disk writes

    analysis_formatted = {
        k: {"sentiment": v["sentiment"], "confidence": round(v["confidence"], 2)}
        for k, v in new_aspects.items()
    }
    total_ms = (time.time() - start_time) * 1000
    print(f"Feedback response time: {total_ms:.0f}ms")

    return self._sanitize_for_json({
        "status": "success",
        "message": "Feedback analyzed and product updated.",
        "feedback_analysis": analysis_formatted
    })
```

---

### 21.9 `recommender.py` — Analytics & Comparison

#### `get_analytics`

```python
def get_analytics(self):
    all_aspects = {}
    sentiment_distribution = {"Positive": 0, "Negative": 0, "Neutral": 0}
    category_stats = {}

    for idx, row in self.unique_df.iterrows():
        try:
            aspects = json.loads(row["aspects_sentiments"])
        except:
            aspects = {}

        for aspect, data in aspects.items():
            if aspect not in all_aspects:
                all_aspects[aspect] = {"positive": 0, "negative": 0,
                                       "neutral": 0, "total": 0}
            sentiment = data.get("sentiment", "Neutral")
            all_aspects[aspect][sentiment.lower()] += 1
            all_aspects[aspect]["total"] += 1
            sentiment_distribution[sentiment] += 1

        category = str(row.get("category", "Unknown"))
        if category not in category_stats:
            category_stats[category] = {"count": 0, "positive": 0, "negative": 0}
        category_stats[category]["count"] += 1
        for aspect, data in aspects.items():
            s = data.get("sentiment")
            if s == "Positive":
                category_stats[category]["positive"] += 1
            elif s == "Negative":
                category_stats[category]["negative"] += 1

    # Sort aspects by total frequency, keep top 15
    top_aspects = sorted(
        [{"name": k, **v} for k, v in all_aspects.items()],
        key=lambda x: x["total"], reverse=True
    )[:15]

    top_categories = sorted(
        [{"name": k, **v} for k, v in category_stats.items()],
        key=lambda x: x["count"], reverse=True
    )[:10]

    return self._sanitize_for_json({
        "total_products": len(self.unique_df),
        "total_aspects": len(all_aspects),
        "sentiment_distribution": sentiment_distribution,
        "top_aspects": top_aspects,
        "top_categories": top_categories,
        "dataset_info": {
            "total_reviews": len(self.df),
            "unique_products": len(self.unique_df)
        }
    })
```

#### `compare_products`

```python
def compare_products(self, product_ids):
    if not product_ids or len(product_ids) < 2:
        return {"error": "At least 2 products required"}
    if len(product_ids) > 4:
        return {"error": "Maximum 4 products can be compared"}

    products = []
    all_aspect_names = set()

    for product_id in product_ids:
        mask = self.unique_df["item_unique_id"] == product_id
        if not mask.any():
            continue   # silently skip unknown IDs

        row = self.unique_df[mask].iloc[0]
        try:
            aspects = json.loads(row["aspects_sentiments"])
        except:
            aspects = {}

        all_aspect_names.update(aspects.keys())  # union of all aspect names

        pos_aspects = sorted(
            [{"name": a, "score": d["confidence"]}
             for a, d in aspects.items() if d.get("sentiment") == "Positive"],
            key=lambda x: x["score"], reverse=True
        )
        neg_aspects = sorted(
            [{"name": a, "score": d["confidence"]}
             for a, d in aspects.items() if d.get("sentiment") == "Negative"],
            key=lambda x: x["score"], reverse=True
        )

        products.append({
            "id": product_id,
            "name": str(row["itemName"]),
            "category": str(row["category"]),
            "image": str(row["image"]) if pd.notna(row.get("image")) else "",
            "all_aspects": aspects,
            "positive_aspects": pos_aspects[:4],
            "negative_aspects": neg_aspects[:2],
            "positive_count": len(pos_aspects),
            "negative_count": len(neg_aspects),
            "total_aspects": len(aspects)
        })

    # Build the aspect × product matrix.
    # Row = one aspect name; Columns = one cell per product.
    # Cell value = {"sentiment": "Positive"|"Negative"|"Neutral"|"N/A",
    #               "confidence": float}
    aspect_matrix = []
    for aspect in sorted(all_aspect_names):
        row_data = {"aspect": aspect}
        for i, product in enumerate(products):
            if aspect in product["all_aspects"]:
                d = product["all_aspects"][aspect]
                row_data[f"product_{i}"] = {
                    "sentiment": d.get("sentiment", "Neutral"),
                    "confidence": d.get("confidence", 0)
                }
            else:
                row_data[f"product_{i}"] = {"sentiment": "N/A", "confidence": 0}
        aspect_matrix.append(row_data)

    return self._sanitize_for_json({
        "products": products,
        "aspect_matrix": aspect_matrix,
        "comparison_count": len(products)
    })
```

---

### 21.10 `recommender.py` — Utility Helpers

```python
def _sanitize_for_json(self, obj):
    """
    Recursively converts NumPy types to Python native types.
    Without this, json.dumps() raises TypeError on np.int64, np.float32, etc.
    Also replaces NaN and Inf (invalid JSON) with 0.0.
    """
    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj): return 0.0
        return obj
    if isinstance(obj, dict):
        return {k: self._sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [self._sanitize_for_json(v) for v in obj]
    # NumPy integer types → Python int
    if isinstance(obj, (np.intc, np.intp, np.int8, np.int16, np.int32, np.int64,
                         np.uint8, np.uint16, np.uint32, np.uint64)):
        return int(obj)
    # NumPy float types → Python float (then recurse to catch NaN/Inf)
    if isinstance(obj, (np.float16, np.float32, np.float64)):
        return self._sanitize_for_json(float(obj))
    return obj   # str, bool, None pass through unchanged


def _infer_user_aspects(self, user_query):
    """Extract aspects from the user query and run ABSA on each."""
    aspects = self._extract_aspects_batch([user_query])[0]
    results = []
    for aspect in aspects:
        text = f"[CLS] {user_query} [SEP] {aspect} [SEP]"
        out = self.absa_pipe(text)[0]
        if out["score"] > 0.6:
            results.append((aspect, out["label"].capitalize(), out["score"]))
    return results   # list of (aspect_str, sentiment_str, confidence_float)


def _format_user_aspect_sentiment(self, query_aspects):
    user_aspects = {}
    for aspect, sentiment, confidence in query_aspects:
        polarity = ("positive" if sentiment.lower() == "positive"
                    else "negative" if sentiment.lower() == "negative"
                    else "neutral")
        user_aspects[aspect] = {
            "sentiment": sentiment,
            "polarity": polarity,
            "confidence": round(confidence, 3)
        }
    return user_aspects


def _compute_overall_sentiment(self, user_aspects):
    """Weighted average polarity across all query aspects."""
    if not user_aspects:
        return {"label": "Neutral", "confidence": 0.0}
    score = sum(
        v["confidence"] * (1 if v["polarity"] == "positive"
                           else -1 if v["polarity"] == "negative" else 0)
        for v in user_aspects.values()
    )
    total = sum(v["confidence"] for v in user_aspects.values())
    final = score / max(total, 1e-6)
    label = "Positive" if final > 0.2 else "Negative" if final < -0.2 else "Neutral"
    return {"label": label, "confidence": round(abs(final), 3)}


def analyze_text_only(self, text):
    """ABSA analysis without any DB write — used for live feedback preview."""
    aspects = self._extract_multi_aspects_single(text)
    return self._sanitize_for_json({
        k: {"sentiment": v["sentiment"], "confidence": round(v["confidence"], 2)}
        for k, v in aspects.items()
    })
```

---

### 21.11 `setup_offline.py` — Complete Source

Run **once** (with internet) to download all models to the local `models/` directory. After that, the system runs entirely offline.

```python
import os, shutil
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import spacy.cli, spacy

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "../models")


def setup_absa():
    print("--- Checking ABSA Model ---")
    absa_path = os.path.join(MODEL_DIR, "deberta-v3-base-absa")
    # config.json presence = valid saved model directory
    if os.path.exists(absa_path) and \
       os.path.exists(os.path.join(absa_path, "config.json")):
        print(f"ABSA model already at {absa_path}")
        return
    model_name = "yangheng/deberta-v3-base-absa-v1.1"
    try:
        # use_fast=False required for DeBERTa-v3 SentencePiece tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        tokenizer.save_pretrained(absa_path)   # saves vocab + tokenizer config
        model.save_pretrained(absa_path)       # saves weights + model config
        print("ABSA model saved.")
    except Exception as e:
        print(f"Failed: {e}")


def setup_sbert():
    print("--- Checking SBERT Model ---")
    sbert_path = os.path.join(MODEL_DIR, "all-MiniLM-L6-v2")
    if os.path.exists(sbert_path) and \
       os.path.exists(os.path.join(sbert_path, "config.json")):
        print("SBERT already installed.")
        return
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        model.save(sbert_path)   # saves in sentence-transformers format
        print("SBERT saved.")
    except Exception as e:
        print(f"Failed: {e}")


def setup_cross_encoder():
    print("--- Checking Cross-Encoder Model ---")
    ce_path = os.path.join(MODEL_DIR, "ms-marco-MiniLM-L-6-v2")
    if os.path.exists(ce_path) and \
       os.path.exists(os.path.join(ce_path, "config.json")):
        print("Cross-Encoder already installed.")
        return
    try:
        from sentence_transformers import CrossEncoder
        model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        model.save(ce_path)
        print("Cross-Encoder saved.")
    except Exception as e:
        print(f"Failed: {e}")


def setup_spacy():
    print("--- Checking Spacy Model ---")
    try:
        spacy.load("en_core_web_sm")  # raises OSError if not installed
        print("Spacy model already installed.")
    except OSError:
        try:
            spacy.cli.download("en_core_web_sm")
            print("Spacy model installed.")
        except Exception as e:
            print(f"Failed: {e}")


if __name__ == "__main__":
    os.makedirs(MODEL_DIR, exist_ok=True)
    setup_absa()          # ~700 MB — downloads DeBERTa-v3 ABSA
    setup_sbert()         # ~80 MB  — downloads all-MiniLM-L6-v2
    setup_cross_encoder() # ~80 MB  — downloads ms-marco cross-encoder
    setup_spacy()         # ~12 MB  — downloads spaCy en_core_web_sm
    print("Setup complete. Models ready for offline use.")
```

**Total download:** ~870 MB on first setup. All subsequent runs are fully offline.

---

*End of AspectMind Full Technical Report — March 19, 2026*
