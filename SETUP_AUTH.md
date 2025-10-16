# SAGE - NASA Launchpad OIDC Authentication Setup Guide

This guide will help you configure and test NASA Launchpad OIDC authentication for the SAGE application.

## Prerequisites

1. NASA Launchpad OAuth client credentials (Client ID and Client Secret)
2. Python 3.9+
3. All dependencies installed from `requirements.txt`

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure OAuth Credentials

Edit the `.streamlit/secrets.toml` file and replace the placeholder values with your actual NASA Launchpad credentials:

```toml
[oauth]
client_id = "YOUR_ACTUAL_NASA_CLIENT_ID"
client_secret = "YOUR_ACTUAL_NASA_CLIENT_SECRET"
issuer_url = "https://authfs.launchpad.nasa.gov/adfs/.well-known/openid-configuration"
redirect_uri = "https://localhost:8501/component/streamlit_oauth.authorize_button"
scopes = "openid profile email"
```

**Important:**
- Make sure your redirect_uri (`https://localhost:8501/component/streamlit_oauth.authorize_button`) is registered in your NASA Launchpad OAuth application settings
- Never commit the `secrets.toml` file to version control

### 3. SSL Certificate Setup

**IMPORTANT**: SSL certificates are not included in the repository (they're in `.gitignore`). You need to generate them on your NASA laptop.

#### Option A: Quick Generation with Script (Recommended for Getting Started)

**For Mac/Linux:**
```bash
./generate_ssl_certs.sh
```

**For Windows PowerShell:**
```powershell
.\generate_ssl_certs.ps1
```

This generates self-signed certificates in the `ssl/` directory valid for 365 days.

**Browser Security Warning**: You'll see a warning since these are self-signed. This is normal and safe for localhost development.

**To proceed past the warning:**
- **Chrome/Edge**: Click "Advanced" → "Proceed to localhost (unsafe)"
- **Firefox**: Click "Advanced" → "Accept the Risk and Continue"
- **Safari**: Click "Show Details" → "visit this website"

---

#### Option B: Using mkcert (Best Experience - No Browser Warnings)

**What is mkcert?**
mkcert creates locally-trusted SSL certificates. Your browser won't show security warnings.

**Installation:**

**macOS:**
```bash
brew install mkcert
brew install nss  # if you use Firefox
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install libnss3-tools
wget https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-linux-amd64
chmod +x mkcert-v1.4.4-linux-amd64
sudo mv mkcert-v1.4.4-linux-amd64 /usr/local/bin/mkcert

# Or use your package manager if available
```

**Windows:**
```powershell
# Using Chocolatey
choco install mkcert

# Or using Scoop
scoop bucket add extras
scoop install mkcert
```

**Generate Certificates:**
```bash
# Install local CA (one-time setup)
mkcert -install

# Generate certificates for localhost
mkcert localhost 127.0.0.1 ::1

# Move to ssl directory
mkdir -p ssl
mv localhost+2.pem ssl/cert.pem
mv localhost+2-key.pem ssl/key.pem
```

**Advantages:**
- ✓ No browser security warnings
- ✓ Cleaner development experience
- ✓ Automatic trust in all browsers

---

#### Option C: Manual OpenSSL (For Maximum Control)

**Generate with OpenSSL:**
```bash
mkdir -p ssl
cd ssl

openssl req -x509 -newkey rsa:4096 \
  -keyout key.pem \
  -out cert.pem \
  -days 365 \
  -nodes \
  -subj "/C=US/ST=Texas/L=Houston/O=NASA JSC/OU=EC4/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

cd ..
```

**Windows PowerShell Alternative:**
```powershell
# Using built-in New-SelfSignedCertificate (Windows only)
$cert = New-SelfSignedCertificate -DnsName "localhost" -CertStoreLocation "cert:\LocalMachine\My"
$certPath = "cert:\LocalMachine\My\$($cert.Thumbprint)"

# Export certificate
$pwd = ConvertTo-SecureString -String "password" -Force -AsPlainText
Export-PfxCertificate -Cert $certPath -FilePath ssl\cert.pfx -Password $pwd

# Note: You'll need to convert .pfx to .pem format or use Streamlit's pfx support
```

---

#### Option D: NASA IT Certificate Authority (Production Use)

**For production deployment or if you want properly trusted certificates:**

1. Contact NASA IT or your security team
2. Request an SSL certificate for your hostname
3. Provide Certificate Signing Request (CSR):
   ```bash
   openssl req -new -newkey rsa:4096 -nodes \
     -keyout ssl/key.pem \
     -out ssl/csr.pem \
     -subj "/C=US/ST=Texas/L=Houston/O=NASA JSC/OU=EC4/CN=your-nasa-hostname"
   ```
4. Submit `csr.pem` to NASA IT
5. Receive signed certificate and save as `ssl/cert.pem`

**Note**: This option is only needed for production deployments on NASA servers, not for local laptop development.

---

#### Comparison Table

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Script (Option A)** | Quick, no installation | Browser warnings | Quick setup, first time users |
| **mkcert (Option B)** | No warnings, trusted | Requires installation | Best development experience |
| **OpenSSL (Option C)** | Full control, portable | Browser warnings | Advanced users, specific requirements |
| **NASA CA (Option D)** | Properly trusted | Requires IT approval, time | Production deployments |

**Recommendation**: Use **Option A** (script) to get started quickly, then switch to **Option B** (mkcert) for a better development experience.

### 4. Register OAuth Application with NASA Launchpad

Before running the application, ensure your OAuth application is registered with NASA Launchpad:

1. Contact NASA IT or access the Launchpad developer portal
2. Register a new OAuth 2.0 application
3. Set the callback/redirect URL to: `https://localhost:8501/component/streamlit_oauth.authorize_button`
4. Request the following scopes: `openid`, `profile`, `email`
5. Note down your Client ID and Client Secret

### 5. Run the Application

Start the Streamlit application with HTTPS:

```bash
streamlit run pdf-rag-streamlit.py
```

The application should start on `https://localhost:8501`

### 6. Test Authentication Flow

1. Open your browser and navigate to `https://localhost:8501`
2. Accept the self-signed certificate warning (for development only)
3. You should see the SAGE login page
4. Click "Login with NASA Launchpad"
5. A popup window will open redirecting to NASA Launchpad
6. Enter your NASA credentials
7. After successful authentication, you'll be redirected back to SAGE
8. The main application interface should appear with your user information in the sidebar

## Architecture Overview

### Authentication Flow

1. **Login Trigger**: User clicks "Login with NASA Launchpad" button
2. **Authorization Request**: Application redirects to NASA Launchpad authorization endpoint
3. **User Authentication**: User authenticates with NASA credentials
4. **Authorization Grant**: NASA Launchpad redirects back with authorization code
5. **Token Exchange**: Application exchanges code for access token
6. **User Info Retrieval**: Application fetches user information using access token
7. **Session Management**: User session is maintained in Streamlit session state

### Key Components

- **`auth.py`**: Authentication module
  - `OIDCMetadata`: Fetches and parses OIDC discovery metadata
  - `initialize_oauth_component()`: Initializes OAuth2Component with NASA endpoints
  - `get_user_info()`: Retrieves user information from userinfo endpoint
  - `check_authentication()`: Validates authentication state
  - `logout()`: Clears authentication session

- **`pdf-rag-streamlit.py`**: Main application
  - `show_login_page()`: Displays login interface
  - `show_sage_app()`: Displays main application (authenticated)
  - `main()`: Entry point with authentication gate

### Session State Variables

- `token`: Complete OAuth token response
- `access_token`: Access token for API calls
- `user_info`: User information from OIDC userinfo endpoint
- `oidc_metadata`: Cached OIDC metadata object

## Troubleshooting

### Issue: "Configuration error: Missing oauth in secrets.toml"

**Solution:** Ensure `.streamlit/secrets.toml` exists and contains the `[oauth]` section with all required fields.

### Issue: SSL Certificate Error

**Solution:**
- Accept the browser security warning for self-signed certificates
- Or, use a proper SSL certificate (e.g., from Let's Encrypt) for production

### Issue: "Failed to fetch OIDC metadata"

**Solution:**
- Verify network connectivity to `https://authfs.launchpad.nasa.gov`
- Check if you're behind a firewall or proxy
- Verify the issuer_url in secrets.toml is correct

### Issue: OAuth Redirect URI Mismatch

**Solution:**
- Ensure the redirect_uri in `secrets.toml` matches exactly what's registered in NASA Launchpad
- The URI must include the protocol, domain, port, and path: `https://localhost:8501/component/streamlit_oauth.authorize_button`

### Issue: "Failed to fetch user info"

**Solution:**
- Verify the `openid`, `profile`, and `email` scopes are requested
- Check if the access token is valid
- Ensure NASA Launchpad's userinfo endpoint is accessible

### Issue: Application doesn't redirect after login

**Solution:**
- Check browser console for JavaScript errors
- Verify popup windows are not blocked
- Clear browser cache and cookies
- Check if the OAuth callback is being received

## Security Considerations

### Development vs Production

**Development (Current Setup):**
- Self-signed SSL certificates
- Credentials in `secrets.toml`
- Running on localhost

**Production Recommendations:**
- Use proper SSL certificates (Let's Encrypt, corporate CA)
- Store secrets in environment variables or secure vault
- Use a reverse proxy (nginx, Apache) for SSL termination
- Enable additional security headers
- Implement rate limiting
- Add audit logging

### Best Practices

1. **Never commit secrets**: Add `.streamlit/secrets.toml` to `.gitignore`
2. **Rotate credentials**: Regularly update OAuth client secrets
3. **Token expiration**: Implement token refresh logic for long sessions
4. **Secure session storage**: Use Streamlit's built-in session state (server-side)
5. **HTTPS only**: Never use plain HTTP for OAuth flows

## Additional Configuration

### Custom Scopes

If you need additional scopes beyond `openid profile email`, update the `scopes` field in `secrets.toml`:

```toml
scopes = "openid profile email custom_scope"
```

### Token Refresh

The current implementation doesn't include automatic token refresh. For long-running sessions, you may want to implement token refresh logic in `auth.py`.

### Logout Endpoint

NASA Launchpad may provide an end session endpoint. If available, the `logout()` function in `auth.py` can be enhanced to call this endpoint.

## Support

For issues specific to:
- **NASA Launchpad OAuth**: Contact NASA IT support
- **SAGE Application**: Contact JSC EC4
- **Streamlit OAuth Library**: See https://github.com/dnplus/streamlit-oauth

## File Structure

```
SAGE_URI/
├── pdf-rag-streamlit.py          # Main application with authentication
├── auth.py                        # Authentication module
├── requirements.txt               # Python dependencies
├── .streamlit/
│   ├── secrets.toml              # OAuth credentials (DO NOT COMMIT)
│   └── config.toml               # Streamlit SSL configuration
├── ssl/
│   ├── cert.pem                  # SSL certificate
│   └── key.pem                   # SSL private key
└── SETUP_AUTH.md                 # This file
```

## Next Steps

After successful authentication setup:

1. Test the authentication flow thoroughly
2. Verify user information is displayed correctly
3. Test the logout functionality
4. Consider implementing token refresh for longer sessions
5. Add error handling for edge cases
6. Implement audit logging for security compliance
7. Plan for production deployment with proper SSL certificates
