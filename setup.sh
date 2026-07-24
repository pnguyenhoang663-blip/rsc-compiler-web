#!/bin/bash
# Clone RAC Compiler if not exists
if [ ! -d "RAC-Compiler" ]; then
    git clone --depth 1 https://github.com/luongvantam/RAC-Compiler.git RAC-Compiler
fi
pip install -r requirements.txt
echo "Setup complete!"
