RAG QA System for Bangla & English (HSC26 Bangla 1st Paper)
Overview
A Retrieval-Augmented Generation (RAG) system that answers queries in Bangla and English using a vectorized knowledge base built from HSC26 Bangla 1st Paper. Features semantic and keyword retrieval, REST API, and evaluation metrics.

# Setup Guide
Clone the repository
 1. git clone https://github.com/Tashin2098/Bangla-RAG-QA.git
 2. cd Bangla-RAG-QA

Create a Virtual Environment (Recommended)
1. python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install Python Dependencies

1. pip install -r requirements.txt

# Install Tesseract OCR and Poppler

- Tesseract OCR (with Bangla language)
Download and install from:
https://github.com/tesseract-ocr/tesseract
Add to PATH or specify the path in your script.
Make sure Bangla language data (ben.traineddata) is present.
- Poppler for Windows
Download from:
https://github.com/oschwartz10612/poppler-windows/releases/
Extract and note the bin directory path (e.g., C:\path\to\poppler\bin).

# Used Tools, Libraries, Packages:
PyTesseract: OCR for extracting Bangla text from scanned PDF

pdf2image: Convert PDF pages to images

SentenceTransformers: For multilingual (Bangla+English) text embedding

ChromaDB: Vector database for efficient semantic retrieval

FastAPI: For building REST API

Uvicorn: ASGI server for FastAPI

Ollama (Llama3 model): For answer generation from retrieved context

# Extract and Chunk PDF Content

-Set the paths for Poppler and Tesseract in extract_chunks.py as per your system.
-Place the HSC26-Bangla1st-Paper.pdf file in the data/ folder.
-Run the extraction and chunking script:
 1. python extract_chunks.py

# Build the Vector Store
 1. python build_vector_store.py

# Start the API Server
 1. python -m uvicorn app:app --reload
 2. The API will be live at: http://127.0.0.1:8000/docs

# API Documentation
curl -X 'POST' \
  'http://127.0.0.1:8000/ask' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "অনুপমের ভাষায় সুপুরুষ কাকে বলা হয়েছে?"
}'

Request URL
http://127.0.0.1:8000/ask

	
Response body
Download
{
  "answer": "শস্তুনাথবাবু\" ,
  "contexts": [
    "কন্যার পিতা শস্তুনাথবাবু হরিশকে কত বিশ্বাস করেন তাহার প্রমাণ এই যে, বিবাহের তিন দিন পূর্বে তিনি আমাকে চক্ষে দেখেন এবং আশীর্বাদ করিয়া যান। বয়স তীর চল্লিশের কিছু এপারে বা ওপারে। চুল কীচা, গোঁফে পাক ধরিতে আরম্ভ করিয়াছে মাত্র। সুপুরুষ বটে। ভিড়ের মধ্যে দেখিলে সকলের আগে তার উপরে চোখ পড়িবার মতো চেহারা।" 
]
}  
  


## Evaluation Matrix

| Query                                      | Expected       | Answer         | Correct | Grounded | Relevance |
|---------------------------------------------|----------------|----------------|---------|----------|-----------|
| অনুপমের ভাষায় সুপুরুষ কাকে বলা হয়েছে?       |    শস্তুনাথবাবু   | শস্তুনাথবাবু       |  ✔️    |	✔️   |  High     |
| কাকে অনুপমের ভাগ্যদেবতা বলে উল্লেখ করা হয়েছে?|    মামা         |  মামা         |  ✔️    |     ✔️   |  High     |


# What method or library did you use to extract the text, and why? Did you face any formatting challenges with the PDF content?
Answer:
I used a combination of pdf2image (with Poppler) to convert each page of the PDF into high-resolution images, and pytesseract (Tesseract OCR with Bangla language data) to extract Bangla text from those images.
This approach was chosen because direct PDF-to-text extraction methods often fail with complex formatting or scanned Bangla books. OCR ensures more reliable extraction from printed Bengali literature.
The main challenge was removing irrelevant page decorations (like page numbers, watermarks, etc.) and cleaning up OCR artifacts.

# What chunking strategy did you choose (e.g. paragraph-based, sentence-based, character limit)? Why do you think it works well for semantic retrieval?
Answer:
I used paragraph-based chunking, splitting text by double newlines or paragraph breaks.
This method preserves context better than sentence-level or fixed-length chunking, which is crucial for semantic retrieval: questions about characters or narrative events are more likely to be answered correctly when whole paragraphs are kept together.

# What embedding model did you use? Why did you choose it? How does it capture the meaning of the text?
Answer:
I used sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 for sentence/paragraph embeddings.
This model is trained on multiple languages, including Bangla and English, and produces dense vector representations that encode the semantic meaning of text.
It is lightweight (fast) yet accurate for both Bangla and English queries, and works well with ChromaDB for similarity search.

# How are you comparing the query with your stored chunks? Why did you choose this similarity method and storage setup?
Answer:
Each chunk and each query is encoded as a vector embedding. For every query, the top-N most similar chunks are retrieved using cosine similarity search in ChromaDB.
Cosine similarity is standard for comparing dense text embeddings and ChromaDB is a fast, modern, Python-native vector database ideal for this RAG use-case.

# How do you ensure that the question and the document chunks are compared meaningfully? What would happen if the query is vague or missing context?
Answer:
To ensure meaningful comparison, I combine keyword-based filtering (extracting nouns and key-terms from the query) with semantic similarity search.

First, chunks containing important query terms are prioritized.
Then, semantically similar chunks (even if keywords don’t match exactly) are included.
The prompt to the LLM is strict: it’s told to answer ONLY if a clear, direct answer is present in the chunks.

If the query is vague or missing context, the system may return উত্তর পাওয়া যায়নি (no answer found), or may select the closest match available in the corpus.

# Do the results seem relevant? If not, what might improve them (e.g. better chunking, better embedding model, larger document)?
Answer:
In most sample and real-world queries, the results are highly relevant and grounded in the retrieved context.
If relevance is low, further improvements can be made by:
Using a Bangla-specific embedding model (if available)
Improving OCR/cleaning
Finer-tuning chunk size (sometimes overlap helps)
Training or prompt-tuning the LLM for even stricter factual extraction


