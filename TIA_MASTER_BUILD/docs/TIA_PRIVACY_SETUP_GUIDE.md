# 🔒 TIA-ARCHITECT-CORE PRIVACY CONFIGURATION GUIDE

**Authority:** Citadel Architect v25.0.OMNI+  
**Priority:** Sovereign Level  
**Estimated Time:** 5-10 minutes

---

## 🎯 OBJECTIVE

Make the TIA-ARCHITECT-CORE repository private to protect sovereign intelligence systems while maintaining integration with mapping-and-inventory and HuggingFace Space.

---

## ⚡ QUICK START (Choose One Method)

### Method 1: GitHub Web UI (Easiest - 2 minutes)

1. **Navigate to Repository Settings**
   ```
   https://github.com/DJ-Goana-Coding/TIA-ARCHITECT-CORE/settings
   ```

2. **Scroll to "Danger Zone"**
   - Located at the bottom of the settings page
   - Look for red warning area

3. **Change Visibility**
   - Click "Change visibility" button
   - Select "Make private"
   - Enter repository name to confirm: `TIA-ARCHITECT-CORE`
   - Click "I understand, make this repository private"

4. **Verify**
   ```
   🔒 Repository should now show a "Private" badge
   ```

---

### Method 2: GitHub CLI (Fastest - 30 seconds)

```bash
# Make repository private
gh repo edit DJ-Goana-Coding/TIA-ARCHITECT-CORE --visibility private

# Verify
gh repo view DJ-Goana-Coding/TIA-ARCHITECT-CORE --json isPrivate
```

**Expected Output:**
```json
{
  "isPrivate": true
}
```

---

### Method 3: GitHub API (Automated - 1 minute)

```bash
# Set GITHUB_TOKEN
export GITHUB_TOKEN="your_github_token_here"

# Make repository private
curl -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/DJ-Goana-Coding/TIA-ARCHITECT-CORE \
  -d '{"private": true}'
```

**Expected Response:**
```json
{
  "name": "TIA-ARCHITECT-CORE",
  "private": true,
  ...
}
```

---

## 🔧 POST-CONFIGURATION REQUIREMENTS

After making the repository private, update the following:

### 1. GitHub Secrets (Required)

Private repos require authentication for cloning and syncing.

**In mapping-and-inventory repository:**
```
Settings → Secrets and variables → Actions → Repository secrets
```

Ensure these secrets exist:
- ✅ `GITHUB_TOKEN` - For private repo access
- ✅ `HF_TOKEN` - For HuggingFace Space deployment

### 2. HuggingFace Space Access (Required)

**In TIA-ARCHITECT-CORE HuggingFace Space:**
```
https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE/settings
```

Add secret:
- `GITHUB_TOKEN` - For pulling from private GitHub repo

**Configure Space to Pull from Private Repo:**

Update Space README.md or add to Space settings:
```yaml
---
title: TIA-ARCHITECT-CORE
sdk: docker
app_port: 7860
secrets:
  - GITHUB_TOKEN
  - GEMINI_API_KEY
  - RCLONE_CONFIG_DATA
---
```

### 3. Update Workflows (Automatic)

The bridge workflow (`global_repo_bridge.yml`) already handles private repos:
```yaml
- uses: actions/checkout@v4
  with:
    token: ${{ secrets.GITHUB_TOKEN }}  # ✅ Handles private repos
```

No changes needed! The workflow will automatically use GITHUB_TOKEN for authentication.

### 4. Update Clone URLs (If Manual)

**Before (Public):**
```bash
git clone https://github.com/DJ-Goana-Coding/TIA-ARCHITECT-CORE.git
```

**After (Private):**
```bash
# Option 1: SSH (Recommended)
git clone git@github.com:DJ-Goana-Coding/TIA-ARCHITECT-CORE.git

# Option 2: HTTPS with Token
git clone https://${GITHUB_TOKEN}@github.com/DJ-Goana-Coding/TIA-ARCHITECT-CORE.git
```

---

## ✅ VERIFICATION CHECKLIST

After making repository private, verify:

- [ ] Repository shows 🔒 "Private" badge on GitHub
- [ ] You can still clone the repository with authentication
- [ ] GitHub Actions workflows in mapping-and-inventory still work
- [ ] HuggingFace Space can still sync from GitHub
- [ ] Bridge workflow discovers and includes TIA-ARCHITECT-CORE
- [ ] Global sync works with private repo

### Test Commands:

```bash
# 1. Check repo visibility
gh repo view DJ-Goana-Coding/TIA-ARCHITECT-CORE --json isPrivate

# 2. Test clone (should require auth)
git clone https://github.com/DJ-Goana-Coding/TIA-ARCHITECT-CORE.git

# 3. Test bridge discovery
cd mapping-and-inventory
python scripts/discover_all_repos.py

# 4. Check registry includes TIA-ARCHITECT-CORE
cat repo_bridge_registry.json | jq '.repositories[] | select(.name=="TIA-ARCHITECT-CORE")'
```

---

## 🛡️ SECURITY CONSIDERATIONS

### Access Control

**Private Repository Benefits:**
- ✅ Code not publicly visible
- ✅ Protects sovereign intelligence architecture
- ✅ Requires authentication for all access
- ✅ Full audit trail of access

**Collaboration:**
- Collaborators must be added explicitly
- Team members need direct repository access
- Workflows use organization secrets for authentication

### HuggingFace Space Visibility

**Important:** Making GitHub repo private does NOT make HuggingFace Space private.

To make HuggingFace Space private:
```
https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE/settings

Scroll to "Visibility" section
Select: "Private"
Save changes
```

**Note:** Private HF Spaces require Pro subscription or organization plan.

---

## 🔄 MAINTAINING SYNC WITH PRIVATE REPO

### GitHub Actions Authentication

Workflows automatically use `GITHUB_TOKEN` for private repos:

```yaml
- name: Clone Private Repo
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    git clone https://${GITHUB_TOKEN}@github.com/DJ-Goana-Coding/TIA-ARCHITECT-CORE.git
```

### HuggingFace Space Pull

Add startup script to Space:
```bash
#!/bin/bash
# pull_from_github.sh

if [ -n "$GITHUB_TOKEN" ]; then
  git clone https://${GITHUB_TOKEN}@github.com/DJ-Goana-Coding/TIA-ARCHITECT-CORE.git /tmp/tia
  # Sync files as needed
else
  echo "⚠️  GITHUB_TOKEN not set - cannot pull from private repo"
fi
```

---

## 🚨 TROUBLESHOOTING

### Problem: "Repository not found" when cloning
**Solution:** 
- Verify you have access to the repository
- Use SSH keys or GITHUB_TOKEN for authentication
- Check organization membership

### Problem: GitHub Actions fail after making private
**Solution:**
- Verify `GITHUB_TOKEN` secret exists
- Check workflow has `contents: read` permission
- Ensure Actions are enabled for private repos

### Problem: HuggingFace Space can't pull from GitHub
**Solution:**
- Add `GITHUB_TOKEN` to Space secrets
- Update Space to use token for authentication
- Consider using SSH deploy keys

### Problem: Bridge workflow doesn't discover private repo
**Solution:**
- Ensure `GITHUB_TOKEN` is set in workflow environment
- Check token has `repo` scope for private repos
- Verify API rate limits not exceeded

---

## 📊 PRIVACY IMPACT ASSESSMENT

### What Changes:
- ✅ Repository code becomes private
- ✅ Requires authentication for access
- ✅ Only visible to organization members/collaborators

### What Stays the Same:
- ✅ Repository name and URL
- ✅ Integration with mapping-and-inventory
- ✅ HuggingFace Space deployment
- ✅ Bridge workflow discovery
- ✅ Artifact extraction and sync

### Additional Steps Needed:
- Configure authentication tokens
- Update Space secrets
- Add collaborators if needed
- Update clone commands in documentation

---

## 📚 RELATED DOCUMENTATION

- [GitHub Private Repositories](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility)
- [HuggingFace Private Spaces](https://huggingface.co/docs/hub/spaces-overview#private-spaces)
- [GitHub Actions Authentication](https://docs.github.com/en/actions/security-guides/automatic-token-authentication)
- [Global Bridge System](REPO_BRIDGE_GUIDE.md)

---

## ✅ COMPLETION CHECKLIST

When finished, you should have:

- [ ] TIA-ARCHITECT-CORE repository is private
- [ ] GITHUB_TOKEN configured in mapping-and-inventory
- [ ] GITHUB_TOKEN configured in HuggingFace Space
- [ ] Bridge workflow tested with private repo
- [ ] Clone commands updated in documentation
- [ ] Team members have access (if needed)
- [ ] HuggingFace Space visibility configured (optional)
- [ ] All integrations verified working

---

**Status:** Privacy Configuration Ready  
**Authority:** Citadel Architect v25.0.OMNI+  
**Last Updated:** 2026-04-03

**Weld. Pulse. Secure.**
