# NASA Laptop Quick Start Guide

This is your quick reference for setting up SAGE on your NASA laptop.

## Step-by-Step Setup

### 1. Clone Repository on NASA Laptop

```bash
git clone https://github.com/EthanHoman/SAGE_STREAMLIT_OAUTH.git
cd SAGE_STREAMLIT_OAUTH
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Generate SSL Certificates

**Choose the easiest method for you:**

#### Option A: Use the Script (Fastest)

**Mac/Linux:**
```bash
./generate_ssl_certs.sh
```

**Windows:**
```powershell
.\generate_ssl_certs.ps1
```

✓ This creates `ssl/cert.pem` and `ssl/key.pem`

**Note**: Your browser will show a security warning. Just click "Advanced" → "Proceed to localhost"

#### Option B: Use mkcert (No Browser Warnings)

**If you want a cleaner experience without security warnings:**

**Mac:**
```bash
brew install mkcert
mkcert -install
mkcert localhost 127.0.0.1 ::1
mkdir -p ssl
mv localhost+2.pem ssl/cert.pem
mv localhost+2-key.pem ssl/key.pem
```

**Windows (with Chocolatey):**
```powershell
choco install mkcert
mkcert -install
mkcert localhost 127.0.0.1 ::1
mkdir ssl
mv localhost+2.pem ssl\cert.pem
mv localhost+2-key.pem ssl\key.pem
```

### 4. Configure NASA OAuth Credentials

**Create your secrets file:**
```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

**Edit `.streamlit/secrets.toml`** and add your NASA credentials:

```toml
[oauth]
client_id = "YOUR_NASA_CLIENT_ID"
client_secret = "YOUR_NASA_CLIENT_SECRET"
issuer_url = "https://authfs.launchpad.nasa.gov/adfs/.well-known/openid-configuration"
redirect_uri = "https://localhost:8501/component/streamlit_oauth.authorize_button"
scopes = "openid profile email"
```

### 5. Get NASA OAuth Credentials

**You need to contact NASA IT to:**
1. Register an OAuth 2.0 application for SAGE
2. Provide redirect URI: `https://localhost:8501/component/streamlit_oauth.authorize_button`
3. Request scopes: `openid`, `profile`, `email`
4. They'll give you a Client ID and Client Secret

### 6. Run the Application

```bash
streamlit run pdf-rag-streamlit.py
```

Open: `https://localhost:8501`

---

## Troubleshooting

### Browser Shows Security Warning

**This is normal for self-signed certificates!**

- **Chrome/Edge**: Click "Advanced" → "Proceed to localhost (unsafe)"
- **Firefox**: Click "Advanced" → "Accept the Risk and Continue"
- **Safari**: Click "Show Details" → "visit this website"

### Can't Reach NASA Launchpad

- Verify you're on **NASA internal network** (not guest WiFi)
- Test connection: `curl https://authfs.launchpad.nasa.gov/adfs/.well-known/openid-configuration`
- Check if you need proxy settings

### OpenSSL Not Found

**Mac:**
```bash
brew install openssl
```

**Windows:**
Download from: https://slproweb.com/products/Win32OpenSSL.html

### OAuth Credentials Not Working

- Verify Client ID and Secret are correct
- Ensure redirect URI is registered with NASA Launchpad
- Check you're using the right NASA Launchpad environment

---

## Important Notes

✓ Must be on **NASA internal network**
✓ Must have **OAuth app registered** with NASA IT
✓ Certificates are **generated locally** (not in repo)
✓ Never commit `.streamlit/secrets.toml` to git

---

## Need More Help?

See the full documentation:
- **[SETUP_AUTH.md](SETUP_AUTH.md)** - Comprehensive authentication setup
- **[README.md](README.md)** - Full project documentation

For NASA IT support: Contact your local IT service desk or identity management team
