import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

print("🔄 Starting RAG Step 2 Script...")

# 1. Verification Check: Does the file exist?
if not os.path.exists("FAQ.txt"):
    print("❌ ERROR: Cannot find 'FAQ.txt' in this folder!")
    print(f"Current working directory is: {os.getcwd()}")
else:
    print("✅ Found FAQ.txt successfully.")
    
    try:
        # 2. Load the document safely with UTF-8 encoding
        print("📄 Loading FAQ.txt content...")
        loader = TextLoader("FAQ.txt", encoding="utf-8")
        raw_documents = loader.load()
        print(f"✅ Loaded raw file. Characters in document: {len(raw_documents[0].page_content)}")

        # 3. Define the text splitter parameters
        # chunk_size=400 splits the text roughly by paragraphs/FAQs
        # chunk_overlap=50 ensures no sentences are lost at the cut boundaries
        print("✂️ Initializing Text Splitter...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=50
        )

        # 4. Perform the splitting process
        chunks = text_splitter.split_documents(raw_documents)
        print(f"✅ Text splitting complete. Total chunks created: {len(chunks)}\n")

        # 5. Print out every single chunk to the terminal window
        print("==============================")
        print("      PRINTING CHUNK DATA     ")
        print("==============================")
        for i, chunk in enumerate(chunks, 1):
            print(f"\n--- Chunk #{i} ---")
            print(chunk.page_content.strip())
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

print("\n🏁 Script Finished Execution.")