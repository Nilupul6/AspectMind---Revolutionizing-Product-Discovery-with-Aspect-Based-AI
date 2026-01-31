import os
import gc
import json
import torch
import numpy as np
import pandas as pd
from tqdm import tqdm
import spacy
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.neighbors import NearestNeighbors
import joblib
import threading
import time

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
EMB_DIR = os.path.join(BASE_DIR, "../embeddings")
MODEL_DIR = os.path.join(BASE_DIR, "../models")

class ProductRecommender:

    def __init__(
        self,
        dataframe_name="Second_fixed_image_urls.csv",
        max_dataset_size=200000,
        absa_chunk_size=400,
        absa_batch_size=16,
        top_n=10
    ):
        torch.set_grad_enabled(False)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # On CPU, intra-op parallelism can sometimes slow things down if too high? 
        # But usually defaults are fine.
        print(f"📦 Device: {self.device.upper()}")
        
        # Caching paths
        self.dataframe_name = dataframe_name
        self.cache_path = os.path.join(DATA_DIR, f"{dataframe_name}_processed.pkl")

        self.absa_chunk_size = absa_chunk_size
        self.absa_batch_size = absa_batch_size
        self.top_n = top_n
        self.max_dataset_size = max_dataset_size

        self.dataframe_path = os.path.join(DATA_DIR, dataframe_name)
        self.emb_path = os.path.join(EMB_DIR, "enriched_item_descriptions_embeddings.npy")
        self.knn_path = os.path.join(EMB_DIR, "knn_model.pkl") 
        self.absa_model_path = os.path.join(MODEL_DIR, "deberta-v3-base-absa")

        print("Loading Data...")
        self.df_original = pd.read_csv(self.dataframe_path)
        
        print("Loading Models...")
        self._load_models()

        print("Preparing Data & Index...")
        self.df = self._prepare_data()
        self._prepare_embeddings_and_index()
        print("Initialization Complete.")

    def _load_data_cache(self):
        if os.path.exists(self.cache_path):
            print(f"⚡ Loading cached processed data from {self.cache_path}...")
            try:
                return pd.read_pickle(self.cache_path)
            except Exception as e:
                print(f"⚠️ Failed to load cache: {e}. Reloading from CSV.")
        return None

    def _save_data_cache(self, df):
        print(f"💾 Saving processed data to {self.cache_path}...")
        try:
            df.to_pickle(self.cache_path)
        except Exception as e:
            print(f"⚠️ Failed to save cache: {e}")

    def _load_models(self):
        # --- LOAD SPACE ---
        try:
            print("Loading Spacy...")
            self.nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
        except OSError:
            print("Downloading spacy model...")
            from spacy.cli import download
            download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
        
        # --- LOAD SBERT ---
        print("Loading SBERT...")
        sbert_path = os.path.join(MODEL_DIR, "all-MiniLM-L6-v2")
        if os.path.exists(sbert_path):
            print(f"Loading local SBERT from {sbert_path}...")
            self.sbert = SentenceTransformer(sbert_path, device=self.device)
        else:
            print(f"⚠️ Local SBERT not found at {sbert_path}. Attempting download (will fail if offline)...")
            self.sbert = SentenceTransformer(
                "all-MiniLM-L6-v2",
                device=self.device
            )
            
        # --- LOAD CROSS ENCODER ---
        print("Loading Cross-Encoder...")
        ce_path = os.path.join(MODEL_DIR, "ms-marco-MiniLM-L-6-v2")
        if os.path.exists(ce_path):
             self.cross_encoder = CrossEncoder(ce_path, device=self.device)
        else:
             print("⚠️ Local Cross-Encoder not found. Downloading...")
             self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device=self.device)
        
        # Quantize for CPU speedup
        if self.device == "cpu":
            print("🏎️  Quantizing Cross-Encoder for CPU...")
            try:
                # Quantize the underlying transformer model (usually DistilBert or similar)
                # qint8 quantization for Linear layers provides ~2x speedup on CPU
                self.cross_encoder.model = torch.quantization.quantize_dynamic(
                    self.cross_encoder.model, {torch.nn.Linear}, dtype=torch.qint8
                )
            except Exception as e:
                print(f"⚠️ Failed to quantize model: {e}")
        # --- LOAD ABSA ---
        print(f"Loading ABSA model from {self.absa_model_path}...")
        try:
            if os.path.exists(self.absa_model_path):
                print("Loading Tokenizer...")
                # FORCE use_fast=False to avoid convert_slow_tokenizer error with DebertaV3
                tokenizer = AutoTokenizer.from_pretrained(self.absa_model_path, use_fast=False)
                
                print("Loading Model...")
                model = AutoModelForSequenceClassification.from_pretrained(
                    self.absa_model_path
                )
                model.to(self.device)
            else:
                raise FileNotFoundError("Local model path does not exist.")
        except Exception as e:
            print(f"⚠️ Failed to load local ABSA model: {e}")
            print("Attempting to download default ABSA model from HuggingFace (requires internet)...")
            model_name = "yangheng/deberta-v3-base-absa-v1.1" 
            # FORCE use_fast=False here as well
            tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
            model = AutoModelForSequenceClassification.from_pretrained(model_name).to(self.device)

        self.absa_pipe = pipeline(
            "text-classification",
            model=model,
            tokenizer=tokenizer,
            truncation=True,
            device=0 if self.device == "cuda" else -1
        )
        print("Models Loaded.")

    def _extract_aspects_batch(self, texts):
        aspects_list = []
        for doc in self.nlp.pipe(texts, batch_size=128):
            aspects = []
            for chunk in doc.noun_chunks:
                a = chunk.text.lower().strip()
                if len(a) > 2 and a not in {"it", "this", "that", "product", "item"}:
                    aspects.append(a)
            aspects_list.append(list(set(aspects))[:3] or ["general"])
        return aspects_list

    def _extract_multi_aspects_single(self, text, threshold=0.6, max_aspects=None):
        aspects = self._extract_aspects_batch([text])[0]
        
        # Limit aspects for faster processing (especially for feedback)
        if max_aspects and len(aspects) > max_aspects:
            aspects = aspects[:max_aspects]
        
        results = {}
        inputs, meta = [], []
        for aspect in aspects:
            inputs.append(f"[CLS] {text} [SEP] {aspect} [SEP]")
            meta.append(aspect)
        if not inputs: return {}

        with torch.no_grad():
             outputs = self.absa_pipe(inputs)
        
        for aspect, out in zip(meta, outputs):
            if out["score"] > threshold:
                 results[aspect] = {
                    "sentiment": out["label"].capitalize(),
                    "confidence": out["score"]
                }
        return results

    def _extract_multi_aspects(self, reviews):
        results = []
        for i in tqdm(range(0, len(reviews), self.absa_chunk_size), desc="🔍 ABSA"):
            batch_reviews = reviews[i:i + self.absa_chunk_size]
            batch_aspects = self._extract_aspects_batch(batch_reviews)

            texts, meta = [], []
            for review, aspects in zip(batch_reviews, batch_aspects):
                for aspect in aspects:
                    texts.append(f"[CLS] {review} [SEP] {aspect} [SEP]")
                    meta.append((review, aspect))
            
            if not texts:
                results.extend([{"general": {"sentiment": "Neutral", "confidence": 0.0}}] * len(batch_reviews))
                continue

            with torch.inference_mode(): 
                outputs = self.absa_pipe(texts, batch_size=self.absa_batch_size)

            review_map = {}
            for (review, aspect), out in zip(meta, outputs):
                review_map.setdefault(review, {})
                if out["score"] > 0.6:
                    review_map[review][aspect] = {
                        "sentiment": out["label"].capitalize(),
                        "confidence": out["score"]
                    }

            for review in batch_reviews:
                results.append(
                    review_map.get(
                        review,
                        {"general": {"sentiment": "Neutral", "confidence": 0.0}}
                    )
                )

            gc.collect()
            if self.device == "cuda":
                torch.cuda.empty_cache()
        return results

    def _prepare_data(self):
        # 1. Try cache
        cached_df = self._load_data_cache()
        if cached_df is not None:
            return cached_df

        # 2. Process from scratch
        df = self.df_original.copy()
        if "reviewText" in df.columns:
            df = df[df["reviewText"].astype(str).str.len() > 15]
        df = df.head(self.max_dataset_size).reset_index(drop=True)
        
        for col in ["description", "feature"]:
            if col not in df.columns: df[col] = ""
            else: df[col] = df[col].fillna("")

        df["item_unique_id"] = (
            df["itemName"].astype(str) + df["category"].astype(str) + 
            df["description"] + df["feature"]
        )

        if "aspects_sentiments" not in df.columns:
            print("Extracting aspects (this may take a while)...")
            aspects = self._extract_multi_aspects(df["reviewText"].tolist())
            df["aspects_sentiments"] = [json.dumps(x) for x in aspects]
        
        # 3. Save Cache
        self._save_data_cache(df)
        return df

    def _prepare_embeddings_and_index(self):
        def enrich(row):
            try: aspects = json.loads(row["aspects_sentiments"])
            except: aspects = {}
            return " ".join(f"{a} {v['sentiment']}" for a, v in aspects.items() if v["confidence"] > 0.6)

        self.df["enriched_text"] = (
            self.df["itemName"].astype(str) + " " + self.df["category"].astype(str) + " " +
            self.df["description"].astype(str) + " " + self.df["feature"].astype(str) + " " +
            self.df.apply(enrich, axis=1)
        )

        unique_df = self.df.drop_duplicates("item_unique_id")
        self.item_ids = unique_df["item_unique_id"].tolist()
        self.unique_df = unique_df 

        if os.path.exists(self.emb_path):
            embeddings = np.load(self.emb_path)
            if len(embeddings) != len(unique_df):
                print("Embeddings mismatch. Recomputing...")
                embeddings = None
        else: embeddings = None

        if embeddings is None:
            print("Creating new embeddings...")
            texts = unique_df["enriched_text"].tolist()
            embeddings = self.sbert.encode(texts, batch_size=64, show_progress_bar=True, convert_to_numpy=True)
            np.save(self.emb_path, embeddings)

        if os.path.exists(self.knn_path):
            print("Loading KNN model...")
            self.knn_index = joblib.load(self.knn_path)
        else:
            print("Building KNN index...")
            self.knn_index = NearestNeighbors(n_neighbors=50, metric='cosine', algorithm='auto')
            self.knn_index.fit(embeddings)
            joblib.dump(self.knn_index, self.knn_path)

    def recommend(self, user_query, top_n_results=10, category_filter=None, min_sentiment_score=None, sort_by="relevance"):
        # 1. Analyze Query
        query_aspects = self._infer_user_aspects(user_query)
        user_comment_analysis = self._format_user_aspect_sentiment(query_aspects)
        overall_sentiment = self._compute_overall_sentiment(user_comment_analysis)
        
        # 2. Semantic Search (Fetch more candidates to allow reranking)
        query_emb = self.sbert.encode(user_query, convert_to_numpy=True).reshape(1, -1)
        # Fetch 3x candidates to allow for re-ranking filtering (Optimized from 5x for speed)
        distances, indices = self.knn_index.kneighbors(query_emb, n_neighbors=min(top_n_results * 3, len(self.item_ids)))

        candidates = []
        query_aspect_names = set(qa[0] for qa in query_aspects)

        for idx, dist in zip(indices[0], distances[0]):
            if idx >= len(self.item_ids): continue
            item_id = self.item_ids[idx]
            row = self.unique_df[self.unique_df["item_unique_id"] == item_id].iloc[0]
            
            # Apply category filter
            if category_filter and str(row["category"]).lower() != category_filter.lower():
                continue
            
            try: aspects = json.loads(row["aspects_sentiments"])
            except: aspects = {}

            # 3. Calculate Boost
            # Boost if product has a query aspect as POSITIVE
            boost = 0.0
            for qa_name in query_aspect_names:
                if qa_name in aspects:
                    attr = aspects[qa_name]
                    if attr.get("sentiment") == "Positive":
                        boost += 0.15 # Boost for positive match
                    elif attr.get("sentiment") == "Negative":
                        boost -= 0.05 # Slight penalty if negative match to query aspect
            
            # Calculate sentiment score for filtering
            pos_count = sum(1 for v in aspects.values() if v.get("sentiment") == "Positive")
            neg_count = sum(1 for v in aspects.values() if v.get("sentiment") == "Negative")
            total_aspects = len(aspects) if len(aspects) > 0 else 1
            sentiment_score = (pos_count - neg_count) / total_aspects
            
            # Apply sentiment filter
            if min_sentiment_score is not None and sentiment_score < min_sentiment_score:
                continue
            
            # Base semantic score + boost
            final_score = float(1 - dist) + boost

            candidates.append({
                "id": item_id,
                "name": row["itemName"],
                "category": row["category"],
                "image": str(row["image"]) if pd.notna(row.get("image")) else "",
                "score": final_score,
                "sentiment_score": sentiment_score,
                "aspects": aspects, # Raw aspects from DB
                "row_ref": row, # temp ref for fallback
                "text_for_ce": str(row["itemName"]) + " " + str(row["description"]) # Text for Cross-Encoder
            })

        # 4. Re-Ranking with Cross-Encoder (Accuracy Boost)
        # Re-rank strictly the top 50 (or whatever we fetched)
        # Cross-Encoder takes pairs: [(query, doc1), (query, doc2), ...]
        if candidates:
            # We only re-rank the candidates we have safely retrieved
            ce_pairs = [[user_query, c["text_for_ce"]] for c in candidates]
            ce_scores = self.cross_encoder.predict(ce_pairs)
            
            # Combine scores. 
            # CE score is usually logits (unbounded) or 0-1 (if sigmoid). ms-marco are logits.
            # Simple approach: Replace score with CE score, or weighted sum.
            # Since CE is much better, we normally trust it primarily for ranking.
            # But we keep the boost logic from before as a tie-breaker or penalty?
            # Actually, let's trust CE for the base rank, apply aspect boost on top of normalized CE score.
            
            # Normalize CE scores roughly to 0-1 for safer boosting
            # Sigmoid: 1 / (1 + exp(-x))
            import math
            def sigmoid(x): return 1 / (1 + math.exp(-x))
            
            for i, c in enumerate(candidates):
                base_score = sigmoid(ce_scores[i])
                
                # Re-apply aspect boost (from previous step, it was mixed in final_score)
                # We need to recalculate boost or extract it.
                # Let's just recalculate to be clean.
                boost = 0.0
                query_aspect_names = set(qa[0] for qa in query_aspects)
                for qa_name in query_aspect_names:
                    if qa_name in c["aspects"]:
                        attr = c["aspects"][qa_name]
                        if attr.get("sentiment") == "Positive":
                            boost += 0.1 # Slightly lower boost since CE is smart
                        elif attr.get("sentiment") == "Negative":
                            boost -= 0.1

                c["score"] = base_score + boost

        # 5. Sort based on sort_by parameter
        if sort_by == "sentiment":
            candidates.sort(key=lambda x: x["sentiment_score"], reverse=True)
        elif sort_by == "name":
            candidates.sort(key=lambda x: x["name"].lower())
        else:  # default: relevance
            candidates.sort(key=lambda x: x["score"], reverse=True)
            
        final_recs = candidates[:top_n_results]

        # 5. Enrich Top-N (Fallback for UI) & Build Explanations
        results = []
        for rec in final_recs:
            aspects = rec["aspects"]
            row = rec["row_ref"]
            
            # --- FALLBACK EXTRACTION (Optimized: Only runs on Top N) ---
            has_pos = any(v.get("sentiment") == "Positive" for v in aspects.values())
            has_neg = any(v.get("sentiment") == "Negative" for v in aspects.values())

            if not has_pos or not has_neg:
                context_text = str(row.get("reviewText", ""))
                if len(context_text) < 20: 
                    context_text = f"{row['itemName']} {row['category']} {row['description']}"
                
                # Run on-the-fly extraction 
                fresh_aspects = self._extract_multi_aspects_single(context_text[:1000], threshold=0.1)
                for k, v in fresh_aspects.items():
                    if k not in aspects: aspects[k] = v
            # -----------------------------------------------------------
            
            # Separate Pos and Neg
            pos_list = []
            neg_list = []
            
            for a, v in aspects.items():
                s = v.get("sentiment", "Neutral")
                c = v.get("confidence", 0)
                if s == "Positive":
                    pos_list.append({"name": a, "score": c})
                elif s == "Negative":
                    neg_list.append({"name": a, "score": c})
            
            # Sort by confidence
            pos_list.sort(key=lambda x: x["score"], reverse=True)
            neg_list.sort(key=lambda x: x["score"], reverse=True)
            
            top_4_pos = pos_list[:4]
            top_2_neg = neg_list[:2]
            
            # Matched reasons
            matched = [a for a in query_aspect_names if a in aspects and aspects[a].get("sentiment") == "Positive"]
            
            results.append({
                "product": rec["name"],
                "matched_aspects": matched,
                "top_pos_aspects": top_4_pos,
                "top_neg_aspects": top_2_neg,
                "reason": f"Winner for: {', '.join(matched)}" if matched else "Highly recommended.",
                "all_aspects": aspects 
            })

        # Clean up internal refs before returning
        for rec in final_recs:
             if "row_ref" in rec: del rec["row_ref"]

        # Get available categories for filtering
        available_categories = sorted(list(set(self.unique_df["category"].astype(str).unique())))

        return self._sanitize_for_json({
            "query_analysis": user_comment_analysis,
            "overall_sentiment": overall_sentiment,
            "results": results,
            "raw_recs": final_recs,
            "available_categories": available_categories
        })
    
    
    def add_feedback(self, product_id, feedback_text):
        start_time = time.time()
        
        # Optimize: Limit to 3 aspects max and use higher threshold for speed
        t1 = time.time()
        new_aspects = self._extract_multi_aspects_single(
            feedback_text, 
            threshold=0.7,  # Higher threshold = fewer, more confident aspects = faster
            max_aspects=3   # Limit to 3 aspects max for speed
        )
        absa_time = (time.time() - t1) * 1000
        print(f"⏱️  ABSA analysis took: {absa_time:.0f}ms")
        
        if not new_aspects: 
            return {
                "status": "mid", 
                "message": "No specific aspects confidently found, but recorded.", 
                "feedback_analysis": {}
            }

        mask = self.unique_df["item_unique_id"] == product_id
        if not mask.any(): return {"status": "error", "message": "Product not found"}
        
        idx = self.unique_df.index[mask][0]
        current_data = self.unique_df.at[idx, "aspects_sentiments"]
        try: current_aspects = json.loads(current_data)
        except: current_aspects = {}
        
        # Merge new aspects (simple overwrite/update for now)
        for k, v in new_aspects.items(): 
            current_aspects[k] = v
            
        # Update in-memory data immediately
        t2 = time.time()
        updated_aspects_json = json.dumps(current_aspects)
        self.unique_df.at[idx, "aspects_sentiments"] = updated_aspects_json
        
        # Update the main dataframe as well
        df_mask = self.df["item_unique_id"] == product_id
        if df_mask.any():
            self.df.loc[df_mask, "aspects_sentiments"] = updated_aspects_json
        
        memory_time = (time.time() - t2) * 1000
        print(f"⏱️  Memory update took: {memory_time:.0f}ms")
        
        # Save EVERYTHING in background thread (NOTHING blocks the response)
        def save_all_background():
            bg_start = time.time()
            # Save to cache file
            try:
                self._save_data_cache(self.df)
                cache_time = (time.time() - bg_start) * 1000
                print(f"✅ Feedback persisted to cache for product: {product_id} ({cache_time:.0f}ms)")
            except Exception as e:
                print(f"⚠️ Failed to save cache after feedback: {e}")
            
            # Save to CSV file
            csv_start = time.time()
            try:
                # Ensure item_unique_id exists in df_original
                if "item_unique_id" not in self.df_original.columns:
                    for col in ["description", "feature"]:
                        if col not in self.df_original.columns: 
                            self.df_original[col] = ""
                        else: 
                            self.df_original[col] = self.df_original[col].fillna("")
                    
                    self.df_original["item_unique_id"] = (
                        self.df_original["itemName"].astype(str) + 
                        self.df_original["category"].astype(str) + 
                        self.df_original["description"] + 
                        self.df_original["feature"]
                    )
                
                # Update the original dataframe
                csv_mask = self.df_original["item_unique_id"] == product_id
                if csv_mask.any():
                    self.df_original.loc[csv_mask, "aspects_sentiments"] = updated_aspects_json
                    self.df_original.to_csv(self.dataframe_path, index=False)
                    csv_time = (time.time() - csv_start) * 1000
                    print(f"✅ Feedback persisted to CSV for product: {product_id} ({csv_time:.0f}ms)")
            except Exception as e:
                print(f"⚠️ Failed to save CSV after feedback: {e}")
        
        # Start background thread for ALL saves (completely non-blocking)
        save_thread = threading.Thread(target=save_all_background, daemon=True)
        save_thread.start()
        
        # Format analysis for frontend
        analysis_formatted = {}
        for k, v in new_aspects.items():
            analysis_formatted[k] = {"sentiment": v["sentiment"], "confidence": round(v["confidence"], 2)}

        total_time = (time.time() - start_time) * 1000
        print(f"🚀 Total feedback response time: {total_time:.0f}ms (ABSA: {absa_time:.0f}ms, Memory: {memory_time:.0f}ms)")
        
        # Return IMMEDIATELY - no waiting for any file I/O
        return self._sanitize_for_json({
            "status": "success", 
            "message": "Feedback analyzed and product updated.", 
            "feedback_analysis": analysis_formatted
        })

    def analyze_text_only(self, text):
        """Analyzes text and returns aspect sentiment without saving."""
        aspects = self._extract_multi_aspects_single(text)
        analysis_formatted = {}
        for k, v in aspects.items():
            analysis_formatted[k] = {"sentiment": v["sentiment"], "confidence": round(v["confidence"], 2)}
        return self._sanitize_for_json(analysis_formatted)
    
    # Utils (Helpers)
    def _sanitize_for_json(self, obj):
        if isinstance(obj, float):
            if np.isnan(obj) or np.isinf(obj): return 0.0
            return obj
        if isinstance(obj, dict): return {k: self._sanitize_for_json(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)): return [self._sanitize_for_json(v) for v in obj]
        
        # NumPy 2.0 safe checks (removed np.int_ and np.float_)
        if isinstance(obj, (np.intc, np.intp, np.int8,
            np.int16, np.int32, np.int64, np.uint8,
            np.uint16, np.uint32, np.uint64)): return int(obj)
            
        if isinstance(obj, (np.float16, np.float32, np.float64)):
            return self._sanitize_for_json(float(obj))
            
        return obj

    def _format_user_aspect_sentiment(self, query_aspects):
        user_aspects = {}
        for aspect, sentiment, confidence in query_aspects:
            polarity = "positive" if sentiment.lower() == "positive" else "negative" if sentiment.lower() == "negative" else "neutral"
            user_aspects[aspect] = {"sentiment": sentiment, "polarity": polarity, "confidence": round(confidence, 3)}
        return user_aspects

    def _compute_overall_sentiment(self, user_aspects):
        if not user_aspects: return {"label": "Neutral", "confidence": 0.0}
        score = sum(v["confidence"] * (1 if v["polarity"]=="positive" else -1 if v["polarity"]=="negative" else 0) for v in user_aspects.values())
        total = sum(v["confidence"] for v in user_aspects.values())
        final = score / max(total, 1e-6)
        label = "Positive" if final > 0.2 else "Negative" if final < -0.2 else "Neutral"
        return {"label": label, "confidence": round(abs(final), 3)}

    def _build_recommendation_explanations(self, user_aspects, recommendations):
        explanations = []
        positive_aspects = {a for a, v in user_aspects.items() if v["polarity"] == "positive"}
        for rec in recommendations:
            row = self.unique_df[self.unique_df["item_unique_id"] == rec["id"]].iloc[0]
            try: aspects = json.loads(row["aspects_sentiments"])
            except: aspects = {}
            matched = [a for a in positive_aspects if a in aspects and aspects[a]["sentiment"] == "Positive"]
            top_product = [a for a, v in aspects.items() if v["sentiment"] == "Positive"]
            explanations.append({
                "product": rec["name"], "matched_aspects": matched,
                "top_product_aspects": top_product[:5], "all_aspects": aspects,
                "reason": f"Positively reviewed for: {', '.join(matched)}" if matched else "Recommended result."
            })
        return explanations

    def _infer_user_aspects(self, user_query):
        aspects = self._extract_aspects_batch([user_query])[0]
        results = []
        for aspect in aspects:
            text = f"[CLS] {user_query} [SEP] {aspect} [SEP]"
            out = self.absa_pipe(text)[0]
            if out["score"] > 0.6: results.append((aspect, out["label"].capitalize(), out["score"]))
        return results
    
    def get_analytics(self):
        """Generate analytics data for dashboard"""
        # Analyze all products for insights
        all_aspects = {}
        sentiment_distribution = {"Positive": 0, "Negative": 0, "Neutral": 0}
        category_stats = {}
        
        for idx, row in self.unique_df.iterrows():
            try:
                aspects = json.loads(row["aspects_sentiments"])
            except:
                aspects = {}
            
            # Count aspects
            for aspect, data in aspects.items():
                if aspect not in all_aspects:
                    all_aspects[aspect] = {"positive": 0, "negative": 0, "neutral": 0, "total": 0}
                
                sentiment = data.get("sentiment", "Neutral")
                all_aspects[aspect][sentiment.lower()] += 1
                all_aspects[aspect]["total"] += 1
                sentiment_distribution[sentiment] += 1
            
            # Category stats
            category = str(row.get("category", "Unknown"))
            if category not in category_stats:
                category_stats[category] = {"count": 0, "positive": 0, "negative": 0}
            category_stats[category]["count"] += 1
            
            # Count positive/negative aspects per category
            for aspect, data in aspects.items():
                if data.get("sentiment") == "Positive":
                    category_stats[category]["positive"] += 1
                elif data.get("sentiment") == "Negative":
                    category_stats[category]["negative"] += 1
        
        # Top aspects by frequency
        top_aspects = sorted(
            [{"name": k, **v} for k, v in all_aspects.items()],
            key=lambda x: x["total"],
            reverse=True
        )[:15]
        
        # Top categories
        top_categories = sorted(
            [{"name": k, **v} for k, v in category_stats.items()],
            key=lambda x: x["count"],
            reverse=True
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
    
    def compare_products(self, product_ids):
        """Compare multiple products side-by-side"""
        if not product_ids or len(product_ids) < 2:
            return {"error": "At least 2 products required for comparison"}
        
        if len(product_ids) > 4:
            return {"error": "Maximum 4 products can be compared at once"}
        
        products = []
        all_aspect_names = set()
        
        for product_id in product_ids:
            mask = self.unique_df["item_unique_id"] == product_id
            if not mask.any():
                continue
            
            row = self.unique_df[mask].iloc[0]
            try:
                aspects = json.loads(row["aspects_sentiments"])
            except:
                aspects = {}
            
            # Collect all aspect names
            all_aspect_names.update(aspects.keys())
            
            # Separate positive and negative
            pos_aspects = []
            neg_aspects = []
            
            for aspect, data in aspects.items():
                sentiment = data.get("sentiment", "Neutral")
                confidence = data.get("confidence", 0)
                
                if sentiment == "Positive":
                    pos_aspects.append({"name": aspect, "score": confidence})
                elif sentiment == "Negative":
                    neg_aspects.append({"name": aspect, "score": confidence})
            
            pos_aspects.sort(key=lambda x: x["score"], reverse=True)
            neg_aspects.sort(key=lambda x: x["score"], reverse=True)
            
            # Limit to top 4 positive and top 2 negative for consistency
            top_4_pos = pos_aspects[:4]
            top_2_neg = neg_aspects[:2]
            
            products.append({
                "id": product_id,
                "name": str(row["itemName"]),
                "category": str(row["category"]),
                "image": str(row["image"]) if pd.notna(row.get("image")) else "",
                "all_aspects": aspects,
                "positive_aspects": top_4_pos,
                "negative_aspects": top_2_neg,
                "positive_count": len(pos_aspects),
                "negative_count": len(neg_aspects),
                "total_aspects": len(aspects)
            })
        
        # Create aspect comparison matrix
        aspect_matrix = []
        for aspect in sorted(all_aspect_names):
            row_data = {"aspect": aspect}
            for i, product in enumerate(products):
                if aspect in product["all_aspects"]:
                    data = product["all_aspects"][aspect]
                    row_data[f"product_{i}"] = {
                        "sentiment": data.get("sentiment", "Neutral"),
                        "confidence": data.get("confidence", 0)
                    }
                else:
                    row_data[f"product_{i}"] = {
                        "sentiment": "N/A",
                        "confidence": 0
                    }
            aspect_matrix.append(row_data)
        
        return self._sanitize_for_json({
            "products": products,
            "aspect_matrix": aspect_matrix,
            "comparison_count": len(products)
        })

