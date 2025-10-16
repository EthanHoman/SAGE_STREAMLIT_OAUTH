#!/bin/bash

# Script to prepare SAGE project for transfer to NASA laptop
# This excludes large/unnecessary files

echo "Preparing SAGE project for transfer..."

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create transfer package
TRANSFER_DIR="../SAGE_URI_TRANSFER"
mkdir -p "$TRANSFER_DIR"

echo "Copying project files..."

# Copy essential files
cp -r . "$TRANSFER_DIR/"

# Remove unnecessary directories
echo "Removing unnecessary files..."
rm -rf "$TRANSFER_DIR/venv"
rm -rf "$TRANSFER_DIR/__pycache__"
rm -rf "$TRANSFER_DIR/chroma_db"
rm -rf "$TRANSFER_DIR/.git" 2>/dev/null

# Create a README for transfer
cat > "$TRANSFER_DIR/TRANSFER_README.txt" << 'EOF'
SAGE - Transfer Package for NASA Laptop
========================================

IMPORTANT: Before running on NASA laptop:

1. Install Python 3.9+
2. Create virtual environment: python3 -m venv venv
3. Activate: source venv/bin/activate (Mac/Linux) or venv\Scripts\activate (Windows)
4. Install: pip install -r requirements.txt
5. Configure .streamlit/secrets.toml with NASA OAuth credentials
6. Verify SSL certificates in ssl/ directory
7. Run: streamlit run pdf-rag-streamlit.py

Contact NASA IT to obtain OAuth Client ID and Secret for Launchpad.

See SETUP_AUTH.md for detailed instructions.
EOF

echo "Creating zip archive..."
cd ..
zip -r SAGE_URI_TRANSFER.zip SAGE_URI_TRANSFER/

echo ""
echo "✓ Transfer package created: ../SAGE_URI_TRANSFER.zip"
echo "✓ Transfer this file to your NASA laptop"
echo ""
echo "On NASA laptop:"
echo "  1. Extract: unzip SAGE_URI_TRANSFER.zip"
echo "  2. Follow instructions in TRANSFER_README.txt"
echo ""
