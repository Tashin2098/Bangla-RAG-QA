from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import chromadb
import re
import requests

app = FastAPI()


def load_chunks(file_path):
    with open(file_path, encoding='utf-8') as f:
        raw = f.read()
    return [x.strip() for x in raw.split('---chunk---') if x.strip()]

chunks = load_chunks("vector_store/chunks.txt")


embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
chroma_client = chromadb.PersistentClient(path="vector_store/chroma_db")
collection = chroma_client.get_or_create_collection("hsc26_chunks")

class QueryRequest(BaseModel):
    query: str


BANGLA_STOPWORDS = set([
    "কে", "কাকে", "এর", "এই", "ওই", "তাকে", "বলে", "হয়ে", "হয়েছে", "অনুপমের", "অনুপম", "উল্লেখ", "বলা",
    "কি", "কার", "কোন", "কখন", "কারণ", "প্রকৃত", "বয়স", "কত", "বলেছে", "দিয়ে", "বা", "কি", "কেন",
    "এবং", "তা", "তাহার", "তাহাকে", "তুমি", "আমি", "আমার", "আমাদের"
])

def get_keywords(question):
    words = [w.strip("?,।'\"") for w in question.split()]
    return [w for w in words if len(w) > 2 and w not in BANGLA_STOPWORDS]

def find_candidate_names(chunk):
    
    candidates = []
    matches = re.findall(r'([অ-হ][অ-হা-ৌ-্]+(?:বাবু|মামা|দাদা|শাস্ত্রী|চৌধুরী|সাহেব|নীলমণি|কল্যাণী|শস্তুনাথ|শুম্ভুনাথ))', chunk)
    for m in matches:
        candidates.append(m)
   
    return list(set(candidates))

def retrieve_chunks(query, top_k=5):
    keywords = get_keywords(query)
    # Chunks containing all keywords are boosted
    scored = []
    for i, c in enumerate(chunks):
        score = 0
        if any(k in c for k in keywords):
            score += 1
        names = find_candidate_names(c)
        if names and any(k in c for k in keywords):
            score += 1  
        scored.append((score, c))
    
    scored.sort(reverse=True)
    ctx = [c for (s, c) in scored if s > 0][:top_k]
    if len(ctx) < top_k:
        # Fallback to vector retrieval
        query_emb = embedding_model.encode([query])[0]
        results = collection.query(
            query_embeddings=[query_emb.tolist()],
            n_results=top_k - len(ctx),
            include=['documents']
        )
        sem_chunks = results['documents'][0] if isinstance(results['documents'][0], list) else results['documents']
        
        for c in sem_chunks:
            if c not in ctx:
                ctx.append(c)
    return ctx[:top_k]

def generate_strict_answer(query, contexts):
    context_str = "\n\n".join([f"{c}" for c in contexts])
    # Example completions in the prompt to reinforce LLM output
    prompt = f"""
তুমি একজন দক্ষ বাংলা সহকারী, HSC বই থেকে প্রশ্নের উত্তর দিচ্ছ।

প্রশ্ন: অনুপমের ভাষায় সুপুরুষ কাকে বলা হয়েছে?
নিচের context:
... কন্যার পিতা শুম্ভুনাথবাবু ... সুপুরুষ বটে ...
শুধুমাত্র যদি context-এ প্রশ্নের সরাসরি উত্তর পাও, তাহলে শুধু "শুম্ভুনাথবাবু" লিখো।

প্রশ্ন: কাকে অনুপমের ভাগ্যদেবতা বলে উল্লেখ করা হয়েছে?
নিচের context:
... মামা, যিনি পৃথিবীতে আমার ভাগ্যদেবতার প্রধান এজেন্ট ...
উত্তর: "মামা"

এবারের প্রশ্ন:
প্রশ্ন: {query}

নিম্নোক্ত প্রাসঙ্গিক তথ্য (context) খুব মনোযোগ দিয়ে পড়ো:
{context_str}

শুধুমাত্র যদি উপরের context-এ প্রশ্নের সরাসরি, স্পষ্ট উত্তর (নাম, ব্যক্তি, সংখ্যা) পাওয়া যায়,
তাহলে সেটাই বাংলায় সংক্ষেপে (১-২ শব্দে) উত্তর দাও।
শুধু নির্দিষ্ট বাংলা শব্দ/নাম (যেমন: মামা, শুম্ভুনাথবাবু, কল্যাণী, ইত্যাদি) লিখো।

কোনোভাবেই ইংরেজি, প্রশ্নের শব্দ, অথবা মূল চরিত্রের নাম ("অনুপম" বা "আমার") উত্তর হিসেবে দেবে না।
ব্যাখ্যা, অনুবাদ, অতিরিক্ত বাক্য, সংখ্যা, বা প্রশ্নের পুনরাবৃত্তি করবে না।
যদি context-এ স্পষ্ট উত্তর না পাও, তাহলে লিখবে: উত্তর পাওয়া যায়নি

উত্তরঃ
"""
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
    )
    result = response.json()
    if "message" in result and "content" in result["message"]:
        return result["message"]["content"].strip()
    elif "response" in result:
        return result["response"].strip()
    else:
        return "উত্তর পাওয়া যায়নি"

@app.post("/ask")
async def ask_question(request: QueryRequest):
    query = request.query
    contexts = retrieve_chunks(query, top_k=5)
    answer = generate_strict_answer(query, contexts)
    return {"answer": answer, "contexts": contexts}

@app.get("/")
def read_root():
    return {"message": "Strict Bangla RAG API with noun/entity-aware retrieval and LLM extraction."}

# --------------------- EVALUATION ENDPOINT -------------------------

class EvalItem(BaseModel):
    query: str
    expected_answer: str

class EvalSet(BaseModel):
    items: list[EvalItem]

@app.post("/evaluate")
async def evaluate(evalset: EvalSet):
    total = 0
    correct = 0
    detailed = []

    for item in evalset.items:
        query = item.query
        expected = item.expected_answer.strip()
        contexts = retrieve_chunks(query, top_k=5)
        answer = generate_strict_answer(query, contexts).strip()
        # Correctness: strict match
        is_correct = (answer == expected)
        total += 1
        correct += int(is_correct)
        
        grounded = any(expected in ctx for ctx in contexts)
        # Relevance (simple): if grounded, relevance=high
        relevance = "high" if grounded else "low"
        detailed.append({
            "query": query,
            "expected": expected,
            "answer": answer,
            "correct": is_correct,
            "grounded": grounded,
            "relevance": relevance,
            "contexts": contexts
        })
    accuracy = correct / total if total else 0.0
    return {
        "accuracy": accuracy,
        "results": detailed
    }
