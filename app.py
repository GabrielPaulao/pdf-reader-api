from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import requests
import io
import os

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY", "")

def check_auth(req):
    if not API_KEY:
        return True
    return req.headers.get("x-api-key") == API_KEY


@app.route("/", methods=["GET", "HEAD"])
def index():
    return jsonify({"status": "ok", "message": "PDF Reader API"})


@app.route("/health", methods=["GET", "HEAD"])
def health():
    return jsonify({"status": "ok", "version": "1.0.0"})


@app.route("/extract", methods=["POST"])
def extract_from_upload():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401

    file = request.files.get("pdf")
    if not file:
        return jsonify({"error": "Nenhum arquivo PDF enviado. Use o campo 'pdf'."}), 400

    try:
        data = file.read()
        doc = fitz.open(stream=data, filetype="pdf")
        pages = []
        for i, page in enumerate(doc):
            pages.append({
                "page": i + 1,
                "text": page.get_text().strip()
            })
        doc.close()
        return jsonify({
            "filename": file.filename,
            "total_pages": len(pages),
            "pages": pages
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/extract-url", methods=["POST"])
def extract_from_url():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401

    body = request.get_json()
    if not body or not body.get("url"):
        return jsonify({"error": "Informe o campo 'url' no body JSON."}), 400

    url = body["url"]
    page_number = body.get("page")

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()

        doc = fitz.open(stream=resp.content, filetype="pdf")
        pages = []
        for i, page in enumerate(doc):
            pages.append({
                "page": i + 1,
                "text": page.get_text().strip()
            })
        doc.close()

        if page_number is not None:
            match = [p for p in pages if p["page"] == page_number]
            if not match:
                return jsonify({"error": f"Pagina {page_number} nao encontrada."}), 404
            return jsonify({
                "url": url,
                "total_pages": len(pages),
                "page": match[0]
            })

        return jsonify({
            "url": url,
            "total_pages": len(pages),
            "pages": pages
        })
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Erro ao baixar PDF: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
