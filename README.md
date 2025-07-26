# Bangla RAG QA System

A Retrieval-Augmented Generation (RAG) system for answering English and Bangla queries from the HSC26 Bangla 1st Paper. The system supports robust document chunking, semantic vector search, and answer generation via an LLM.

---

## 🚀 Setup Guide

**Requirements:**
- Python 3.10+ (recommended)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) with Bangla language pack
- [Poppler](https://github.com/oschwartz10612/poppler-windows/releases/) (for pdf2image)
- All dependencies in `requirements.txt`

**Steps:**
1. Clone the repo:
    ```sh
    git clone https://github.com/Tashin2098/Bangla-rag-QA.git
    cd Bangla-rag-QA
    ```
2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    venv\Scripts\activate  # (Windows) or source venv/bin/activate (Linux/Mac)
    ```
3. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```
4. Install and configure Tesseract OCR and Poppler.  
   Ensure their paths are correct in `extract_chunks.py`.
5. Run chunk extraction:
    ```sh
    python extract_chunks.py
    ```
6. Build the vector store:
    ```sh
    python build_vector_store.py
    ```
7. Start Ollama (ensure the `llama3` model is pulled) and run the API:
    ```sh
    ollama run llama3
    python -m uvicorn app:app --reload
    ```

---

## 🛠️ Used Tools, Libraries & Packages

- **OCR & PDF:** `pytesseract`, `pdf2image`, `poppler`
- **NLP:** `sentence-transformers` (paraphrase-multilingual-MiniLM-L12-v2)
- **Vector DB:** `chromadb`
- **Web API:** `FastAPI`, `Uvicorn`
- **LLM:** `llama3` (served locally via [Ollama](https://ollama.com/))
- **Utility:** `requests`, `re`, `os`, `json`, `pillow`

---

## 💬 Sample Queries and Outputs

**Bangla:**
> **Q:** অনুপমের ভাষায় সুপুরুষ কাকে বলা হয়েছে?  
> **A:** শস্তুনাথবাবু

> **Q:** কাকে অনুপমের ভাগ্যদেবতা বলে উল্লেখ করা হয়েছে?  
> **A:** মামা

**English:**
> **Q:** Who is mentioned as Anupam’s "fortune deity"?  
> **A:** Mama

---

## 📝 API Documentation

### POST `/ask`

**Request:**
```json
{ "query": "অনুপমের ভাষায় সুপুরুষ কাকে বলা হয়েছে?" }
Response:
{
  "answer": "শস্তুনাথবাবু",
  "contexts": [
    "কন্যার পিতা শস্তুনাথবাবু হরিশকে কত বিশ্বাস করেন তাহার প্রমাণ এই যে, বিবাহের তিন দিন পূর্বে তিনি আমাকে চক্ষে দেখেন এবং আশীর্বাদ করিয়া যান... সুপুরুষ বটে ... ভিড়ের মধ্যে দেখিলে সকলের আগে তার উপরে চোখ পড়িবার মতো চেহারা।"
  ]
}
