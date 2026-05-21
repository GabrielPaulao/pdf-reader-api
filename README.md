# 📄 PDF Reader API

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![PyMuPDF](https://img.shields.io/badge/PyMuPDF-1.x-orange?style=for-the-badge)
![License](https://img.shields.io/badge/Licença-MIT-blue?style=for-the-badge)

**API REST em Python para extrair texto de PDFs** — recebe um arquivo PDF via upload ou URL pública e retorna o texto de cada página em JSON.

Criada para ser usada em conjunto com o [mega-mcp-server](https://github.com/GabrielPaulao/mega-mcp-server), permitindo que o Perplexity leia o conteúdo real de PDFs armazenados no MEGA.

---

## 🛠️ Endpoints

### `GET /health`
Verifica se a API está no ar.

```json
{ "status": "ok", "version": "1.0.0" }
```

---

### `POST /extract`
Recebe um PDF via **upload de arquivo** e retorna o texto de todas as páginas.

**Content-Type:** `multipart/form-data`

| Campo | Tipo | Descrição |
|---|---|---|
| `pdf` | file | Arquivo PDF |

**Exemplo com curl:**
```bash
curl -X POST https://sua-api.onrender.com/extract \
  -H "x-api-key: SUA_CHAVE" \
  -F "pdf=@documento.pdf"
```

**Resposta:**
```json
{
  "filename": "documento.pdf",
  "total_pages": 3,
  "pages": [
    { "page": 1, "text": "Conteúdo da primeira página..." },
    { "page": 2, "text": "Conteúdo da segunda página..." }
  ]
}
```

---

### `POST /extract-url`
Recebe a **URL pública** de um PDF e retorna o texto. Aceita o parâmetro opcional `page` para retornar apenas uma página específica.

**Content-Type:** `application/json`

| Campo | Tipo | Descrição |
|---|---|---|
| `url` | string | URL pública do PDF |
| `page` | number? | Número da página (opcional) |

**Exemplo — todas as páginas:**
```bash
curl -X POST https://sua-api.onrender.com/extract-url \
  -H "x-api-key: SUA_CHAVE" \
  -H "Content-Type: application/json" \
  -d '{ "url": "https://link-publico.mega.nz/arquivo.pdf" }'
```

**Exemplo — apenas página 1:**
```bash
curl -X POST https://sua-api.onrender.com/extract-url \
  -H "x-api-key: SUA_CHAVE" \
  -H "Content-Type: application/json" \
  -d '{ "url": "https://link-publico.mega.nz/arquivo.pdf", "page": 1 }'
```

---

## ⚡ Deploy no Render (gratuito)

1. Acesse [render.com](https://render.com) e crie uma conta
2. **New** → **Web Service** → conecte este repositório
3. Configure:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. Em **Environment Variables**, adicione:
   - `API_KEY` → uma chave secreta (gere com `openssl rand -hex 32`)
5. Clique em **Deploy** — URL HTTPS gerada automaticamente ✅

> ⚠️ No plano gratuito do Render, o serviço **dorme após 15 min** sem uso. A primeira requisição pode demorar ~30s para "acordar".

---

## 💻 Rodando localmente

```bash
# Clone o repositório
git clone https://github.com/GabrielPaulao/pdf-reader-api.git
cd pdf-reader-api

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Configure o .env
cp .env.example .env
# Edite com sua API_KEY

# Rode
python app.py
# API disponível em: http://localhost:10000
```

---

## 🔒 Segurança

- Todos os endpoints podem ser protegidos com **API Key** via header `x-api-key`
- Se `API_KEY` não estiver definida no ambiente, os endpoints ficam abertos (apenas para desenvolvimento local)
- Nunca commite o `.env` — ele já está no `.gitignore`

---

## 📦 Tecnologias

| Pacote | Função |
|---|---|
| `PyMuPDF` | Extrai texto de PDFs com alta fidelidade |
| `Flask` | Servidor HTTP leve |
| `gunicorn` | Servidor WSGI para produção |
| `requests` | Download de PDFs via URL |

---

## 📄 Licença

MIT
