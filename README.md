# LegalRAG – Legal Knowledge Retrieval System

A Retrieval-Augmented Generation (RAG) based legal knowledge retrieval application designed to retrieve relevant Indian Supreme Court judgment passages and generate grounded answers to user queries.

The system combines semantic search, FAISS vector retrieval, sentence embeddings, and Gemini-based Large Language Models to provide context-aware answers from legal judgment documents.

---

## Project Overview

Legal documents are often lengthy and difficult to search manually. This project develops a domain-specific Retrieval-Augmented Generation (RAG) system that allows users to enter a legal case name and ask questions about the corresponding judgment.

The application retrieves relevant passages from Indian Supreme Court judgments using semantic similarity and provides a grounded response generated from the retrieved legal context.

The system is designed for **research and educational purposes** and should not be considered a substitute for professional legal advice.

---

## Objectives

The main objectives of this project are:

- Retrieve relevant legal judgment passages using semantic search.
- Build a domain-specific legal RAG pipeline.
- Use sentence embeddings to represent legal documents.
- Perform efficient similarity search using FAISS.
- Generate grounded answers using a Large Language Model.
- Reduce unsupported or hallucinated responses by restricting generation to retrieved context.
- Provide retrieved sources alongside generated answers for verification.
- Develop an interactive web interface using Flask.

---

## Dataset

### Jud-IPL – Indian Legal Judgement Prediction Dataset

The project uses the **Jud-IPL – Indian Legal Judgement Prediction Dataset** from Kaggle.

Dataset source:

https://www.kaggle.com/dsv/14441669

The dataset contains approximately **42,342 Supreme Court of India case documents**.

Important fields include:

- `name`
- `case_category`
- `case_type`
- `case_info`
- `judgement`
- `tokens`
- `sentences`
- `label`
- `proof_sentence`

The `judgement` field contains the raw judgment text used as the primary source for the RAG system.

> Note: The original dataset is not included in this GitHub repository because of its large file size.

---

# RAG Architecture

The system follows the following pipeline:


Legal Judgment Dataset
        │
        ▼
Data Cleaning
        │
        ▼
Document Preparation
        │
        ▼
Text Chunking
        │
        ▼
Sentence Transformer
(All-MiniLM-L6-v2)
        │
        ▼
Vector Embeddings
        │
        ▼
FAISS Vector Index
        │
        ▼
User Case Name + Question
        │
        ▼
Case-Specific Retrieval
        │
        ▼
Semantic Similarity Search
        │
        ▼
Relevant Judgment Context
        │
        ▼
Gemini LLM
        │
        ▼
Grounded Legal Answer
        │
        ▼
Retrieved Sources


## Installation
### 1. Clone the Repository
git clone https://github.com/debanjancal37/Legal-Document-RAG.git

Move into the project directory:
cd Legal-Document-RAG

### 2. Create a Virtual Environment
python -m venv .venv

Windows
.venv\Scripts\activate

macOS/Linux
source .venv/bin/activate

### 3. Install Dependencies
pip install -r requirements.txt

## Gemini API Configuration
The application requires a Gemini API key for answer generation.
Create an API key through Google AI Studio:
https://aistudio.google.com/app/apikey
Do not hard-code the API key inside the source code.
Set the following environment variable:
GEMINI_API_KEY=your_api_key_here

### PyCharm
In PyCharm:

Run
   ↓
Edit Configurations
   ↓
Environment Variables
   ↓
Add GEMINI_API_KEY


## Running the Application
Start the Flask application:
python app.py

### The application will run locally at:
http://127.0.0.1:5000

Open the URL in a web browser.
## Application Workflow
### Enter Case Name
Example:
Rupa Ashok Hurra vs Ashok Hurra Anr

### Enter Question
Example:
What was the main issue considered by the Supreme Court in this case?

### Ask the Question
Click:
ASK LEGAL QUESTION

## Author
Debanjan Gayen
Data Analyst | Python | SQL | Power BI | Machine Learning | NLP | RAG