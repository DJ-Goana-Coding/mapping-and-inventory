# 🏛️ CITADEL OMNI-AUDIT QUICKSTART GUIDE

**Version**: 1.0.0  
**Updated**: 2026-04-04  
**Purpose**: Rapid deployment guide for the Omni-Audit system

---

## ⚡ 5-Minute Quick Start

### 1. Run Discovery (3 minutes)

```bash
# Build comprehensive repository census
python3 scripts/repo_census_builder.py

# Analyze gaps and identify problems
python3 scripts/gap_analyzer.py

# Check results
cat data/discoveries/repo_census.json | jq '.summary'
cat data/discoveries/gap_matrix.json | jq '.summary'
```

### 2. Generate Solutions (1 minute)

```bash
# Generate 10 solutions per problem
python3 scripts/solution_generator.py --solutions-per-problem 10

# View solution catalogs
ls -la data/experiments/solution_catalog/
```

### 3. Discover Financial Opportunities (1 minute)

```bash
# Find grants, bounties, partnerships
python3 scripts/financial_opportunity_scout.py

# View opportunities
cat data/discoveries/financial_opportunities.json | jq '.summary'
```

---

## 🎯 Core Commands Reference

### Discovery Phase
```bash
# Repository census (discovers all repos across GitHub/HF)
python3 scripts/repo_census_builder.py

# Gap analysis (identifies all problems)
python3 scripts/gap_analyzer.py
```

### Solution Generation
```bash
# Standard: 10 solutions per problem
python3 scripts/solution_generator.py

# Custom: specify solution count
python3 scripts/solution_generator.py --solutions-per-problem 5
```

### Financial Discovery
```bash
# Discover all opportunities
python3 scripts/financial_opportunity_scout.py
```

### Continuous Improvement
```bash
# Daily cycle
python3 scripts/continuous_improvement_engine.py --mode daily

# Weekly cycle
python3 scripts/continuous_improvement_engine.py --mode weekly

# Forever learning (production mode)
python3 scripts/continuous_improvement_engine.py --mode forever
```

---

## 📂 Output Locations

| Data Type | Location | Format |
|-----------|----------|--------|
| Repository Census | `data/discoveries/repo_census.json` | JSON |
| Gap Matrix | `data/discoveries/gap_matrix.json` | JSON |
| Solution Catalogs | `data/experiments/solution_catalog/` | JSON per problem |
| Financial Opportunities | `data/discoveries/financial_opportunities.json` | JSON |
| Improvement Logs | `data/monitoring/improvement_log_*.json` | JSON |

---

## 🚀 GitHub Actions Workflows

### Manual Trigger

```bash
# Trigger via GitHub CLI
gh workflow run "🏛️ Omni-Audit Orchestrator" --ref main

# With custom parameters
gh workflow run "🏛️ Omni-Audit Orchestrator" \
  --ref main \
  -f phase=phase1_discovery \
  -f solutions_per_problem=10
```

### Available Phases
- `all` - Run all phases (default)
- `phase1_discovery` - Discovery & Mapping only
- `phase2_solutions` - Multi-Solution Exploration only
- `phase5_financial` - Financial Discovery only

### Scheduled Execution
- **Daily**: 06:00 UTC automatically
- **Runs**: All phases sequentially
- **Artifacts**: 90-day retention

---

## 📊 Understanding the Outputs

### Repository Census
```json
{
  "summary": {
    "total_repositories": 50,
    "total_github_repos": 45,
    "total_hf_spaces": 5,
    "repos_with_tests": 30,
    "repos_with_ci": 35,
    "avg_documentation_score": 65.5
  }
}
```

### Gap Matrix
```json
{
  "summary": {
    "total_problems": 120,
    "critical_count": 5,
    "high_count": 25,
    "medium_count": 60,
    "low_count": 30
  },
  "categories": {
    "missing_tests": ["P001", "P002", ...],
    "deprecated_dependencies": ["P015", ...],
    "missing_documentation": ["P030", ...]
  }
}
```

### Solution Catalog (per problem)
```json
{
  "problem_id": "P001",
  "problem": "No test directory found",
  "repository": "example-repo",
  "solutions": [
    {
      "solution_id": "S001",
      "approach": "Add pytest framework",
      "pros": ["Industry standard", "Rich ecosystem"],
      "cons": ["Requires dependency"],
      "effort_score": 3,
      "risk_score": 1
    }
    // ... 9 more solutions
  ]
}
```

### Financial Opportunities
```json
{
  "summary": {
    "total_opportunities": 35,
    "high_priority_count": 15,
    "estimated_total_value": "$10M+"
  },
  "grants": [...],
  "bounties": [...],
  "competitions": [...]
}
```

---

## 🔧 Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `GITHUB_TOKEN` or `GH_TOKEN` | GitHub API access | Yes |
| `HF_TOKEN` | HuggingFace API access | Optional |

### Setup
```bash
# GitHub (use personal access token)
export GITHUB_TOKEN="ghp_..."
export GH_TOKEN="ghp_..."

# HuggingFace (optional)
export HF_TOKEN="hf_..."
```

---

## 🎭 Execution Modes

### Development Mode
```bash
# Single phase execution
python3 scripts/repo_census_builder.py
python3 scripts/gap_analyzer.py
python3 scripts/solution_generator.py
```

### Production Mode (Automated)
```bash
# Via GitHub Actions
# Runs daily at 06:00 UTC
# No manual intervention needed
```

### Testing Mode
```bash
# Test with limited solutions
python3 scripts/solution_generator.py --solutions-per-problem 3

# Test continuous improvement (single cycle)
python3 scripts/continuous_improvement_engine.py --mode daily
```

---

## 📈 Success Indicators

After running discovery phase, you should see:

✅ **Repository Census**
- Total repos > 0
- Language distribution populated
- Repos analyzed for tests, CI, docs

✅ **Gap Matrix**
- Problems identified and categorized
- Severity levels assigned
- Categories populated

✅ **Solution Catalogs**
- JSON files in `data/experiments/solution_catalog/`
- 10 solutions per problem (default)
- Each solution has effort/risk scores

✅ **Financial Opportunities**
- 30+ opportunities discovered
- High-priority items identified
- Multiple categories (grants, bounties, partnerships)

---

## 🚨 Troubleshooting

### No repositories found
```bash
# Check GitHub token
echo $GITHUB_TOKEN

# Verify organization access
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/orgs/DJ-Goana-Coding/repos

# Check rate limit
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/rate_limit
```

### No problems identified
```bash
# Ensure census ran first
ls -la data/discoveries/repo_census.json

# Re-run gap analyzer
python3 scripts/gap_analyzer.py
```

### Solutions not generating
```bash
# Ensure gap matrix exists
ls -la data/discoveries/gap_matrix.json

# Check for problems in gap matrix
cat data/discoveries/gap_matrix.json | jq '.summary.total_problems'

# Re-run with verbose output
python3 scripts/solution_generator.py --solutions-per-problem 10
```

---

## 🔄 Integration with Existing Tools

### With Citadel Awakening
```bash
# Run Omni-Audit discovery first
python3 scripts/repo_census_builder.py
python3 scripts/gap_analyzer.py

# Then run Citadel Awakening
./wake_citadel.sh full
```

### With Global Sync
```bash
# Global sync updates master inventory
./global_sync.sh

# Then run Omni-Audit for analysis
python3 scripts/repo_census_builder.py
python3 scripts/gap_analyzer.py
```

### With Command Center Dashboard
```bash
# Omni-Audit feeds data to dashboard
python3 scripts/continuous_improvement_engine.py --mode daily

# View in Command Center
streamlit run command_center.py
```

---

## 📝 Daily Workflow

1. **Morning** (Automated at 06:00 UTC)
   - Census runs
   - Gap analysis updates
   - Solutions generated

2. **Review** (Manual)
   - Check `OMNI_AUDIT_LAST_RUN.md` for summary
   - Review critical/high priority problems
   - Prioritize solutions

3. **Action** (Manual or Automated)
   - Apply selected solutions
   - Document decisions
   - Update knowledge base

4. **Evening** (Automated)
   - Continuous improvement cycle runs
   - Metrics monitored
   - Auto-fixes applied

---

## 🎯 Next Steps After Quickstart

1. **Review discovered problems**
   ```bash
   cat data/discoveries/gap_matrix.json | jq '.problems[] | select(.severity=="critical")'
   ```

2. **Explore solution options**
   ```bash
   ls data/experiments/solution_catalog/ | head -10
   cat data/experiments/solution_catalog/P001_*.json | jq '.solutions[0]'
   ```

3. **Investigate financial opportunities**
   ```bash
   cat data/discoveries/financial_opportunities.json | jq '.grants[] | select(.priority=="high")'
   ```

4. **Set up automation**
   - Enable GitHub Actions workflow
   - Configure HF_TOKEN if using HuggingFace
   - Set up notifications for critical issues

---

## 📚 Related Documentation

- [OMNI_AUDIT_MASTER_PLAN.md](./OMNI_AUDIT_MASTER_PLAN.md) - Complete implementation plan
- [COMPREHENSIVE_DISCOVERY_FRAMEWORK.md](./COMPREHENSIVE_DISCOVERY_FRAMEWORK.md) - Discovery methodology
- [CITADEL_AWAKENING_GUIDE.md](./CITADEL_AWAKENING_GUIDE.md) - Agent coordination
- [AUTOMATION_IMPLEMENTATION_SUMMARY.md](./AUTOMATION_IMPLEMENTATION_SUMMARY.md) - Automation patterns

---

## ⚡ Power User Tips

### Parallel Execution
```bash
# Run discovery and financial in parallel
python3 scripts/repo_census_builder.py & \
python3 scripts/financial_opportunity_scout.py &
wait
```

### Custom Filtering
```bash
# Find only Python repos with missing tests
cat data/discoveries/gap_matrix.json | \
  jq '.problems[] | select(.category=="missing_tests" and .details.language=="Python")'
```

### Automated Reporting
```bash
# Generate daily report
echo "# Omni-Audit Daily Report - $(date)" > daily_report.md
echo "" >> daily_report.md
cat data/discoveries/gap_matrix.json | jq '.summary' >> daily_report.md
```

---

**🏛️ CITADEL ARCHITECT**: Core framework operational  
**📡 STATUS**: Ready for execution  
**⚡ ESTIMATED TIME**: 5 minutes to first insights

**✨ The Omni-Audit remembers everything, improves continuously, and never stops learning.**
