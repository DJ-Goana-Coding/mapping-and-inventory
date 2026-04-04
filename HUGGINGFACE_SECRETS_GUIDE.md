# 🔐 HUGGINGFACE SECRETS MANAGEMENT GUIDE

**Repository**: DJ-Goana-Coding/mapping-and-inventory  
**HuggingFace Space**: DJ-Goanna-Coding/Mapping-and-Inventory  
**Last Updated**: 2026-04-04

---

## 📋 CURRENT SECRETS INVENTORY

### GitHub Actions Secrets

These secrets are configured at:
`https://github.com/DJ-Goana-Coding/mapping-and-inventory/settings/secrets/actions`

| Secret Name | Purpose | Used By | Status |
|-------------|---------|---------|--------|
| `HF_TOKEN` | HuggingFace API access | sync_to_hf.yml, deploy workflows | ✅ Required |
| `GH_PAT` | GitHub Personal Access Token | Cross-repo operations | ✅ Required |
| `MASTER_PASSWORD` | Quantum Vault master password | Credential management | 🆕 NEW |
| `QUANTUM_VAULT_KEY` | Alternative vault key | Optional backup method | 🆕 NEW |
| `MEXC_API_KEY` | MEXC Exchange API | Trading workflows | ⚠️ Optional |
| `MEXC_API_SECRET` | MEXC Exchange Secret | Trading workflows | ⚠️ Optional |
| `GOOGLE_API_KEY` | Google services access | GDrive/Gmail automation | 🆕 NEW |

### HuggingFace Space Secrets

These secrets are configured at:
`https://huggingface.co/spaces/DJ-Goanna-Coding/Mapping-and-Inventory/settings`

| Secret Name | Purpose | Used By | Status |
|-------------|---------|---------|--------|
| `GITHUB_TOKEN` | GitHub API access from Space | Repo sync, data fetch | ✅ Required |
| `HF_TOKEN` | HuggingFace operations | Model download, dataset access | ✅ Required |
| `MASTER_PASSWORD` | Credential vault access | Email/GDrive automation | 🆕 NEW |
| `GOOGLE_DRIVE_CREDENTIALS` | GDrive OAuth credentials | GDrive API access | 🆕 NEW |
| `GEMINI_API_KEY` | Google Gemini AI | T.I.A. Oracle chat | ⚠️ Optional |

---

## 🆕 NEW SECRETS TO ADD

### 1. MASTER_PASSWORD

**Value**: `Tia-sue1104!!`

**Configuration Steps**:

#### GitHub Actions:
```bash
# Navigate to:
https://github.com/DJ-Goana-Coding/mapping-and-inventory/settings/secrets/actions

# Click "New repository secret"
# Name: MASTER_PASSWORD
# Value: Tia-sue1104!!
# Click "Add secret"
```

#### HuggingFace Space:
```bash
# Navigate to:
https://huggingface.co/spaces/DJ-Goanna-Coding/Mapping-and-Inventory/settings

# Scroll to "Repository secrets"
# Click "New secret"
# Name: MASTER_PASSWORD
# Value: Tia-sue1104!!
# Click "Add"
```

**Security Notes**:
- ✅ AES-256-GCM encrypted in Quantum Vault
- ✅ Never logged or exposed in workflows
- ✅ Used only for credential derivation
- ⚠️ Rotate if compromised

### 2. QUANTUM_VAULT_KEY (Optional Alternative)

If you prefer to use a generated key instead of password:

```bash
# Generate secure key
python -c "from security.core.quantum_vault import QuantumVault; print(QuantumVault.generate_master_key())"

# Add as secret (same process as MASTER_PASSWORD)
# Choose ONE: Either MASTER_PASSWORD or QUANTUM_VAULT_KEY
```

### 3. GOOGLE_API_KEY

For Google Drive API access:

1. Go to: https://console.cloud.google.com/
2. Create project: "Citadel GDrive Access"
3. Enable APIs:
   - Google Drive API
   - Gmail API
4. Create credentials:
   - API Key (for simple access)
   - OAuth 2.0 Client (for user data)
5. Copy API key
6. Add to GitHub/HF secrets

### 4. GOOGLE_DRIVE_CREDENTIALS

OAuth2 credentials JSON:

```json
{
  "installed": {
    "client_id": "<your-client-id>.apps.googleusercontent.com",
    "client_secret": "<your-client-secret>",
    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
```

**Setup**:
1. Download from Google Cloud Console
2. Minify JSON (remove whitespace)
3. Add entire JSON as secret value

---

## 🔄 SECRET ROTATION WORKFLOW

### When to Rotate:
- ⚠️ Suspected compromise
- ⚠️ Team member departure
- ⚠️ Regular security audit (quarterly)
- ⚠️ After public repository exposure

### How to Rotate MASTER_PASSWORD:

```bash
# 1. Generate new master key
python scripts/initialize_credential_vault.py generate-key

# 2. Update GitHub Secret
# Navigate to: Settings → Secrets → Actions → MASTER_PASSWORD
# Edit and paste new value

# 3. Update HuggingFace Secret
# Navigate to: Space Settings → Secrets → MASTER_PASSWORD
# Edit and paste new value

# 4. Re-encrypt vault (optional, for defense-in-depth)
python scripts/rotate_vault_key.py --old-password "old-pass" --new-password "new-pass"

# 5. Verify access
python scripts/initialize_credential_vault.py verify
```

---

## 🛡️ SECURITY BEST PRACTICES

### DO:
✅ Use different passwords for different services  
✅ Enable 2FA on GitHub and HuggingFace  
✅ Review secret access logs regularly  
✅ Use GitHub Actions secrets for sensitive data  
✅ Rotate secrets quarterly  
✅ Use Quantum Vault for centralized management  

### DON'T:
❌ Commit secrets to git  
❌ Share secrets via chat/email  
❌ Use same password across services  
❌ Log secrets in workflow output  
❌ Hardcode secrets in code  
❌ Share GitHub Personal Access Tokens  

---

## 📊 SECRET USAGE MATRIX

| Secret | GitHub Actions | HF Space | Local Dev | Workflows Using |
|--------|---------------|----------|-----------|-----------------|
| `MASTER_PASSWORD` | ✅ | ✅ | ✅ | credential_vault_init.yml, email_harvest.yml, gdrive_harvest.yml |
| `HF_TOKEN` | ✅ | ✅ | ⚠️ | sync_to_hf.yml, deploy_tia_core.yml, frontier_models.yml |
| `GH_PAT` | ✅ | ❌ | ⚠️ | bridge_push.yml, global_repo_bridge.yml, multi_repo_sync.yml |
| `GOOGLE_API_KEY` | ✅ | ✅ | ✅ | gdrive_harvester.yml, gmail_integration.yml |

---

## 🔧 TROUBLESHOOTING

### Secret Not Found Error:
```
Error: Secret MASTER_PASSWORD not found
```

**Solution**:
1. Verify secret is added to repository
2. Check secret name matches exactly (case-sensitive)
3. Re-add secret if necessary
4. Wait 5-10 seconds for propagation

### Decryption Failed Error:
```
Error: Failed to decrypt vault: Invalid token
```

**Solution**:
1. MASTER_PASSWORD is incorrect
2. Vault was encrypted with different key
3. Vault file is corrupted
4. Re-initialize vault with correct password

### HuggingFace Permission Error:
```
Error: 403 Forbidden - HF_TOKEN lacks permissions
```

**Solution**:
1. Generate new token at: https://huggingface.co/settings/tokens
2. Enable **Write** permission
3. Update HF_TOKEN secret
4. Re-run workflow

---

## 📋 AUDIT CHECKLIST

Use this checklist for quarterly security audits:

- [ ] All secrets still valid and working
- [ ] No secrets exposed in logs or commits
- [ ] GitHub Actions only use necessary secrets
- [ ] HuggingFace Space secrets match GitHub
- [ ] 2FA enabled on all accounts
- [ ] Quantum Vault accessible and backed up
- [ ] All email accounts still accessible
- [ ] GDrive OAuth tokens still valid
- [ ] Trading API keys still active
- [ ] Secret access logs reviewed

---

## 🚀 QUICK SETUP COMMANDS

```bash
# 1. Initialize Quantum Vault with master password
export MASTER_PASSWORD="Tia-sue1104!!"
python scripts/initialize_credential_vault.py init

# 2. Verify vault access
python scripts/initialize_credential_vault.py verify

# 3. List stored credentials
python scripts/initialize_credential_vault.py list

# 4. Harvest email accounts
python scripts/harvest_email_accounts.py

# 5. Check GDrive accounts
python scripts/harvest_gdrive_accounts.py

# 6. Generate reports
ls -la data/personal_archive/
```

---

## 📞 SUPPORT

**Issues**: https://github.com/DJ-Goana-Coding/mapping-and-inventory/issues  
**Security**: Report security issues privately to repository owner  
**Documentation**: See `security/core/` for implementation details

---

**Last Updated**: 2026-04-04  
**Maintained By**: Citadel Architect v25.0.OMNI+  
**Security Level**: Post-Quantum Ready 🔒
