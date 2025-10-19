# Security Guidelines

## 🔒 Sensitive Data Management

### What Should NEVER Be Committed

1. **API Keys** - All API keys must come from environment variables
   - LANGFUSE_SECRET_KEY
   - LANGFUSE_PUBLIC_KEY
   - LOGFIRE_API_KEY
   - CEREBRAS_API_KEY
   - OPENROUTER_API_KEY

2. **Database Passwords** - All credentials must come from environment variables
   - Database credentials (PostgreSQL, Neo4j, etc.)
   - Redis passwords
   - Any other sensitive authentication

3. **.env Files** - The `.env` file is in `.gitignore` and should never be committed

### Proper Configuration Pattern

✅ **CORRECT** - Use environment variables:
```python
class Settings(BaseSettings):
    cerebras_api_key: str = ""  # Must be set via .env or environment
    
settings = Settings()
```

❌ **WRONG** - Hardcoded values:
```python
class Settings(BaseSettings):
    cerebras_api_key: str = "csk_27f88e3dfd3c4bfc96e91d6b4ddd6c3f"  # ❌ NEVER DO THIS!
```

### Environment File Template

Create `.env` locally (not committed):
```bash
# .env (add to .gitignore - DO NOT COMMIT)
LANGFUSE_SECRET_KEY=sk-lf-xxxxx
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxx
LOGFIRE_API_KEY=your_key_here
CEREBRAS_API_KEY=csk_xxxxx
OPENROUTER_API_KEY=sk-or-v1-xxxxx
NEO4J_PASSWORD=your_password_here
```

Use `env.example` for template (with placeholder values):
```bash
# env.example (committed for reference)
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
```

## 🛡️ Security Checklist

Before every commit, verify:

- [ ] No API keys in code (use `settings.api_key_name`)
- [ ] No passwords in code (use environment variables)
- [ ] No `.env` file committed
- [ ] `.gitignore` contains `.env` entries
- [ ] All credentials loaded from environment

## 🔍 Scanning for Secrets

If you accidentally commit a secret:

1. **Immediate fix:**
   ```bash
   # Remove from config
   git add .
   git commit -m "security: remove exposed secret"
   
   # Remove from history
   git filter-branch --force --tree-filter \
     'sed -i "" "s/secret_value//g" app/core/config.py' -- --all
   
   # Force push (⚠️ use with caution)
   git push origin branch --force
   ```

2. **Rotate the exposed credential immediately** in your provider dashboard

## 📋 Files Protected

- `.env` - Local environment variables (in .gitignore)
- `.env.local` - Local overrides (in .gitignore)
- `.env.*.local` - Environment-specific (in .gitignore)

## 🚀 For Deployment

1. Set environment variables in your deployment platform
2. Load configuration from environment at runtime
3. Never hard-code secrets in code or config files
4. Use secrets management tools (AWS Secrets Manager, HashiCorp Vault, etc.)

## 📚 References

- [OWASP - Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [12-Factor App - Config](https://12factor.net/config)

---

**Last Updated**: 2024
**Status**: ✅ All sensitive data removed from repository
