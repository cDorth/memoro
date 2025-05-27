# 🧠 Memoro – Memória Artificial Pessoal

Memoro é um sistema inteligente e pessoal de organização de ideias e anotações. Utiliza **IA, OCR, busca semântica e uma timeline interativa** para ajudar você a capturar, entender e recuperar seus pensamentos com facilidade.

---

## 🎯 Propósito

> Um repositório pessoal de ideias com inteligência artificial.  
> Esqueça notas perdidas — **Memoro pensa com você.**

Ideal para:
- Criativos que registram ideias espontâneas
- Estudantes e pesquisadores que desejam consultar resumos
- Profissionais que precisam acessar conteúdos passados com rapidez

---

## 🧩 Funcionalidades

### ✅ Criação de Anotações
- Inserção de textos livres
- Upload de **imagens com OCR** para extração de texto
- Resumo automático com IA (OpenRouter)
- Extração automática de tags com IA

### 🔍 Busca Semântica
- Busca inteligente por **significado**, não apenas por palavras-chave
- Realizada com embeddings + FAISS

### 🗓 Visualização em Timeline
- Agrupamento de anotações por data
- Interface amigável com rolagem automática

### ✏️ Edição e Exclusão
- Editar conteúdo, tags e resumo
- Deletar com segurança e confirmação

### 📤 Exportação
- Salve suas anotações em `.txt` com um clique

---

## 🛠 Tecnologias Utilizadas

| Tecnologia        | Função                                        |
|------------------|-----------------------------------------------|
| **Python**       | Lógica principal do sistema                   |
| **Flet**         | Criação da interface visual (UI)              |
| **SQLite**       | Armazenamento local leve                      |
| **Tesseract OCR**| Extração de texto de imagens                  |
| **OpenRouter**   | API de IA para resumo, tags e embeddings      |
| **FAISS**        | Busca semântica vetorial                      |
| **dotenv**       | Gestão segura da API Key                      |

---

## 📦 Estrutura do Projeto

```
memoro/
├── app/
│   ├── main.py           # Interface com Flet
│   ├── ia.py             # Funções com OpenRouter e OCR
│   ├── db.py             # Operações com SQLite
│   ├── embeddings.py     # Busca semântica com FAISS
├── .env                  # Chave de API OpenRouter
├── requirements.txt      # Dependências do projeto
```

---

## 🚀 Como Executar

### 1. Clone o repositório
```bash
git clone https://github.com/cDorth/memoro.git
cd memoro
```

### 2. Crie o ambiente virtual
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o arquivo `.env`
Crie um arquivo `.env` na raiz com a seguinte linha:
```
OPEN_API_KEY=sk-or-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 5. Instale o Tesseract OCR
- [Instalar para Windows (recomendado: versão UB Mannheim)](https://github.com/UB-Mannheim/tesseract/wiki)
- Configure o caminho correto no `ia.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

### 6. Execute o sistema
```bash
python app/main.py
```

---

## 📌 Requisitos

- Python 3.10+
- Tesseract OCR instalado
- Conexão com a internet (para uso da IA via OpenRouter)

---

## 💡 Sugestões Futuras

- Suporte a múltiplos usuários
- Exportação em Markdown ou PDF
- Backup em nuvem
- Suporte a áudio (transcrição)

---

## 📄 Licença

Este projeto é de código aberto e gratuito para uso pessoal e educacional.

---
