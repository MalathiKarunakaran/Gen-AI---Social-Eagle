import os
import json
import networkx as nx
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

print("🚀 Starting Hybrid RAG Step 2: Unified Routing Test...")

# 1. Load Environmental Keys & Secure Databases
load_dotenv()
if "OPENAI_API_KEY" not in os.environ:
    print("❌ ERROR: Missing OPENAI_API_KEY inside your .env file!")
    exit()

# 2. Ingest the Local Vector Database (Chroma)
db_folder = "./chroma_db"
if not os.path.exists(db_folder):
    print(f"❌ ERROR: Cannot find Vector Store at '{db_folder}'. Please rebuild your vector files.")
    exit()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_db = Chroma(persist_directory=db_folder, embedding_function=embeddings)
print("✅ Vector Store connected successfully.")

# 3. Ingest the Local Knowledge Graph (NetworkX)
if not os.path.exists("graph_data.json"):
    print("❌ ERROR: Cannot find 'graph_data.json'. Please rebuild your graph data file.")
    exit()

G = nx.DiGraph()
with open("graph_data.json", "r", encoding="utf-8") as f:
    triplets = json.load(f)
for item in triplets:
    G.add_edge(item["source"], item["target"], label=item["relation"])
print("✅ Knowledge Graph loaded successfully.")


# 4. The Unified Hybrid Retrieval Engine Function
def hybrid_retrieve(query_text, target_destination, v_db, k_graph, k_slots=2):
    print(f"\n🔍 Executing Hybrid Retrieval for: '{query_text}' across '{target_destination}'")
    
    # --- Part A: Vector Database Similarity Search ---
    vector_results = v_db.similarity_search(query_text, k=k_slots)
    vector_context = "\n".join([f"[Vector Match]: {doc.page_content}" for doc in vector_results])
    
    # --- Part B: Knowledge Graph Traversal Lookup ---
    graph_context_lines = []
    matched_node = None
    for node in k_graph.nodes:
        if target_destination.lower() in node.lower():
            matched_node = node
            break
            
    if matched_node:
        for neighbor in k_graph.neighbors(matched_node):
            relation = k_graph[matched_node][neighbor]['label']
            graph_context_lines.append(f"[Graph Map]: {matched_node} {relation} {neighbor}")
            # Pull secondary details if they exist
            for sub_neighbor in k_graph.neighbors(neighbor):
                sub_relation = k_graph[neighbor][sub_neighbor]['label']
                graph_context_lines.append(f"  * Detail: {neighbor} {sub_relation} {sub_neighbor}")
                
    graph_context = "\n".join(graph_context_lines) if graph_context_lines else "[Graph Map]: No specific network matches found."
    
    # --- Part C: Merge and Consolidate context blocks ---
    combined_context = f"=== VECTOR RETRIEVED POLICIES ===\n{vector_context}\n\n=== GRAPH RETRIEVED CONNECTIONS ===\n{graph_context}"
    return combined_context


# 5. Run a Live Test of the Hybrid Retriever
test_destination = "Paris"
test_query = "What hidden secrets exist for Paris and what are the checked bag policies?"

final_context = hybrid_retrieve(test_query, test_destination, vector_db, G)

print("\n==================================================")
print("         HYBRID RETRIEVER CONTEXT OUTPUT          ")
print("==================================================")
print(final_context)
print("==================================================")

print("\n🏁 Step 2 Execution Finished Successfully.")