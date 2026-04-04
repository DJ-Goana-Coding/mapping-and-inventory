# 🚀 PERSONAL ARCHIVE OMNIVAC - QUICKSTART GUIDE

Complete setup and execution guide for harvesting your entire digital life.

---

## 📋 Prerequisites

### Required:
- Python 3.11+
- Git
- 8+ GB disk space (initial), up to 1TB for full archive

### API Credentials Needed:
1. **Gmail API** (OAuth2): https://console.cloud.google.com/
2. **Yahoo Mail API**: https://developer.yahoo.com/apps/
3. **Google Gemini API**: https://makersuite.google.com/
4. **OpenAI API** (optional): https://platform.openai.com/
5. **Anthropic Claude API** (optional): https://console.anthropic.com/
6. **HuggingFace Token**: https://huggingface.co/settings/tokens

### Optional (for full RAG):
- `pip install sentence-transformers faiss-cpu`

---

## ⚡ Quick Start (5 Minutes)

### 1. Clone Repository
```bash
git clone https://github.com/DJ-Goana-Coding/mapping-and-inventory.git
cd mapping-and-inventory
```

### 2. Install Dependencies
```bash
pip install requests beautifulsoup4
# Optional for RAG:
# pip install sentence-transformers faiss-cpu
```

### 3. Run Demo (Mock Data)
```bash
# This will generate mock data for all phases
python scripts/personal_archive_orchestrator.py --phase all
```

### 4. Check Results
```bash
ls -la data/personal_archive/
# View summaries
cat data/personal_archive/emails/harvest_summary.json
cat data/personal_archive/browser_history/laptop_summary.json
cat data/personal_archive/ai_chats/ai_chats_summary.json
```

---

## 🔧 Full Setup (30 Minutes)

### Step 1: Setup Email Access

#### Gmail (OAuth2):
1. Go to https://console.cloud.google.com/
2. Create new project: "Personal Archive"
3. Enable Gmail API
4. Create OAuth2 credentials (Desktop app)
5. Download `credentials.json`
6. Set environment variable:
```bash
export GMAIL_CREDENTIALS_FILE=/path/to/credentials.json
```

#### Yahoo Mail:
1. Go to https://developer.yahoo.com/apps/
2. Create new app
3. Get Client ID and Secret
4. Set environment variables:
```bash
export YAHOO_CLIENT_ID=your_client_id
export YAHOO_CLIENT_SECRET=your_secret
```

#### IMAP (Custom Domains):
```bash
# Format: {EMAIL_ADDRESS}_PASSWORD (replace @ and . with _)
export OCEANIC105_CARPKINGDOM_COM_PASSWORD=your_password
export GRUFFDAY_ALTMAIL_KR_PASSWORD=your_password
export HIPPY_CARPKINGDOM_COM_PASSWORD=your_password
```

### Step 2: Setup AI Platform Access

```bash
# Google Gemini
export GEMINI_API_KEY=your_gemini_key

# OpenAI (optional)
export OPENAI_API_KEY=your_openai_key

# Anthropic Claude (optional)
export ANTHROPIC_API_KEY=your_anthropic_key
```

### Step 3: Run Full Harvest

```bash
# Harvest all data
python scripts/personal_archive_orchestrator.py --phase all
```

Or run phases individually:

```bash
# Phase 1: Data harvesting
python scripts/personal_archive_orchestrator.py --phase harvest

# Phase 2: RAG ingestion
python scripts/personal_archive_orchestrator.py --phase rag

# Phase 3: Tech stack research
python scripts/personal_archive_orchestrator.py --phase tech
```

---

## 📦 Running Individual Components

### Email Harvester
```bash
python scripts/email_archive_harvester.py
```

### Browser History Vacuum
```bash
python scripts/browser_history_vacuum.py
```

### AI Chat Extractor
```bash
python scripts/ai_chat_extractor.py
```

### Device Scanner
```bash
python scripts/device_account_scanner.py
```

### RAG Ingestion
```bash
python scripts/personal_archive_rag_ingest.py
```

### Tech Stack Shopper
```bash
python scripts/tech_stack_shopper.py
```

---

## 🤖 GitHub Actions Automation

### Setup Secrets

In your GitHub repository:

1. Go to Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `GMAIL_CREDENTIALS_FILE` (base64 encoded)
   - `YAHOO_CLIENT_ID`
   - `YAHOO_CLIENT_SECRET`
   - `GEMINI_API_KEY`
   - `OPENAI_API_KEY` (optional)
   - `ANTHROPIC_API_KEY` (optional)
   - `HF_TOKEN` (for HuggingFace deployment)

### Manual Trigger

1. Go to Actions tab
2. Select "Personal Archive Omnivac Harvester"
3. Click "Run workflow"
4. Choose phase (all, harvest, rag, tech)
5. Click "Run workflow"

### Automatic Schedule

The workflow runs automatically every day at 6 AM UTC.

---

## 📊 Understanding Output

### Directory Structure
```
data/personal_archive/
├── emails/
│   ├── gmail/
│   │   ├── chanceroofing/
│   │   │   ├── metadata.json
│   │   │   ├── threads/
│   │   │   └── attachments/
│   │   └── ...
│   ├── yahoo/
│   └── custom_domains/
├── browser_history/
│   ├── laptop/
│   │   ├── chrome/
│   │   └── firefox/
│   └── unified_timeline.json
├── ai_chats/
│   ├── gemini/
│   ├── copilot/
│   ├── chatgpt/
│   └── claude/
├── devices/
│   ├── laptop/
│   └── unified_account_registry.json
├── rag_store/
│   ├── vectors/
│   ├── indices/
│   └── metadata/
└── tech_stack/
    ├── bill_of_materials.json
    └── shopping_summary.json
```

### Key Files

1. **`harvest_summary.json`** - Email harvest statistics
2. **`laptop_summary.json`** - Browser history summary
3. **`ai_chats_summary.json`** - AI conversations summary
4. **`scan_results.json`** - Device scan results
5. **`ingestion_summary.json`** - RAG ingestion stats
6. **`bill_of_materials.json`** - Tech stack recommendations
7. **`orchestration_results.json`** - Master execution report

---

## 🔍 Searching Your Archive

### Start RAG Search API
```bash
cd data/personal_archive/rag_store
python search_api.py
```

Or with uvicorn:
```bash
uvicorn search_api:app --reload --host 0.0.0.0 --port 8000
```

### Search Queries
```bash
# Semantic search
curl "http://localhost:8000/search?q=trading%20bots&limit=10"

# Entity listing
curl "http://localhost:8000/entities"
```

---

## 🌐 Website Deployment

### 1. Generate Next.js Project
```bash
npx create-next-app@latest personal-portfolio \
  --typescript \
  --tailwind \
  --app \
  --no-src-dir
cd personal-portfolio
```

### 2. Install UI Libraries
```bash
npm install @radix-ui/react-* framer-motion
npx shadcn-ui@latest init
```

### 3. Add Components
```bash
npx shadcn-ui@latest add button card input
```

### 4. Deploy to Vercel
```bash
npm install -g vercel
vercel login
vercel --prod
```

---

## 💰 Infrastructure Costs

Based on Tech Stack Shopper BOM:

| Category | Service | Monthly Cost |
|----------|---------|--------------|
| Database | Supabase + Redis | $32 |
| Hosting | Vercel + Railway + Cloudflare | $40 |
| GPU | HuggingFace Spaces (L4) | $150 (avg) |
| Monitoring | Sentry + Analytics | $26 |
| **TOTAL** | | **$248/month** |

### Budget Utilization
- Available: $700-1,200/month (from retrieved funds)
- Used: $248/month (35% of budget)
- Remaining: $452-952/month for scaling

---

## 🔧 Troubleshooting

### Email Harvesting Fails
- **Error**: "GMAIL_CREDENTIALS_FILE not set"
- **Fix**: Export environment variable with path to credentials.json

### Browser History Empty
- **Error**: Database not found
- **Fix**: Check browser paths in script, may need platform-specific adjustments

### RAG Ingestion Slow
- **Error**: Timeout during embedding generation
- **Fix**: Install `sentence-transformers` or use mock embeddings

### API Rate Limits
- **Error**: 429 Too Many Requests
- **Fix**: Scripts include rate limiting, but may need adjustment

---

## 📞 Support

### Documentation
- Full protocol: `PERSONAL_ARCHIVE_OMNIVAC_PROTOCOL.md`
- Tech stack: `data/personal_archive/tech_stack/shopping_summary.json`

### Issues
- Check GitHub Issues
- Review orchestration logs
- Examine individual component outputs

---

## ✅ Success Checklist

- [ ] Python 3.11+ installed
- [ ] API credentials configured
- [ ] Environment variables set
- [ ] Ran orchestrator successfully
- [ ] Checked output directories
- [ ] Reviewed summary files
- [ ] RAG ingestion completed
- [ ] Tech stack researched
- [ ] Website plan created
- [ ] Ready for deployment

---

**Status**: 🟢 READY TO EXECUTE

**Generated**: 2026-04-04T04:03:00Z  
**Version**: 1.0  
**Protocol**: Personal Archive Omnivac
