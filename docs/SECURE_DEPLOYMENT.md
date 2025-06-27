# 🔐 Secure Deployment Guide

This guide explains how to deploy Gap Hunter Bot without exposing your API keys.

## ⚠️ **CRITICAL SECURITY RULES**

1. **NEVER commit `.env` files** to version control
2. **NEVER hardcode API keys** in your source code  
3. **ALWAYS use environment variables** in production
4. **REGULARLY rotate** your API keys
5. **MONITOR usage** for suspicious activity

## 🚀 **Deployment Options**

### **Option 1: Streamlit Cloud (Recommended)**

1. **Prepare your repository:**
```bash
# Ensure .env is in .gitignore
git add .gitignore
git commit -m "Secure .env files"
git push origin main
```

2. **Deploy to Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set main file: `web/streamlit_app.py`

3. **Add secrets securely:**
   - In your app dashboard, click "Settings" → "Secrets"
   - Add your API keys in TOML format:
```toml
OPENAI_API_KEY = "sk-..."
ANTHROPIC_API_KEY = "sk-ant-..."
GEMINI_API_KEY = "AIza..."
GOOGLE_API_KEY = "AIza..."
S2_API_KEY = "your_s2_key"
CORE_API_KEY = "your_core_key"
CONTACT_EMAIL = "your_email@example.com"
```

### **Option 2: Heroku**

1. **Create Heroku app:**
```bash
heroku create your-app-name
```

2. **Set environment variables:**
```bash
heroku config:set OPENAI_API_KEY="your_key" --app your-app-name
heroku config:set ANTHROPIC_API_KEY="your_key" --app your-app-name
heroku config:set GEMINI_API_KEY="your_key" --app your-app-name
heroku config:set GOOGLE_API_KEY="your_key" --app your-app-name
heroku config:set S2_API_KEY="your_key" --app your-app-name
heroku config:set CORE_API_KEY="your_key" --app your-app-name
heroku config:set CONTACT_EMAIL="your_email@example.com" --app your-app-name
```

3. **Deploy:**
```bash
git push heroku main
```

### **Option 3: Docker + VPS**

1. **Build with secrets:**
```bash
# Use Docker secrets or environment variables
docker run -d \
  --name gaphunter \
  -p 8501:8501 \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  -e GEMINI_API_KEY="$GEMINI_API_KEY" \
  -e GOOGLE_API_KEY="$GOOGLE_API_KEY" \
  -e S2_API_KEY="$S2_API_KEY" \
  -e CORE_API_KEY="$CORE_API_KEY" \
  -e CONTACT_EMAIL="$CONTACT_EMAIL" \
  gaphunter:latest
```

## 🔍 **Security Verification**

### **Before Deployment Checklist:**

- [ ] `.env` file is in `.gitignore`
- [ ] No API keys in source code
- [ ] All secrets configured in deployment platform
- [ ] Test app works with environment variables
- [ ] Monitor API usage after deployment

### **Test Security:**
```bash
# Check that .env is ignored
git status
# Should NOT show .env as tracked

# Verify environment variables work
python src/config_loader.py
```

## 🛡️ **Best Practices**

### **API Key Management:**
1. **Use different keys** for development and production
2. **Set usage limits** on your API keys
3. **Enable monitoring** and alerts
4. **Rotate keys regularly** (every 3-6 months)

### **Access Control:**
1. **Limit repository access** to trusted collaborators
2. **Use branch protection** rules
3. **Review all pull requests** carefully
4. **Enable two-factor authentication**

### **Monitoring:**
1. **Track API usage** patterns
2. **Set up billing alerts**
3. **Monitor application logs**
4. **Watch for unusual activity**

## 🚨 **If API Keys Are Compromised**

1. **Immediately revoke** the compromised keys
2. **Generate new keys** with different names
3. **Update deployment** with new keys
4. **Review usage logs** for unauthorized activity
5. **Consider changing** other related credentials

## 📞 **Support**

If you need help with secure deployment:
- Check the security status in the app sidebar
- Review deployment logs for errors
- Ensure all required environment variables are set
- Test with minimal API key set first

Remember: **Security is not optional** - always protect your API keys!
