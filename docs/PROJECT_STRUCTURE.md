# 📁 Project Structure - Clean & Organized

## ✅ Current Structure (After Cleanup)

```
requirments/
│
├── 📄 README.md                    # Main project documentation
├── 📄 .gitignore                   # Git ignore rules
├── 📄 start_app.bat                # Quick start script (Windows)
├── 📄 fixed_image_urls.csv         # Root CSV (reference data)
│
├── 📁 client/                      # Frontend React Application
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── 📁 server/                      # Backend FastAPI Server
│   ├── main.py                     # Server entry point
│   ├── recommender.py              # Core recommendation engine
│   └── requirements.txt
│
├── 📁 data/                        # Dataset Files
│   ├── Second_fixed_image_urls.csv              # Main dataset (134K rows)
│   └── Second_fixed_image_urls.csv_processed.pkl # Cache file
│
├── 📁 models/                      # Pre-trained ML Models
│   ├── all-MiniLM-L6-v2/          # Semantic search model
│   ├── ms-marco-MiniLM-L-6-v2/    # Cross-encoder model
│   └── deberta-v3-base-absa/      # Sentiment analysis model
│
├── 📁 embeddings/                  # Cached Embeddings
│   ├── enriched_item_descriptions_embeddings.npy
│   └── knn_model.pkl
│
├── 📁 scripts/                     # Utility Scripts ⭐
│   ├── quick_check.py              # Fast data health check
│   ├── diagnose_images.py          # Full diagnostic tool
│   ├── repair_images_fixed.py      # Image URL repair tool
│   └── test_data_loading.py        # Server compatibility test
│
├── 📁 docs/                        # Documentation 📚
│   ├── QUICK_START.md              # Quick start guide
│   ├── FEATURES_IMPLEMENTED.md     # Feature documentation
│   ├── README_IMAGE_FIX.md         # Image troubleshooting
│   └── IMAGE_FIX_SUMMARY.md        # Technical details
│
└── 📁 archive/                     # Old/Debug Files (Safe to Ignore)
    ├── check_*.py                  # Old check scripts
    ├── compare_*.py                # Old compare scripts
    ├── repair_images.py            # Old buggy repair script
    └── *.txt                       # Debug output files
```

## 📊 Directory Breakdown

### Essential Directories (Keep)

| Directory | Purpose | Size | Important |
|-----------|---------|------|-----------|
| `client/` | Frontend React app | ~50 MB | ✅ Yes |
| `server/` | Backend FastAPI server | ~10 KB | ✅ Yes |
| `data/` | Dataset files | ~750 MB | ✅ Yes |
| `models/` | ML models | ~500 MB | ✅ Yes |
| `embeddings/` | Cached embeddings | ~200 MB | ✅ Yes |
| `scripts/` | Utility tools | ~15 KB | ✅ Yes |
| `docs/` | Documentation | ~25 KB | ✅ Yes |

### Archive Directory (Safe to Delete)

| Directory | Purpose | Safe to Delete |
|-----------|---------|----------------|
| `archive/` | Old debug files | ✅ Yes (after backup) |

## 🎯 Key Files

### Root Level
- **README.md** - Main project documentation
- **.gitignore** - Git ignore rules
- **start_app.bat** - Quick start script
- **fixed_image_urls.csv** - Reference data (318 MB)

### Scripts (Most Used)
- **scripts/quick_check.py** - Run before starting server
- **scripts/diagnose_images.py** - Full data analysis
- **scripts/repair_images_fixed.py** - Fix image URLs
- **scripts/test_data_loading.py** - Test server compatibility

### Documentation
- **docs/QUICK_START.md** - How to get started
- **docs/FEATURES_IMPLEMENTED.md** - What the system can do
- **docs/README_IMAGE_FIX.md** - Troubleshooting guide

## 🧹 What Was Cleaned Up

### Moved to `archive/` (32 files)
- ✅ All `check_*.py` debug scripts (11 files)
- ✅ All `compare_*.py` scripts (2 files)
- ✅ Old `repair_images.py` (buggy version)
- ✅ All `.txt` output files (9 files)
- ✅ Debug scripts: `verify_root_urls.py`, `inspect_csv.py`, etc.
- ✅ Old logs and temporary files

### Organized into `scripts/` (4 files)
- ✅ `quick_check.py` - Essential health check
- ✅ `diagnose_images.py` - Diagnostic tool
- ✅ `repair_images_fixed.py` - Fixed repair script
- ✅ `test_data_loading.py` - Server test

### Organized into `docs/` (4 files)
- ✅ All `.md` documentation files
- ✅ Feature lists and guides
- ✅ Troubleshooting documentation

## 📏 Size Summary

```
Total Project Size: ~1.5 GB

Breakdown:
- Data files (.csv, .pkl):    ~750 MB (50%)
- Models:                     ~500 MB (33%)
- Embeddings:                 ~200 MB (13%)
- Client (node_modules):      ~50 MB  (3%)
- Code & Docs:                ~1 MB   (1%)
```

## 🚀 Quick Commands

### Daily Use
```bash
# Check data health
python scripts/quick_check.py

# Start backend
cd server && python main.py

# Start frontend (new terminal)
cd client && npm run dev
```

### Maintenance
```bash
# Full diagnostic
python scripts/diagnose_images.py

# Repair data
python scripts/repair_images_fixed.py

# Test server
python scripts/test_data_loading.py
```

## ⚠️ Important Notes

### DO Keep
- ✅ `client/`, `server/`, `data/`, `models/`, `embeddings/`
- ✅ `scripts/` and `docs/` folders
- ✅ `README.md` and `.gitignore`

### Can Delete (After Backup)
- ⚠️ `archive/` folder (old debug files)
- ⚠️ `fixed_image_urls.csv` (if you have backup)

### Never Delete
- ❌ `data/Second_fixed_image_urls.csv` (main dataset)
- ❌ `models/` folder (ML models)
- ❌ `embeddings/` folder (cached embeddings)
- ❌ `server/` and `client/` folders

## 🎨 Clean Structure Benefits

1. **Easy Navigation** - Clear folder structure
2. **Quick Access** - Essential scripts in `scripts/`
3. **Good Documentation** - All docs in `docs/`
4. **No Clutter** - Debug files archived
5. **Git Ready** - Proper `.gitignore` in place
6. **Professional** - Clean, organized structure

## 📝 Next Steps

1. ✅ Structure is clean and organized
2. ✅ All essential files are in place
3. ✅ Documentation is complete
4. ✅ Scripts are organized
5. ✅ Ready for development/deployment

---

**Status**: ✅ Clean & Organized
**Files Moved**: 32 to archive
**New Folders**: scripts/, docs/, archive/
**Total Root Files**: 4 (down from 42)
**Structure**: Professional & Maintainable
