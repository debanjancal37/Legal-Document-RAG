# LEGAL DOCUMENT RAG APPLICATION
# Flask Backend

from flask import Flask, render_template, request, jsonify

import os
import time
import numpy as np
import pandas as pd
import faiss

from sentence_transformers import SentenceTransformer
from google import genai
from google.genai.errors import ServerError


# FLASK APP

app = Flask(__name__)


# PATH CONFIGURATION

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

FAISS_PATH = os.path.join(
    MODEL_DIR,
    "legal_judgment_faiss.index"
)

CHUNKS_PATH = os.path.join(
    MODEL_DIR,
    "legal_judgment_chunks.pkl"
)


# LOAD FAISS INDEX

print("\nLoading FAISS index...")

if not os.path.exists(FAISS_PATH):
    raise FileNotFoundError(
        f"FAISS file not found: {FAISS_PATH}"
    )

index = faiss.read_index(
    FAISS_PATH
)

print(
    f"FAISS loaded successfully. "
    f"Vectors: {index.ntotal}"
)


# LOAD CHUNK METADATA

print("\nLoading chunk metadata...")

if not os.path.exists(CHUNKS_PATH):
    raise FileNotFoundError(
        f"Chunk file not found: {CHUNKS_PATH}"
    )

chunks_df = pd.read_pickle(
    CHUNKS_PATH
)

print(
    f"Chunk metadata loaded. "
    f"Total chunks: {len(chunks_df)}"
)


# LOAD EMBEDDING MODEL


print("\nLoading embedding model...")

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

print("Embedding model loaded successfully.")


# GEMINI API CONFIGURATION


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if GEMINI_API_KEY:

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    print("Gemini client initialized.")

else:

    client = None

    print(
        "WARNING: GEMINI_API_KEY not found."
    )


# CASE-SPECIFIC RETRIEVAL


def retrieve_case_specific_documents(
    case_name,
    question,
    top_k=5
):

    # Extract a searchable keyword

    words = case_name.strip().split()

    if not words:
        return []

    # Use first meaningful case-name word
    case_keyword = words[0]

    # Find chunks belonging to the case

    case_matches = chunks_df[
        chunks_df["case_info"]
        .astype(str)
        .str.contains(
            case_keyword,
            case=False,
            na=False
        )
    ].copy()

    print(
        f"Case-related chunks found: "
        f"{len(case_matches)}"
    )

    if len(case_matches) == 0:
        return []

    # Create question embedding

    query_embedding = embedding_model.encode(
        [question],
        normalize_embeddings=True
    )

    # Create embeddings for case chunks

    case_embeddings = embedding_model.encode(
        case_matches["text"].tolist(),
        normalize_embeddings=True,
        show_progress_bar=False
    )

    # Calculate cosine similarity

    scores = np.dot(
        case_embeddings,
        query_embedding[0]
    )

    case_matches[
        "similarity_score"
    ] = scores

    # Sort by relevance

    case_matches = case_matches.sort_values(
        "similarity_score",
        ascending=False
    )


    # Return Top-K

    return case_matches.head(
        top_k
    ).to_dict(
        orient="records"
    )


# BUILD RETRIEVED CONTEXT


def build_context(sources):

    context_parts = []

    for i, source in enumerate(sources):

        context_parts.append(
            f"""
SOURCE {i + 1}

Case Information:
{source["case_info"]}

Relevant Judgment:
{source["text"]}
"""
        )

    return "\n".join(
        context_parts
    )


# GENERATE RAG ANSWER


def generate_answer(
    case_name,
    question,
    top_k=5
):

    # Retrieve relevant chunks

    sources = retrieve_case_specific_documents(
        case_name,
        question,
        top_k=top_k
    )

    if len(sources) == 0:

        return {
            "answer":
                "The requested case could not be "
                "found in the dataset.",
            "sources": [],
            "model": None
        }

    # Build context

    context = build_context(
        sources
    )

    # Check Gemini API

    if client is None:

        return {
            "answer":
                "Gemini API key is not configured.",
            "sources": sources,
            "model": None
        }

    # RAG Prompt

    prompt = f"""
You are a legal document retrieval assistant.

Answer the user's question ONLY using the
retrieved judgment excerpts provided below.

Do not use outside knowledge.

Do not invent legal facts.

If the retrieved context does not contain
enough information, say:

"Insufficient information in the retrieved documents."

Case:
{case_name}

Question:
{question}

Retrieved Judgment Context:
{context}

Provide a concise, factual and easy-to-understand answer.

Answer:
"""

    # Gemini fallback models

    models = [
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-2.5-flash-lite"
    ]

    for model_name in models:

        try:

            print(
                f"Trying model: {model_name}"
            )

            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            print(
                f"Successfully generated using: "
                f"{model_name}"
            )

            return {
                "answer": response.text,
                "sources": sources,
                "model": model_name
            }

        except ServerError:

            print(
                f"{model_name} unavailable. "
                f"Trying next model..."
            )

            time.sleep(2)

        except Exception as e:

            print(
                f"Error with {model_name}: {e}"
            )

            continue

    return {
        "answer":
            "Gemini is currently unavailable. "
            "Please try again later.",
        "sources": sources,
        "model": None
    }


# HOME PAGE

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# RAG API


@app.route(
    "/ask",
    methods=["POST"]
)
def ask():

    try:

        data = request.get_json()

        case_name = data.get(
            "case_name",
            ""
        ).strip()

        question = data.get(
            "question",
            ""
        ).strip()


        # Validate case name

        if not case_name:

            return jsonify({
                "error":
                    "Please enter a case name."
            }), 400

        # Validate question

        if not question:

            return jsonify({
                "error":
                    "Please enter your question."
            }), 400

        # Generate answer

        result = generate_answer(
            case_name,
            question,
            top_k=5
        )

        # Format sources

        formatted_sources = []

        for source in result["sources"]:

            formatted_sources.append({

                "case_info":
                    source["case_info"],

                "similarity":
                    round(
                        source[
                            "similarity_score"
                        ],
                        4
                    ),

                "text":
                    source["text"][:1000]
            })

        # Return JSON

        return jsonify({

            "answer":
                result["answer"],

            "model":
                result["model"],

            "sources":
                formatted_sources

        })

    except Exception as e:

        print(
            f"Application error: {e}"
        )

        return jsonify({
            "error": str(e)
        }), 500


# RUN APPLICATION

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )