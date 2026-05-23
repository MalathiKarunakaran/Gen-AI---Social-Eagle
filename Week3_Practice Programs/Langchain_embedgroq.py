import os
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

# -----------------------------------------------
# Set your Groq API key
# Get a FREE key from: https://console.groq.com/
# -----------------------------------------------
os.environ["GROQ_API_KEY"] = "your-groq-api-key-here"  # Replace with your real key

# Step 1: Groq LLM (fast inference using Llama model)
groq_llm = ChatGroq(model="llama3-8b-8192")

textembed = "This is the one of most wonderful AI Course"

# Step 2: Generate a response using Groq LLM
response = groq_llm.invoke(textembed)
print("Groq LLM Response:")
print(response.content)
print()

# Step 3: Embed the text using HuggingFace (Groq does not support embeddings)
hf_embed = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
embeded = hf_embed.embed_query(textembed)

print("Embedding Vector (first 5 values):")
print(embeded[:5])
print(f"Embedding Dimension: {len(embeded)}")
