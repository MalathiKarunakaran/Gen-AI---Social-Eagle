import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

print("🧠 Rebuilding Clean Graph Data...")

load_dotenv()
if "OPENAI_API_KEY" not in os.environ:
    print("❌ ERROR: Missing OPENAI_API_KEY inside your .env file!")
    exit()

if not os.path.exists("FAQ.txt"):
    print("❌ ERROR: Cannot find FAQ.txt!")
    exit()

with open("FAQ.txt", "r", encoding="utf-8") as f:
    knowledge_text = f.read()

# Setup Extraction
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
output_parser = JsonOutputParser()

extraction_template = ChatPromptTemplate.from_messages([
    ("system", """You are a Knowledge Graph extraction engineer. Extract entities and relationships from the text provided.
    Format your entire output strictly as a valid JSON array of objects with 'source', 'relation', and 'target' keys.
    Do not output any introductory text or markdown ticks."""),
    ("user", "Extract data from this text:\n\n{text}")
])

extraction_chain = extraction_template | llm | output_parser

try:
    extracted_triplets = extraction_chain.invoke({"text": knowledge_text})
    with open("graph_data.json", "w", encoding="utf-8") as out_f:
        json.dump(extracted_triplets, out_f, indent=2)
    print("✅ Success! 'graph_data.json' successfully created.")
except Exception as e:
    print(f"❌ Extraction Error: {e}")