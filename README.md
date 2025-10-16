# SAGE - Safety Analysis Generation Engine

A Streamlit-based RAG (Retrieval Augmented Generation) application with NASA Launchpad OIDC authentication for safety analysis documentation.

## Features

- **NASA Launchpad OIDC Authentication**: Secure OAuth 2.0 / OpenID Connect authentication
- **PDF RAG System**: Question answering over safety analysis documentation using LangChain
- **Multi-Query Retrieval**: Enhanced document retrieval with multiple query perspectives
- **Vector Database**: Chroma vector store with Ollama embeddings
- **User Management**: Session-based authentication with user info display

## Architecture

### Authentication Flow

1. User accesses application
2. NASA Launchpad OIDC login via OAuth 2.0
3. Token exchange and validation
4. User information retrieval from userinfo endpoint
5. Session management in Streamlit

### Components

- **`pdf-rag-streamlit.py`**: Main Streamlit application
- **`auth.py`**: Authentication module with OIDC integration
- **`.streamlit/config.toml`**: Streamlit configuration (SSL/HTTPS)
- **`.streamlit/secrets.toml`**: OAuth credentials (not in repo - see setup)

## Prerequisites

- Python 3.9+
- NASA Launchpad OAuth credentials
- Access to NASA internal network
- Ollama with Mistral model (for RAG functionality)

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/EthanHoman/SAGE_STREAMLIT_OAUTH.git
cd SAGE_STREAMLIT_OAUTH
```

### 2. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure OAuth Credentials

Create `.streamlit/secrets.toml`:

```toml
[oauth]
client_id = "YOUR_NASA_CLIENT_ID"
client_secret = "YOUR_NASA_CLIENT_SECRET"
issuer_url = "https://authfs.launchpad.nasa.gov/adfs/.well-known/openid-configuration"
redirect_uri = "https://localhost:8501/component/streamlit_oauth.authorize_button"
scopes = "openid profile email"
```

**⚠️ Important**: Contact NASA IT to obtain OAuth credentials and register your redirect URI.

### 4. Generate SSL Certificates

**IMPORTANT**: SSL certificates are NOT in the repository. Generate them after cloning:

**Quick Method (Recommended):**

```bash
# Mac/Linux
./generate_ssl_certs.sh

# Windows PowerShell
.\generate_ssl_certs.ps1
```

**Or manually with OpenSSL:**

```bash
mkdir -p ssl
cd ssl
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes \
  -subj "/C=US/ST=Texas/L=Houston/O=NASA/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
```

**For a better experience without browser warnings, use [mkcert](https://github.com/FiloSottile/mkcert)** - see [SETUP_AUTH.md](SETUP_AUTH.md) for detailed instructions and other options.

### 5. Run Application

```bash
streamlit run pdf-rag-streamlit.py
```

Access at: `https://localhost:8501`

## NASA Network Requirements

**This application must run on a NASA laptop with access to:**
- NASA internal network (not guest WiFi)
- NASA Launchpad authentication servers
- Registered OAuth application in NASA Launchpad

## Documentation

- **[SETUP_AUTH.md](SETUP_AUTH.md)**: Comprehensive authentication setup guide
- **[prepare_for_transfer.sh](prepare_for_transfer.sh)**: Script to prepare project for NASA laptop transfer

## Dependencies

Key packages:
- `streamlit`: Web application framework
- `streamlit-oauth`: OAuth 2.0 / OIDC component
- `langchain`: RAG framework
- `chromadb`: Vector database
- `ollama`: Local LLM integration

See [requirements.txt](requirements.txt) for full list.

## Security

### Protected Files (Not in Repository)

- `.streamlit/secrets.toml` - OAuth credentials
- `ssl/*.pem` - SSL certificates
- `chroma_db/` - Vector database
- `venv/` - Virtual environment

### Best Practices

- Never commit secrets to repository
- Use HTTPS for OAuth flows
- Rotate credentials regularly
- Implement token refresh for long sessions

## Project Structure

```
SAGE_STREAMLIT_OAUTH/
├── pdf-rag-streamlit.py          # Main application
├── auth.py                        # Authentication module
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
├── README.md                      # This file
├── SETUP_AUTH.md                  # Comprehensive setup guide
├── generate_ssl_certs.sh          # SSL certificate generator (Mac/Linux)
├── generate_ssl_certs.ps1         # SSL certificate generator (Windows)
├── prepare_for_transfer.sh        # Transfer preparation script
├── .streamlit/
│   ├── config.toml                # Streamlit configuration
│   ├── secrets.toml.template      # OAuth credentials template
│   └── secrets.toml               # OAuth credentials (not in repo)
├── ssl/
│   ├── cert.pem                   # SSL certificate (not in repo)
│   └── key.pem                    # SSL private key (not in repo)
├── data/                          # PDF documents
└── images/                        # Application assets
```

## Troubleshooting

### Cannot reach NASA Launchpad

- Verify you're on NASA internal network
- Check proxy settings if behind NASA firewall
- Test connection: `curl https://authfs.launchpad.nasa.gov/adfs/.well-known/openid-configuration`

### OAuth Redirect URI Mismatch

- Ensure redirect URI in `secrets.toml` matches NASA Launchpad registration
- Verify format: `https://localhost:8501/component/streamlit_oauth.authorize_button`

### SSL Certificate Errors

- Accept browser warning for self-signed certificates (development only)
- For production, use proper CA-signed certificates

See [SETUP_AUTH.md](SETUP_AUTH.md) for detailed troubleshooting.

## Development vs Production

### Current Setup (Development)
- Self-signed SSL certificates
- Running on localhost
- Secrets in local file

### Production Recommendations
- Proper SSL certificates (Let's Encrypt, NASA CA)
- Reverse proxy (nginx, Apache)
- Environment variables or secrets management
- Rate limiting and security headers
- Audit logging

## Contributing

This is an internal NASA tool. For issues or enhancements, contact JSC EC4.

## License

Internal NASA use only.

## Support

- **Authentication Issues**: Contact NASA IT or identity management team
- **Application Issues**: Contact JSC EC4
- **OAuth Library**: https://github.com/dnplus/streamlit-oauth

---

**Developed by JSC EC4**

*A specialized tool for generating safety analysis documentation*

