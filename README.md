# Bangla RAG QA System

A Retrieval-Augmented Generation (RAG) system for answering English and Bangla queries from the HSC26 Bangla 1st Paper. The system supports robust document chunking, semantic vector search, and answer generation via an LLM.

---

## Setup Guide

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

##  Used Tools, Libraries & Packages

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

##  API Documentation

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
Explanation:
The API retrieves the most semantically relevant chunk, passes it with the query to the LLM, and the LLM is prompted to output a single Bangla word or name, not an explanation or translation. This ensures answers are concise, contextually grounded, and in the correct language.
```
## Evaluation Matrix

| Query                                      | Expected       | Answer         | Correct | Grounded | Relevance |
|---------------------------------------------|----------------|----------------|---------|----------|-----------|
| অনুপমের ভাষায় সুপুরুষ কাকে বলা হয়েছে?    | শস্তুনাথবাবু   | শস্তুনাথবাবু   | ✔️      | ✔️       | High      |
| কাকে অনুপমের ভাগ্যদেবতা বলে উল্লেখ করা হয়েছে? | মামা           | মামা           | ✔️      | ✔️       | High      |

# Submission Questions & Answers
# 1. What method or library did you use to extract the text, and why? Did you face any formatting challenges with the PDF content?
# Answer:
I used pytesseract with Tesseract OCR (configured for Bangla) and pdf2image (with Poppler) to extract text from the scanned PDF pages.
Formatting challenges: Yes, the original PDF had noisy footers and inconsistent line breaks. I cleaned repetitive page decorations (“কল আললাইন ব্যাচ”, etc.) via post-processing, and grouped lines into paragraphs for coherent chunking.

# 2. What chunking strategy did you choose (e.g. paragraph-based, sentence-based, character limit)? Why do you think it works well for semantic retrieval?
# Answer:
I used paragraph-based chunking. Each chunk represents a semantically complete thought, so the retrieval step can return full context for a query. This avoids returning too little context (as in sentence-based) or splitting answers (as in character limits), improving retrieval accuracy.

# 3. What embedding model did you use? Why did you choose it? How does it capture the meaning of the text?
# Answer:
I used sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2, a strong multilingual sentence embedding model.
It supports both English and Bangla, and captures semantic meaning—so similar questions and answers are embedded closely in vector space, even if not identical in wording.

# 4. How are you comparing the query with your stored chunks? Why did you choose this similarity method and storage setup?
# Answer:
Queries and chunks are both embedded with the same model.
Similarity is measured as cosine similarity via ChromaDB, which is efficient for nearest-neighbor search at scale. ChromaDB’s persistent vector storage enables easy retrieval and updating.

# 5. How do you ensure that the question and the document chunks are compared meaningfully? What would happen if the query is vague or missing context?
# Answer:
Both the query and each chunk are embedded in the same semantic space, so the model retrieves the most contextually similar chunk, not just literal matches. If a query is vague, the system may return less relevant chunks or answer "উত্তর পাওয়া যায়নি" if no answer is found in the retrieved contexts.

# 6. Do the results seem relevant? If not, what might improve them (e.g. better chunking, better embedding model, larger document)?
# Answer:
Yes, results are generally relevant when the question is clear and the answer exists in the document.
Improvements could include:

Finer-grained chunking (but not too fine!)

Using a stronger Bangla-native embedding model

More advanced keyword extraction for ranking chunks

Improving OCR quality with better PDF scans




