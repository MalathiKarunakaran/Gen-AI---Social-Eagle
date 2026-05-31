import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

# Modern integration package fix for Python 3.13 / Windows
from langchain_chroma import Chroma

print("🔄 Starting Fail-Safe Vector Store Compilation...")

# 1. Load your OpenAI API Key securely
load_dotenv()
if "OPENAI_API_KEY" not in os.environ:
    print("❌ ERROR: Missing OPENAI_API_KEY inside your .env file!")
    print("Please add OPENAI_API_KEY=sk-... to your .env file in this directory.")
    exit()
else:
    print("✅ OpenAI API Key read successfully.")

# 2. Check for the text source data
if not os.path.exists("FAQ.txt"):
    print("❌ ERROR: Cannot find 'FAQ.txt' in this directory.")
    print(f"Current working directory: {os.getcwd()}")
    exit()

try:
    # 3. Document Extraction & Chunks Conversion
    print("📄 Extracting text layers from FAQ.txt...")
    loader = TextLoader("FAQ.txt", encoding="utf-8")
    raw_documents = loader.load()

    print("✂️ Chopping text blocks into searchable fragments...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
    chunks = text_splitter.split_documents(raw_documents)
    print(f"📦 Total data chunks ready: {len(chunks)}")

    # 4. Initialize the Vector Mapping Architecture
    print("🧠 Contacting OpenAI to initialize Embedding Model...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # 5. Build and Force Write the Directory Database to Disk
    db_folder = "./chroma_db"
    print(f"💾 Compiling and saving database directly to: {db_folder}...")
    
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=db_folder
    )
    
    print("✅ Local database successfully compiled!")

    # 6. Verify directory creation status
    if os.path.exists(db_folder):
        print(f"📁 Verification Check: The folder '{db_folder}' now physically exists on your drive.")
    else:
        print("⚠️ Warning: The engine reported success, but the physical folder structure is hidden.")

    # 7. Run Verification Retrieval Query
    test_query = "What is the policy for cancellation?"
    print(f"\n🔍 Executing Test Query: '{test_query}'")
    matching_docs = vector_store.similarity_search(test_query, k=1)
    
    print("\n--- [Retrieved Database Context] ---")
    if matching_docs:
        print(matching_docs[0].page_content)
    else:
        print("❌ Search returned empty results.")
    print("------------------------------------\n")

except Exception as e:
    print(f"❌ CRITICAL COMPILATION FAULT: {e}")

print("🏁 Execution Loop Ended.")