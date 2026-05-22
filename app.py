from flask import Flask, request, jsonify
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
import requests
import os
import base64
import io

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY", "")
VERSION = "1.3.0"

def check_auth(req):
    if not API_KEY:
        return True
    return req.headers.get("x-api-key") == API_KEY

def extract_text_from_bytes(pdf_bytes, max_pages=20):
    """Extrai texto do PDF usando pdfminer (leve em memoria)"""
    laparams = LAParams()
    text = extract_text(
        io.BytesIO(pdf_bytes),
        laparams=laparams,
        maxpages=max_pages
    )
    return text

@app.route("/", methods=["GET", "HEAD"])
def index():
    return jsonify({"status": "ok", "version": VERSION, "service": "pdf-reader-api"})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "version": VERSION})

@app.route("/extract-url", methods=["POST"])
def extract_url():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "Campo 'url' obrigatorio"}), 400
    url = data["url"]
    max_pages = int(data.get("max_pages", 20))
    try:
        resp = requests.get(url, timeout=30, stream=True)
        resp.raise_for_status()
        # Limite de 30MB para evitar estouro de memoria
        content = b""
        for chunk in resp.iter_content(chunk_size=65536):
            content += chunk
            if len(content) > 30 * 1024 * 1024:
                break
        text = extract_text_from_bytes(content, max_pages=max_pages)
        return jsonify({"text": text, "pages_extracted": max_pages, "version": VERSION})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/extract-base64", methods=["POST"])
def extract_base64():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    if not data or "pdf_base64" not in data:
        return jsonify({"error": "Campo 'pdf_base64' obrigatorio"}), 400
    max_pages = int(data.get("max_pages", 20))
    try:
        pdf_bytes = base64.b64decode(data["pdf_base64"])
        # Limite de 30MB
        if len(pdf_bytes) > 30 * 1024 * 1024:
            return jsonify({"error": "PDF muito grande (max 30MB)"}), 413
        text = extract_text_from_bytes(pdf_bytes, max_pages=max_pages)
        return jsonify({"text": text, "pages_extracted": max_pages, "version": VERSION})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/extract", methods=["POST"])
def extract_upload():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    file = request.files["file"]
    max_pages = int(request.form.get("max_pages", 20))
    try:
        pdf_bytes = file.read()
        if len(pdf_bytes) > 30 * 1024 * 1024:
            return jsonify({"error": "PDF muito grande (max 30MB)"}), 413
        text = extract_text_from_bytes(pdf_bytes, max_pages=max_pages)
        return jsonify({"text": text, "pages_extracted": max_pages, "version": VERSION})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
