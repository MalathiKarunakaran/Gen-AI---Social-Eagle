from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# -----------------------------------------------
# Step 1: Create Embedding Model
# -----------------------------------------------
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# -----------------------------------------------
# Step 2: Sample texts to store in FAISS
# -----------------------------------------------
texts = [
    "This is a wonderful AI Course",
    "LangChain is a framework for LLM applications",
    "FAISS is a library for efficient similarity search",
    "HuggingFace provides free embedding models",
    "Retrievers fetch relevant documents from vector stores",
    "RAG stands for Retrieval Augmented Generation",
    "Deep learning is a subset of machine learning",
    "Python is the most popular language for AI development"
]

# -----------------------------------------------
# Step 3: Create FAISS Vector Store
# -----------------------------------------------
vectorstore = FAISS.from_texts(texts, embeddings)

# -----------------------------------------------
# Step 4: Basic Similarity Search (without retriever)
# -----------------------------------------------
query = "Tell me about AI"
results = vectorstore.similarity_search(query, k=2)

print("=" * 50)
print("1. Basic Similarity Search")
print("=" * 50)
for i, doc in enumerate(results):
    print(f"{i+1}. {doc.page_content}")

# -----------------------------------------------
# Step 5: Retriever - Basic (as_retriever)
# -----------------------------------------------
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
retrieved_docs = retriever.invoke("What is LangChain?")

print("\n" + "=" * 50)
print("2. Basic Retriever (k=3)")
print("=" * 50)
for i, doc in enumerate(retrieved_docs):
    print(f"{i+1}. {doc.page_content}")

# -----------------------------------------------
# Step 6: MMR Retriever (Maximum Marginal Relevance)
#         - Avoids duplicate/similar results
# -----------------------------------------------
mmr_retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 3, "fetch_k": 6}
)
mmr_docs = mmr_retriever.invoke("machine learning and AI")

print("\n" + "=" * 50)
print("3. MMR Retriever (Diverse Results)")
print("=" * 50)
for i, doc in enumerate(mmr_docs):
    print(f"{i+1}. {doc.page_content}")

# -----------------------------------------------
# Step 7: Similarity Score Threshold Retriever
#         - Only returns results above a score
# -----------------------------------------------
score_retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.3, "k": 3}
)
score_docs = score_retriever.invoke("vector database search")

print("\n" + "=" * 50)
print("4. Score Threshold Retriever (score >= 0.3)")
print("=" * 50)
for i, doc in enumerate(score_docs):
    print(f"{i+1}. {doc.page_content}")