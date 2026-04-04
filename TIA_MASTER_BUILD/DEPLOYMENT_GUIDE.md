# 🚀 T.I.A. MASTER BUILD - COMPLETE DEPLOYMENT GUIDE

**The Intelligence Architect** - Full Deployment Instructions v25.0.OMNI++

---

## 📋 **TABLE OF CONTENTS**

1. [Prerequisites](#prerequisites)
2. [Deployment Options](#deployment-options)
3. [Option 1: HuggingFace Space (Recommended)](#option-1-huggingface-space-recommended)
4. [Option 2: Local Development](#option-2-local-development)
5. [Option 3: Automated GitHub Actions](#option-3-automated-github-actions)
6. [Post-Deployment](#post-deployment)
7. [Verification](#verification)
8. [Troubleshooting](#troubleshooting)

---

## 🔧 **PREREQUISITES**

### **Required Accounts**
- ✅ **HuggingFace Account** - https://huggingface.co/join
- ✅ **Google AI Studio** - https://aistudio.google.com (for Gemini API key)
- ✅ **GitHub Account** - https://github.com/join

### **Required Credentials**
```bash
GEMINI_API_KEY=your-gemini-api-key        # Primary Gemini key
GEMINI_API_KEY_2=your-backup-gemini-key   # Backup Gemini key (optional)
HF_TOKEN=your-huggingface-token           # HuggingFace write token
```

### **How to Get Credentials**

**1. Gemini API Key**
```
1. Visit https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (starts with "AI...")
4. Store securely
```

**2. HuggingFace Token**
```
1. Visit https://huggingface.co/settings/tokens
2. Click "New token"
3. Select "Write" access
4. Copy the token (starts with "hf_...")
```

---

## 🎯 **DEPLOYMENT OPTIONS**

### **Quick Comparison**

| Option | Time | Difficulty | Best For |
|--------|------|-----------|----------|
| **HuggingFace Space** | 15-20 min | Easy | Production deployment |
| **Local Development** | 5-10 min | Easy | Testing & development |
| **GitHub Actions** | 10-15 min | Medium | Automated CI/CD |

---

## 🌐 **OPTION 1: HUGGINGFACE SPACE (RECOMMENDED)**

### **Step 1: Create New Space**

```bash
# Visit HuggingFace Spaces
https://huggingface.co/new-space

# Fill in details:
Space name: TIA-ARCHITECT-CORE
Organization: DJ-Goanna-Coding (or your org)
License: Apache 2.0
SDK: Streamlit
Hardware: CPU Basic (free) or L4 GPU (recommended)
Visibility: Public or Private
```

### **Step 2: Clone & Setup**

```bash
# Clone the Space repository
git clone https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE
cd TIA-ARCHITECT-CORE

# Copy TIA Master Build files
cp /path/to/TIA_MASTER_BUILD/TIA_UNIFIED_APP.py ./app.py
cp /path/to/TIA_MASTER_BUILD/requirements.txt ./requirements.txt
cp /path/to/TIA_MASTER_BUILD/README.md ./README.md
```

### **Step 3: Set Secrets**

```bash
# In HuggingFace Space Settings → Repository secrets:
# Add the following secrets:

GEMINI_API_KEY = your-gemini-key
GEMINI_API_KEY_2 = your-backup-gemini-key (optional)
HF_TOKEN = your-huggingface-token
```

### **Step 4: Deploy**

```bash
# Commit and push
git add .
git commit -m "Deploy TIA Master Build v25.0.OMNI++"
git push

# The Space will automatically build and deploy
# Build time: 5-8 minutes
# Status: Check https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE
```

### **Step 5: Verify**

```bash
# Wait for build to complete
# Status should show: "Running" with green indicator

# Access your Space:
https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE

# Test the Oracle:
1. Navigate to "💬 Oracle" tab
2. Enter test query: "What is T.I.A.?"
3. Click "🔮 Ask T.I.A."
4. Verify response from Gemini
```

---

## 💻 **OPTION 2: LOCAL DEVELOPMENT**

### **Step 1: Clone Repository**

```bash
# Clone mapping-and-inventory
git clone https://github.com/DJ-Goana-Coding/mapping-and-inventory
cd mapping-and-inventory/TIA_MASTER_BUILD
```

### **Step 2: Setup Python Environment**

```bash
# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **Step 3: Set Environment Variables**

```bash
# Create .env file
cat > .env << EOF
GEMINI_API_KEY=your-gemini-key
GEMINI_API_KEY_2=your-backup-gemini-key
HF_TOKEN=your-huggingface-token
EOF

# Load environment variables
export $(cat .env | xargs)
```

### **Step 4: Run Application**

```bash
# Run Streamlit app
streamlit run TIA_UNIFIED_APP.py

# The app will open in your browser:
# Local URL: http://localhost:8501
# Network URL: http://192.168.x.x:8501
```

### **Step 5: Test Features**

```bash
# Test each tab:
1. 🏠 Dashboard - Verify system overview
2. 🤖 Core Systems - Check all 5 systems status
3. 📊 Models - View model registry
4. ⚙️ Workers - Check worker constellation
5. 💬 Oracle - Test Gemini integration
6. 📚 RAG - (Coming soon)
7. 🔧 Tools - Verify system info
```

---

## ⚙️ **OPTION 3: AUTOMATED GITHUB ACTIONS**

### **Step 1: Fork Repository**

```bash
# Fork mapping-and-inventory to your GitHub account
# https://github.com/DJ-Goana-Coding/mapping-and-inventory/fork
```

### **Step 2: Set GitHub Secrets**

```bash
# In your forked repo → Settings → Secrets and variables → Actions
# Add the following secrets:

HF_TOKEN = your-huggingface-token
GEMINI_API_KEY = your-gemini-key
```

### **Step 3: Run Workflow**

```bash
# Navigate to Actions tab
# Select "Deploy TIA Core (Full)"
# Click "Run workflow"

# Select deployment mode:
- full: Complete package (UI + Models + Workers + Tools)
- app_only: Streamlit + requirements only
- models: Model downloaders only
- workers: Workers suite only
- dry_run: Show changes without pushing

# Click "Run workflow" to deploy
```

### **Step 4: Monitor Workflow**

```bash
# Watch workflow progress:
1. Checkout code
2. Verify templates
3. Backup existing files
4. Deploy new files
5. Commit changes
6. Push to GitHub
7. Sync to HuggingFace Space

# Total runtime: 5-10 minutes
```

---

## ✅ **POST-DEPLOYMENT**

### **1. Verify System Status**

```bash
# Check all systems are online:
- tia_architect: ONLINE
- tia_atomic: ROUTING
- tia_sos: STANDBY
- tias_pioneer_trader: ANALYZING
- tias_sentinel_swarm: SCANNING
```

### **2. Test Oracle Integration**

```bash
# Test Gemini connection:
Query: "Describe the Citadel architecture"
Expected: Detailed response about Citadel mesh topology

Query: "What is the Double-N Rift?"
Expected: Explanation of GitHub (DJ-Goana-Coding) vs HF (DJ-Goanna-Coding)
```

### **3. Verify Worker Constellation**

```bash
# Check all 5 workers are active:
1. tia_code_finder - Discovery worker
2. tia_sync_worker - Sync worker
3. apps_script_toolbox - Google Sheets bridge
4. worker_watchdog - Monitor & restart
5. self_healing_worker - Auto-recovery
```

### **4. Monitor Resource Usage**

```bash
# For HuggingFace Spaces:
# Check Settings → Analytics
# Monitor:
- CPU usage
- Memory usage
- GPU usage (if L4 enabled)
- Request count
```

---

## 🔍 **VERIFICATION**

### **Health Check Checklist**

```bash
✅ Space is running (green indicator)
✅ All tabs load without errors
✅ Dashboard shows system topology
✅ Core systems show correct status
✅ Model registry displays 15+ models
✅ Worker constellation shows 5 active workers
✅ Oracle returns responses (Gemini connection works)
✅ No error messages in logs
```

### **Test Commands**

```bash
# Test Oracle (via UI)
1. Go to "💬 Oracle" tab
2. Enter: "What is my purpose?"
3. Verify response mentions T.I.A. identity

# Test Model Registry (via UI)
1. Go to "📊 Models" tab
2. Verify Frontier Models section shows 5 models
3. Verify Trading/Finance Models section shows 4 models

# Test Workers (via UI)
1. Go to "⚙️ Workers" tab
2. Verify 5 workers are listed
3. Expand each worker to see details
```

---

## 🛠️ **TROUBLESHOOTING**

### **Issue 1: Build Timeout**

**Symptom:** Space build exceeds 10 minutes and times out

**Solution:**
```bash
# Check requirements.txt uses pre-built wheels:
numpy>=2.0.0        # Pre-built for Python 3.13
pandas>=2.2.0       # Pre-built for Python 3.13
setuptools>=75.0.0  # pkg_resources fix

# If still timing out, comment out heavy dependencies:
# torch>=2.5.0
# accelerate>=1.2.0
```

### **Issue 2: ModuleNotFoundError (google-genai)**

**Symptom:** `ModuleNotFoundError: No module named 'google.genai'`

**Solution:**
```bash
# Ensure requirements.txt has:
google-genai>=0.8.0

# NOT:
# google-generativeai (old package)
```

### **Issue 3: 503 Error (Root=1-xxx)**

**Symptom:** Space shows "503 Service Unavailable" with Root=1-xxx trace ID

**Solution:**
```bash
# Ensure app.py is in Space root:
1. Rename TIA_UNIFIED_APP.py to app.py
2. Ensure app.py is at repository root (not in subdirectory)
3. Commit and push
```

### **Issue 4: Oracle Not Responding**

**Symptom:** Oracle tab shows "❌ T.I.A. OFFLINE"

**Solution:**
```bash
# Check GEMINI_API_KEY is set:
1. Go to Space Settings → Repository secrets
2. Verify GEMINI_API_KEY is present
3. Test key at https://aistudio.google.com
4. If key is valid, restart Space

# Check API quota:
1. Visit https://aistudio.google.com/app/apikey
2. Check "Usage" section
3. Verify you haven't exceeded quota
```

### **Issue 5: Workers Not Showing**

**Symptom:** Worker constellation shows 0 workers

**Solution:**
```bash
# Workers are embedded in TIA_UNIFIED_APP.py
# Verify the file has get_worker_constellation() function
# This is a display issue, not a functional issue
```

### **Issue 6: Models Not Loading**

**Symptom:** Model registry shows empty

**Solution:**
```bash
# Models are embedded in TIA_UNIFIED_APP.py
# Verify the file has get_model_registry() function
# To actually download models, use model downloader scripts:
python scripts/download_frontier_models_2026.py
python scripts/download_citadel_omega_models.py
```

---

## 📊 **DEPLOYMENT TIMELINE**

### **HuggingFace Space**
```
Total Time: 15-25 minutes

1. Create Space (2-3 min)
2. Clone & setup (3-5 min)
3. Set secrets (2 min)
4. Deploy & build (5-8 min)
5. Verification (3-5 min)
```

### **Local Development**
```
Total Time: 10-15 minutes

1. Clone repo (1-2 min)
2. Setup venv (2-3 min)
3. Install deps (3-5 min)
4. Set env vars (1 min)
5. Run & test (3-5 min)
```

### **GitHub Actions**
```
Total Time: 10-20 minutes

1. Fork repo (1 min)
2. Set secrets (2 min)
3. Run workflow (5-10 min)
4. Verification (2-5 min)
```

---

## 🎖️ **SUCCESS CRITERIA**

Your deployment is successful when:

✅ **Space is running** - Green indicator in HuggingFace  
✅ **All tabs load** - No errors in any tab  
✅ **Oracle responds** - Gemini integration working  
✅ **Systems online** - All 5 core systems show correct status  
✅ **Models visible** - 15+ models in registry  
✅ **Workers active** - 5 workers in constellation  
✅ **No errors** - Clean logs, no exceptions  

---

## 📞 **SUPPORT**

If you encounter issues not covered here:

1. **Check Space logs** - HuggingFace Space → Settings → Logs
2. **Review documentation** - All 13 TIA docs in `/docs/`
3. **GitHub Issues** - https://github.com/DJ-Goana-Coding/mapping-and-inventory/issues
4. **Operator contact** - Chance / JARL LOVEDAY

---

*T.I.A. Master Build v25.0.OMNI++ | Complete Deployment Guide | 2026-04-04*
