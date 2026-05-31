import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
# New import for automated JSON parsing
from langchain_core.output_parsers import JsonOutputParser

print("🔄 Starting Robust GraphRAG Extraction Script...")

# 1. Load API Key
load_dotenv()
if "OPENAI_API_KEY" not in os.environ:
    print("❌ ERROR: Missing OPENAI_API_KEY inside your .env file!")
    exit()
else:
    print("✅ OpenAI API Key loaded.")

# 2. Read Source Knowledge File
if not os.path.exists("FAQ.txt"):
    print("❌ ERROR: Cannot find 'FAQ.txt'")
    exit()

with open("FAQ.txt", "r", encoding="utf-8") as f:
    knowledge_text = f.read()

# 3. Setup Extraction Model (Temperature 0.0 for strict rules)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

# 4. Initialize LangChain's JsonOutputParser
output_parser = JsonOutputParser()

# 5. Create the Extraction Blueprint Prompt
extraction_template = ChatPromptTemplate.from_messages([
    ("system", """You are a Knowledge Graph extraction engineer. Your job is to extract entities and their explicit relationships from the text provided.
    
    You must format your entire output as a valid JSON array of objects. Each object must have exactly three keys: 'source', 'relation', and 'target'.
    
    Example Structure:
    [
      {{"source": "Paris", "relation": "HAS_HIDDEN_GEM", "target": "Musée de la Vie Romantique"}}
    ]
    
    Ensure entity names are concise nouns. Ensure relationship strings are short and uppercase.
    Do not output any introductory or concluding text—only the JSON array."""),
    ("user", "Extract all entities and relationships from this text:\n\n{text}")
])

# 6. Build the Chain (Prompt -> LLM -> JSON Parser)
extraction_chain = extraction_template | llm | output_parser

# 7. Run the Extraction Request
print("🤖 Sending text data to OpenAI for entity processing...")
try:
    extracted_triplets = extraction_chain.invoke({"text": knowledge_text})
    
    print(f"\n✅ Graph Extraction Complete! Captured {len(extracted_triplets)} unique relationships:\n")
    
    # This will print the beautiful formatting directly to your terminal
    print(json.dumps(extracted_triplets, indent=2))
    
    # Save this structured data temporarily to disk for our next step
    with open("graph_data.json", "w", encoding="utf-8") as out_f:
        json.dump(extracted_triplets, out_f, indent=2)
    print("\n💾 Progress saved locally to 'graph_data.json'.")

except Exception as e:
    print(f"❌ Extraction Parsing Error: {e}")

print("\n🏁 Script Finished Execution.")