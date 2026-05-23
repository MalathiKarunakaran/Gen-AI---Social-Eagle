from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Create embedding model
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Sample texts to store in Chroma vector store
texts = [
    "This is a wonderful AI Course",
    "LangChain is a framework for LLM applications",
    "Chroma is a vector database for AI applications",
    "HuggingFace provides free embedding models"
]

# Create Chroma vector store from texts
vectorstore = Chroma.from_texts(texts, embeddings)

# Search for similar text
query = "Tell me about AI"
results = vectorstore.similarity_search(query, k=2)

print("Top 2 similar results:")
for i, doc in enumerate(results):
    print(f"{i+1}. {doc.page_content}")