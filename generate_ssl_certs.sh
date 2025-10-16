#!/bin/bash

# SSL Certificate Generation Script for SAGE
# Generates self-signed SSL certificates for localhost development

echo "=========================================="
echo "SAGE - SSL Certificate Generator"
echo "=========================================="
echo ""

# Create ssl directory if it doesn't exist
mkdir -p ssl

# Check if certificates already exist
if [ -f "ssl/cert.pem" ] && [ -f "ssl/key.pem" ]; then
    echo "⚠️  SSL certificates already exist in ssl/ directory"
    echo ""
    read -p "Do you want to regenerate them? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing certificates."
        exit 0
    fi
    echo "Regenerating certificates..."
    echo ""
fi

# Generate self-signed certificate
echo "Generating self-signed SSL certificate for localhost..."
echo ""

openssl req -x509 -newkey rsa:4096 \
    -keyout ssl/key.pem \
    -out ssl/cert.pem \
    -days 365 \
    -nodes \
    -subj "/C=US/ST=Texas/L=Houston/O=NASA JSC/OU=EC4/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

# Check if generation was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✓ SSL certificates generated successfully!"
    echo ""
    echo "Certificate files:"
    echo "  - ssl/cert.pem (Certificate)"
    echo "  - ssl/key.pem (Private Key)"
    echo ""
    echo "Certificate details:"
    openssl x509 -in ssl/cert.pem -noout -subject -dates
    echo ""
    echo "=========================================="
    echo "IMPORTANT: Browser Security Warnings"
    echo "=========================================="
    echo ""
    echo "Since this is a self-signed certificate, your browser will show"
    echo "a security warning when you access https://localhost:8501"
    echo ""
    echo "To proceed:"
    echo "  Chrome/Edge: Click 'Advanced' → 'Proceed to localhost (unsafe)'"
    echo "  Firefox: Click 'Advanced' → 'Accept the Risk and Continue'"
    echo "  Safari: Click 'Show Details' → 'visit this website'"
    echo ""
    echo "This is normal for development and safe for localhost."
    echo ""
    echo "For a better experience without warnings, consider using mkcert:"
    echo "  See SETUP_AUTH.md for instructions"
    echo ""
else
    echo ""
    echo "❌ Error: Failed to generate SSL certificates"
    echo ""
    echo "Please ensure OpenSSL is installed:"
    echo "  macOS: brew install openssl"
    echo "  Ubuntu/Debian: sudo apt-get install openssl"
    echo "  Windows: Download from https://slproweb.com/products/Win32OpenSSL.html"
    echo ""
    exit 1
fi
