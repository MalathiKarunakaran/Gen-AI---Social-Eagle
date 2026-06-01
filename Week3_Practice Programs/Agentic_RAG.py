import os
import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI
import requests
from sentence_transformers import SentenceTransformer
import faiss
from dotenv import load_dotenv

load_dotenv()

# === API Keys ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

client = OpenAI()

# === Load PDF & create index ===
@st.cache_resource
def load_pdfs_and_create_index(pdf_paths):

    chunks = []
    model = SentenceTransformer("all-MiniLM-L6-v2")

    for pdf in pdf_paths:
        reader = PdfReader(pdf)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

        chunk_size = 500

        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i + chunk_size])

    vectors = model.encode(chunks)

    dimension = vectors.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)

    return chunks, index, model


# === Retrieve ===
def retrieve(query, chunks, index, model, top_k=3):

    q_emb = model.encode([query])

    D, I = index.search(q_emb, top_k)

    return [chunks[i] for i in I[0]]


# === Verifier ===
def is_answer_sufficient(query, answer):

    prompt = f"""
Question: {query}
Retrieved Answer: {answer}

Is the answer sufficient, accurate, and complete?
Reply with YES or NO and a short reason.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# === Fallback: SerpAPI via requests ===
def serp_search(query):

    url = "https://serpapi.com/search.json"

    params = {
        "q": query,
        "api_key": SERPAPI_KEY
    }

    resp = requests.get(url, params=params)

    results = resp.json()

    organic = results.get("organic_results", [])

    snippets = []

    for r in organic:

        snippet = r.get("snippet") or r.get("title")

        if snippet:
            snippets.append(snippet)

    if snippets:

        return "\n".join(snippets)

    else:

        # If search failed, ask LLM to answer from scratch

        fallback_prompt = f"""
The web search for the question "{query}" returned no relevant results.

Please generate a helpful answer to this question using your general knowledge.
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": fallback_prompt
                }
            ]
        )

        return response.choices[0].message.content


# === Orchestrator ===
def answer_query(query, chunks, index, model):

    retrieved = retrieve(query, chunks, index, model)

    combined = "\n".join(retrieved)

    verdict = is_answer_sufficient(query, combined)

    if "YES" in verdict.upper():

        return (
            f"📄 **From PDF:**\n\n"
            f"{combined}\n\n"
            f"✅ **Verifier:** {verdict}"
        )

    else:

        serp_result = serp_search(query)

        return (
            f"🌐 **From Web:**\n\n"
            f"{serp_result}\n\n"
            f"❌ **Verifier:** {verdict}"
        )


# === Streamlit UI ===
st.title("⚡ Agentic RAG (No Framework)")

uploaded_files = st.file_uploader(
    "Upload your PDF(s)",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:

    chunks, index, model = load_pdfs_and_create_index(uploaded_files)

    st.success(
        f"Loaded {len(uploaded_files)} PDF(s) and indexed {len(chunks)} chunks."
    )

    query = st.text_input("Ask a question")

    if query:

        with st.spinner("Thinking..."):

            result = answer_query(
                query,
                chunks,
                index,
                model
            )

        st.markdown(result)