#!/bin/bash
set -e
echo "=== Installing dependencies ==="
pip install -r requirements.txt
echo "=== Downloading RAC-Compiler ==="
if [ ! -d "RAC-Compiler" ]; then
    git clone --depth 1 https://github.com/luongvantam/RAC-Compiler.git RAC-Compiler
fi
echo "=== Setup complete ==="
