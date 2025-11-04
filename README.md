# SAGE - Safety Analysis Generation Engine

A Streamlit-based RAG (Retrieval Augmented Generation) application with NASA Launchpad OIDC authentication for safety analysis documentation.

## Features

- **NASA Launchpad OIDC Authentication**: Secure OAuth 2.0 / OpenID Connect authentication with PIV card
- **Group-Based Access Control**: Role-based authorization with SAGE-EC4-Engineers and SAGE-Administrators groups
- **PDF RAG System**: Question answering over safety analysis documentation using LangChain
- **Multi-Query Retrieval**: Enhanced document retrieval with multiple query perspectives
- **Vector Database**: Chroma vector store with Ollama embeddings
- **Production-Ready**: Environment-based configuration, systemd service, nginx reverse proxy support
- **Admin Panel**: System management tools for administrators

## Architecture

### Authentication Flow

1. User accesses application
2. NASA Launchpad OIDC login via OAuth 2.0
3. Token exchange and validation
4. User information retrieval from userinfo endpoint
5. Session management in Streamlit

### Components

- **`pdf-rag-streamlit.py`**: Main Streamlit application with authorization
- **`auth.py`**: Authentication module with OIDC integration
- **`.streamlit/config.toml`**: Streamlit configuration (SSL/HTTPS)
- **`.streamlit/secrets.toml`**: OAuth credentials (not in repo - see setup)

## Prerequisites

- Python 3.9+
- NASA Launchpad OAuth credentials
- Access to NASA internal network
- Ollama with Mistral model (for RAG functionality)

## Quick Start

### 1. Configure OAuth Credentials

Create `.streamlit/secrets.toml`:

```toml
[oauth]
client_id = "YOUR_NASA_CLIENT_ID"
client_secret = "YOUR_NASA_CLIENT_SECRET"
issuer_url = "https://authfs.launchpad.nasa.gov/adfs/.well-known/openid-configuration"
redirect_uri = "https://localhost:8501/component/streamlit_oauth.authorize_button"
scopes = "openid profile email"
```

### 2. Run Application

```bash
streamlit run pdf-rag-streamlit.py
```

Access at: `https://localhost:8501`

## NASA Network Requirements

**This application must run on a NASA laptop with access to:**
- NASA internal network
- NASA Launchpad authentication servers
- Registered OAuth application in NASA Launchpad

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

