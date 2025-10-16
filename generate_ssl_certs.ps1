# SSL Certificate Generation Script for SAGE (Windows PowerShell)
# Generates self-signed SSL certificates for localhost development

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "SAGE - SSL Certificate Generator" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Create ssl directory if it doesn't exist
if (-not (Test-Path "ssl")) {
    New-Item -ItemType Directory -Path "ssl" | Out-Null
}

# Check if certificates already exist
if ((Test-Path "ssl\cert.pem") -and (Test-Path "ssl\key.pem")) {
    Write-Host "⚠️  SSL certificates already exist in ssl\ directory" -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "Do you want to regenerate them? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Keeping existing certificates."
        exit 0
    }
    Write-Host "Regenerating certificates..." -ForegroundColor Yellow
    Write-Host ""
}

# Check if OpenSSL is available
$opensslPath = Get-Command openssl -ErrorAction SilentlyContinue

if (-not $opensslPath) {
    Write-Host "❌ Error: OpenSSL not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install OpenSSL for Windows:" -ForegroundColor Yellow
    Write-Host "  Option 1: Download from https://slproweb.com/products/Win32OpenSSL.html"
    Write-Host "  Option 2: Install via Chocolatey: choco install openssl"
    Write-Host "  Option 3: Install via Scoop: scoop install openssl"
    Write-Host ""
    Write-Host "Alternatively, use the built-in PowerShell method (see SETUP_AUTH.md)"
    Write-Host ""
    exit 1
}

# Generate self-signed certificate using OpenSSL
Write-Host "Generating self-signed SSL certificate for localhost..." -ForegroundColor Green
Write-Host ""

$subject = "/C=US/ST=Texas/L=Houston/O=NASA JSC/OU=EC4/CN=localhost"
$san = "subjectAltName=DNS:localhost,IP:127.0.0.1"

& openssl req -x509 -newkey rsa:4096 `
    -keyout ssl\key.pem `
    -out ssl\cert.pem `
    -days 365 `
    -nodes `
    -subj $subject `
    -addext $san

# Check if generation was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ SSL certificates generated successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Certificate files:" -ForegroundColor Cyan
    Write-Host "  - ssl\cert.pem (Certificate)"
    Write-Host "  - ssl\key.pem (Private Key)"
    Write-Host ""
    Write-Host "Certificate details:" -ForegroundColor Cyan
    & openssl x509 -in ssl\cert.pem -noout -subject -dates
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "IMPORTANT: Browser Security Warnings" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Since this is a self-signed certificate, your browser will show"
    Write-Host "a security warning when you access https://localhost:8501"
    Write-Host ""
    Write-Host "To proceed:" -ForegroundColor Yellow
    Write-Host "  Chrome/Edge: Click 'Advanced' → 'Proceed to localhost (unsafe)'"
    Write-Host "  Firefox: Click 'Advanced' → 'Accept the Risk and Continue'"
    Write-Host ""
    Write-Host "This is normal for development and safe for localhost."
    Write-Host ""
    Write-Host "For a better experience without warnings, consider using mkcert:" -ForegroundColor Cyan
    Write-Host "  See SETUP_AUTH.md for instructions"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Error: Failed to generate SSL certificates" -ForegroundColor Red
    Write-Host ""
    exit 1
}
