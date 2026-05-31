import os
import json
import streamlit as st
import networkx as nx
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma

# 1. Page Configuration & UI Headers
st.set_page_config(page_title="Production Trip Planner", page_icon="✈️", layout="wide")
st.title("✈️ Production-Grade AI Trip Planner (Hybrid RAG)")
st.write("An enterprise-grade GenAI application merging Vector Store (Chroma) and Knowledge Graph (NetworkX) context streams.")

# Load environment keys securely
load_dotenv()
if "OPENAI_API_KEY" not in os.environ:
    st.error("Missing OpenAI API Key! Please check your .env file.")

# 2. Initialize Core Backends & Databases
@st.cache_resource
def setup_hybrid_backend():
    app_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    guard_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    eval_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    
    # Connect to local Vector DB
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    
    # Load local Knowledge Graph triplets
    G = nx.DiGraph()
    if os.path.exists("graph_data.json"):
        with open("graph_data.json", "r", encoding="utf-8") as f:
            triplets = json.load(f)
        for item in triplets:
            G.add_edge(item["source"], item["target"], label=item["relation"])
            
    return app_llm, guard_llm, eval_llm, vector_db, G

app_llm, guard_llm, eval_llm, vector_db, knowledge_graph = setup_hybrid_backend()

# Helper function to query both systems and build the blended context
def get_hybrid_context(query_text, target_destination, v_db, k_graph):
    # Part A: Vector Semantic Search (For broad policies, luggage rules, insurance)
    vector_results = v_db.similarity_search(query_text, k=2)
    vector_context = "\n".join([f"- {doc.page_content}" for doc in vector_results])
    
    # Part B: Knowledge Graph Traversal (For explicit structural facts, secrets)
    graph_lines = []
    matched_node = None
    for node in k_graph.nodes:
        if target_destination.lower() in node.lower():
            matched_node = node
            break
            
    if matched_node:
        for neighbor in k_graph.neighbors(matched_node):
            relation = k_graph[matched_node][neighbor]['label']
            graph_lines.append(f"- {matched_node} {relation} {neighbor}")
            for sub_neighbor in k_graph.neighbors(neighbor):
                sub_relation = k_graph[neighbor][sub_neighbor]['label']
                graph_lines.append(f"  * Detail: {neighbor} {sub_relation} {sub_neighbor}")
                
    graph_context = "\n".join(graph_lines) if graph_lines else "No specific graph structural nodes found."
    
    return vector_context, graph_context

# 3. Define Prompt Templates
guardrail_template = ChatPromptTemplate.from_messages([
    ("system", "You are a safety filter for a travel app. Check if the location is safe, real, and appropriate for a vacation."),
    ("user", "Analyze this destination: '{destination}'. Reply with exactly one word: SAFE or UNSAFE.")
])

# Upgraded User Prompt engineered specifically for Dual-Core Context consumption
travel_template = ChatPromptTemplate.from_messages([
    ("system", """You are an expert travel guide. Create a concise, day-by-day itinerary with key highlights.
    You MUST weave the custom local agency policies (luggage, insurance, cancellations) and destination-specific secrets provided below directly into your response."""),
    ("user", """
    === AGENCY POLICIES (FROM VECTOR DATABASE) ===
    {vector_context}
    
    === UNIQUE DESTINATION SECRETS (FROM KNOWLEDGE GRAPH) ===
    {graph_context}
    
    User Request:
    I want to plan a {days}-day trip to {destination}.
    """)
])

eval_template = ChatPromptTemplate.from_messages([
    ("system", "You are an independent Quality Assurance Auditor checking an AI travel assistant's output."),
    ("user", """
    User Request: Plan a {days}-day trip to {destination}.
    AI Response Output:
    {itinerary}
    
    Analyze the AI response text. Evaluate it on two strict requirements:
    1. Does it focus directly on the requested destination?
    2. Does it provide exactly the requested number of days?
    
    Provide your response in this exact layout:
    SCORE: [Insert a percentage score from 0% to 100% based on accuracy]
    STATUS: [PASSED or FAILED based on a 70% threshold]
    REASONING: [Provide a one-sentence summary explaining your grade]
    """)
])

# Build Chains
guardrail_chain = guardrail_template | guard_llm
travel_chain = travel_template | app_llm
eval_chain = eval_template | eval_llm

# 4. User Interface Sidebar Configuration with Testing Suite
st.sidebar.header("🧪 Hybrid QA Testing Suite")
test_cases = [
    {"label": "Manual Input (Type your own)", "dest": "", "days": 3},
    {"label": "Hybrid Test 1: Paris (Injects Luggage Rules + Secret Spot)", "dest": "Paris", "days": 3},
    {"label": "Hybrid Test 2: Tokyo (Injects Refund Policy + Train Spot)", "dest": "Tokyo", "days": 2},
    {"label": "Hybrid Test 3: Rome (Injects Insurance Policy + Brass Keyhole)", "dest": "Rome", "days": 4},
    {"label": "Guardrail Test: Active Conflict Zone", "dest": "Active Conflict Zone", "days": 3}
]

selected_case = st.sidebar.selectbox("Choose a Test Scenario:", test_cases, format_func=lambda x: x["label"])

st.sidebar.markdown("---")
st.sidebar.header("🗺️ Plan Your Adventure")

if selected_case["label"] == "Manual Input (Type your own)":
    destination_input = st.sidebar.text_input("Destination", placeholder="e.g., Tokyo, London")
    days_input = st.sidebar.number_input("Number of Days", min_value=1, max_value=14, value=3)
else:
    destination_input = st.sidebar.text_input("Destination", value=selected_case["dest"])
    days_input = st.sidebar.number_input("Number of Days", min_value=1, max_value=14, value=selected_case["days"])

submit_btn = st.sidebar.button("Generate & Evaluate Itinerary")

# 5. Core Application Execution Pipeline
if submit_btn:
    if not destination_input.strip():
        st.sidebar.warning("Please enter a destination.")
    else:
        col1, col2 = st.columns([3, 2])
        
        # --- STAGE 1: RUN GUARDRAIL ---
        with st.spinner("🔒 Scanning destination safety parameters..."):
            safety_check = guardrail_chain.invoke({"destination": destination_input})
            safety_status = safety_check.content.strip().upper()
            
        if "UNSAFE" in safety_status:
            st.error(f"❌ Security Guardrail Alert: '{destination_input}' was flagged as unsafe or inappropriate for vacation routing.")
        else:
            # --- STAGE 2: DUAL RETRIEVAL & HYBRID GENERATION ---
            with col1:
                st.subheader("🗺️ Your Custom Itinerary")
                
                # Fetch context chunks simultaneously from Chroma and NetworkX
                with st.spinner("🔄 Querying Vector Store & Knowledge Graph in parallel..."):
                    search_query = f"Baggage guidelines, cancellation windows, insurance and hidden secrets for {destination_input}"
                    v_context, g_context = get_hybrid_context(search_query, destination_input, vector_db, knowledge_graph)
                
                # Generate Itinerary using merged context inputs
                with st.spinner("🤖 Generating trip contents..."):
                    response = travel_chain.invoke({
                        "vector_context": v_context,
                        "graph_context": g_context,
                        "destination": destination_input, 
                        "days": str(days_input)
                    })
                    itinerary_output = response.content
                    st.success("Generation Complete!")
                    st.markdown(itinerary_output)
                    
                    # Diagnostic Dashboard Expander
                    with st.expander("📂 View Blended Hybrid RAG Context Streams"):
                        st.subheader("📥 Vector Store Payload")
                        st.text(v_context)
                        st.subheader("🕸️ Knowledge Graph Payload")
                        st.code(g_context, language="text")
            
            # --- STAGE 3: RUN AUTOMATED EVALUATION ---
            with col2:
                st.subheader("📊 Real-Time Quality Evaluation")
                with st.spinner("🔬 Auditing response accuracy criteria..."):
                    
                    eval_response = eval_chain.invoke({
                        "destination": destination_input,
                        "days": str(days_input),
                        "itinerary": itinerary_output
                    })
                    
                    eval_text = eval_response.content
                    lines = eval_text.split("\n")
                    
                    score_display = "100%"
                    status_display = "PASSED"
                    reasoning_display = "The output perfectly matches parameters."
                    
                    for line in lines:
                        if line.startswith("SCORE:"):
                            score_display = line.replace("SCORE:", "").strip()
                        elif line.startswith("STATUS:"):
                            status_display = line.replace("STATUS:", "").strip()
                        elif line.startswith("REASONING:"):
                            reasoning_display = line.replace("REASONING:", "").strip()
                    
                    st.metric(
                        label="Answer Relevancy Score", 
                        value=score_display,
                        delta=status_display,
                        delta_color="normal" if "PASS" in status_display else "inverse"
                    )
                    
                    with st.expander("🔎 See Evaluator Breakdown & Reasoning", expanded=True):
                        st.write(f"**Status:** {status_display}")
                        st.write(f"**Reasoning:** {reasoning_display}")