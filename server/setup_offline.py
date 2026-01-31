import os
import shutil
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import spacy.cli
import spacy

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "../models")

def setup_absa():
    print("\n--- Checking ABSA Model ---")
    absa_path = os.path.join(MODEL_DIR, "deberta-v3-base-absa")
    # Check for a key file like config.json to confirm it exists and is populated
    if os.path.exists(absa_path) and os.path.exists(os.path.join(absa_path, "config.json")):
        print(f"✅ ABSA model found at {absa_path}")
    else:
        print(f"⬇️ Downloading ABSA model to {absa_path}...")
        model_name = "yangheng/deberta-v3-base-absa-v1.1"
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            tokenizer.save_pretrained(absa_path)
            model.save_pretrained(absa_path)
            print("✅ ABSA model saved.")
        except Exception as e:
            print(f"❌ Failed to download ABSA model: {e}")

def setup_sbert():
    print("\n--- Checking SBERT Model ---")
    sbert_path = os.path.join(MODEL_DIR, "all-MiniLM-L6-v2")
    if os.path.exists(sbert_path) and os.path.exists(os.path.join(sbert_path, "config.json")):
        print(f"✅ SBERT model found at {sbert_path}")
    else:
        print(f"⬇️ Downloading SBERT model to {sbert_path}...")
        try:
            model = SentenceTransformer("all-MiniLM-L6-v2")
            model.save(sbert_path)
            print("✅ SBERT model saved.")
        except Exception as e:
             print(f"❌ Failed to download SBERT model: {e}")

def setup_spacy():
    print("\n--- Checking Spacy Model ---")
    try:
        spacy.load("en_core_web_sm")
        print("✅ Spacy model 'en_core_web_sm' is already installed.")
    except OSError:
        print("⬇️ Downloading Spacy model 'en_core_web_sm'...")
        try:
            spacy.cli.download("en_core_web_sm")
            print("✅ Spacy model installed.")
        except Exception as e:
            print(f"❌ Failed to download Spacy model: {e}")


def setup_cross_encoder():
    print("\n--- Checking Cross-Encoder Model ---")
    ce_path = os.path.join(MODEL_DIR, "ms-marco-MiniLM-L-6-v2")
    if os.path.exists(ce_path) and os.path.exists(os.path.join(ce_path, "config.json")):
        print(f"✅ Cross-Encoder model found at {ce_path}")
    else:
        print(f"⬇️ Downloading Cross-Encoder model to {ce_path}...")
        try:
            # We use CrossEncoder from sentence_transformers, but for saving/loading offline 
            # we can just use the automodel logic or the library's save functions.
            # Easiest is to use the library's wrapper if possible, but AutoModel is more generic.
            # CrossEncoder in sbert loads via automodel locally.
            from sentence_transformers import CrossEncoder
            model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            model.save(ce_path)
            print("✅ Cross-Encoder model saved.")
        except Exception as e:
             print(f"❌ Failed to download Cross-Encoder model: {e}")

if __name__ == "__main__":
    os.makedirs(MODEL_DIR, exist_ok=True)
    setup_absa()
    setup_sbert()
    setup_cross_encoder()
    setup_spacy()
    print("\n🎉 Setup complete. Models are ready for offline use.")
