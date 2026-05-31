import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma  # Modern integration fix

print("🚀 Rebuilding Clean Vector Store...")

load_dotenv()
if "OPENAI_API_KEY" not in os.environ:
    print("❌ ERROR: Missing OpenAI API Key inside your .env file!")
    exit()

if not os.path.exists("FAQ.txt"):
    print("❌ ERROR: Cannot find FAQ.txt!")
    exit()

# Load and Split
loader = TextLoader("FAQ.txt", encoding="utf-8")
raw_documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
chunks = text_splitter.split_documents(raw_documents)

# Build Database Folder
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
db_folder = "./chroma_db"

vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=db_folder
)

print(f"✅ Success! Local 'chroma_db' directory successfully created at: {db_folder}")