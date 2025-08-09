# Insurance\_RAG

**A production-ready Retrieval-Augmented Generation (RAG) backend** built with **FastAPI**, **MongoDB**, and **Pinecone**.
It answers insurance-related queries based on provided documents with a **three-level caching system** for ultra-fast response times and reduced API costs.

---

## 🚀 Features

* **Multi-format Document Support**
  Handles **PDF, PPTX, Images, Excel, Word, TXT, HTML**.

  * **OCR fallback** using `pytesseract` for scanned or image-based documents.

* **Three-Level Caching Architecture**

  1. **Document cache** – Check if document embeddings already exist in Pinecone.
  2. **Exact Q\&A match** – Retrieve exact past answers from MongoDB.
  3. **Semantic cache** – Use Pinecone vector search to find similar past queries.

* **Vector Database Integration**

  * Stores document chunks and question-answer embeddings in **Pinecone**.
  * Each QA pair is stored with metadata for faster retrieval.

* **Async Question Processing**

  * Uses **OpenAI GPT-4o** for context-based answers.
  * Supports **tool usage**:

    * **Serper Search API** – for real-time web search.
    * **Fetch Tool** – perform GET requests for additional data.

* **Secure API**
  Bearer Token authentication for all endpoints.

---

## 📡 API Endpoints

### **`POST /hackrx/run`**

Process documents and answer questions.

**Request body:**

```json
{
  "documents": "https://hackrx.blob.core.windows.net/assets/......",
  "questions": [
    "When will my root canal claim of Rs 25,000 be settled?",
    "I have done an IVF for Rs 56,000. Is it covered?",
    "I did a cataract treatment of Rs 100,000. Will you settle the full Rs 100,000?",
    "Give me a list of documents to be uploaded for hospitalization for heart surgery."
  ]
}
```

**Flow:**

1. Check if document already exists in Pinecone.
2. If not, download → extract text → chunk → embed → store.
3. Process questions:

   * Check MongoDB for exact match.
   * If not found, search Pinecone for semantic match.
   * If still not found, query GPT-4o with retrieved context.
4. Store QA pairs in MongoDB and Pinecone.

---

### **`POST /clear_cache`**

Clears stored cache for testing or maintenance purposes.

---

## 🛠️ Installation & Setup

### **Local Setup**

```bash
# Clone the repo
git clone https://github.com/DebdipWritesCode/Insurance_RAG.git
cd Insurance_RAG

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Mac/Linux
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Run server
python main.py
```

### **Docker Setup**

```bash
docker build -t insurance_rag .
docker run -p 8000:8000 --env-file .env insurance_rag
```

---

## ⚙️ Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX_NAME=
PINECONE_HOST_NAME=
PINECONE_ENVIRONMENT=
EXPECTED_TOKEN=
MONGODB_URI=
DATABASE_NAME=
SERPER_API_KEY=
```

---

## 📦 Tech Stack

* **FastAPI** – API framework
* **MongoDB** – QA storage
* **Pinecone** – Vector database
* **OpenAI** – Embeddings & LLM (GPT-4o)
* **Pytesseract OCR** – Fallback for scanned documents
* **Serper Search API** – Web search
* **Docker** – Containerized deployment

---

## 📂 Project Structure

```
Insurance_RAG/
│── main.py              # FastAPI entry point
│── requirements.txt     # Dependencies
│── Dockerfile           # Docker build file
│── config/               # Helper functions
│── services/            # Embedding, OCR, and RAG logic
```

---

## 🔮 Future Improvements

* Support for streaming responses.
* Enhanced caching expiration policies.
* Support for additional file formats.

---

## 📄 License

This project is licensed under the MIT License.
