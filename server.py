import sys
import os
import json
import tempfile
import subprocess
import shlex
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import urllib.request
import zipfile
import shutil

# Detect environment
IS_PRODUCTION = os.environ.get('RENDER', '') or os.environ.get('RAILWAY', '') or os.environ.get('RAILWAY_SERVICE_ID', '')
if IS_PRODUCTION:
    COMPILER_DIR = os.path.join(os.path.dirname(__file__), 'RAC-Compiler')
else:
    COMPILER_DIR = r"C:\Users\ADMIN\Downloads\RAC-Compiler-main\RAC-Compiler-main"

# Auto-download compiler if missing
def ensure_compiler():
    if os.path.exists(os.path.join(COMPILER_DIR, 'lib', 'main.py')):
        return True
    try:
        print("Downloading RAC-Compiler...")
        base = os.path.dirname(__file__)
        zip_path = os.path.join(base, 'compiler.zip')
        urllib.request.urlretrieve(
            'https://github.com/luongvantam/RAC-Compiler/archive/refs/heads/main.zip',
            zip_path
        )
        extract_dir = os.path.join(base, 'RAC-Compiler-main')
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(base)
        if os.path.exists(COMPILER_DIR):
            shutil.rmtree(COMPILER_DIR)
        os.rename(
            os.path.join(base, 'RAC-Compiler-main'),
            COMPILER_DIR
        )
        os.remove(zip_path)
        print("RAC-Compiler downloaded successfully!")
        return True
    except Exception as e:
        print(f"Failed to download compiler: {e}")
        return False

ensure_compiler()

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route("/compile", methods=["POST"])
def compile_code():
    data = request.get_json()
    code = data.get("code", "")
    model = data.get("model", "580vnx")

    if model not in ("580vnx", "880btg"):
        return jsonify({"success": False, "error": "Invalid model"}), 400

    rsc_dir = os.path.join(COMPILER_DIR, "rsc_ropchain")
    os.makedirs(rsc_dir, exist_ok=True)

    tmp_name = "_web_tmp"
    tmp_file = os.path.join(rsc_dir, tmp_name + ".rsc")
    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write(code)

    try:
        proc = subprocess.run(
            [sys.executable, "-u", os.path.join(COMPILER_DIR, "lib", "main.py"), model, tmp_name],
            cwd=COMPILER_DIR,
            capture_output=True,
            text=True,
            timeout=30
        )

        stdout = proc.stdout
        stderr = proc.stderr

        if proc.returncode != 0:
            return jsonify({
                "success": False,
                "error": stderr.strip() or stdout.strip(),
                "stdout": stdout,
                "stderr": stderr
            })

        lines = stdout.split("\n")
        output_lines = []
        capture = False
        for line in lines:
            if line.startswith("===") and "->" in line:
                capture = True
                continue
            if line.startswith("======"):
                capture = False
                continue
            if capture:
                output_lines.append(line)

        hex_output = " ".join(output_lines).strip()

        return jsonify({
            "success": True,
            "hex": hex_output,
            "stdout": stdout,
            "stderr": stderr
        })

    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "error": "Compiler timed out"}), 504
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if os.path.exists(tmp_file):
            os.remove(tmp_file)

@app.route("/samples", methods=["GET"])
def list_samples():
    rsc_dir = os.path.join(COMPILER_DIR, "rsc_ropchain")
    if not os.path.exists(rsc_dir):
        return jsonify({"success": False, "error": "Directory not found"})
    files = sorted([f for f in os.listdir(rsc_dir) if f.endswith((".rsc", ".asm"))])
    return jsonify({"success": True, "files": files})

@app.route("/sample", methods=["GET"])
def get_sample():
    name = request.args.get("name", "")
    rsc_dir = os.path.join(COMPILER_DIR, "rsc_ropchain")
    filepath = os.path.join(rsc_dir, name)
    if not os.path.exists(filepath):
        return jsonify({"success": False, "error": "File not found"})
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return jsonify({"success": True, "content": content})

@app.route("/labels", methods=["GET"])
def get_labels():
    model = request.args.get("model", "580vnx")
    label_file = os.path.join(COMPILER_DIR, model, "labels.txt")
    if not os.path.exists(label_file):
        return jsonify({"success": False, "error": "File not found: " + label_file})
    with open(label_file, "r", encoding="utf-8") as f:
        content = f.read()
    return jsonify({"success": True, "content": content})

@app.errorhandler(404)
def not_found(e):
    return send_from_directory('.', 'index.html')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"Server starting... Compiler dir: {COMPILER_DIR}")
    print(f"Open http://127.0.0.1:{port} in browser")
    app.run(host="0.0.0.0", port=port, debug=not IS_PRODUCTION)
