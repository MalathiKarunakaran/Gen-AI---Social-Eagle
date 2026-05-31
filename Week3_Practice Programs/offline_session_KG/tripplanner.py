import os
import json
import streamlit as st
import networkx as nx
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 1. Page Configuration & UI Headers
st.set_page_config(page_title="Production Trip Planner", page_icon="✈️", layout="wide")
st.title("✈️ Production-Grade AI Trip Planner (GraphRAG)")
st.write("An interactive GenAI application featuring input guardrails, live Knowledge Graph contextual lookups, and automated evaluations.")

# Load environment keys securely
load_dotenv()
if "OPENAI_API_KEY" not in os.environ:
    st.error("Missing OpenAI API Key! Please check your .env file.")

# 2. Initialize Engines & Graph Storage
@st.cache_resource
def setup_ai_backend():
    app_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    guard_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    eval_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    
    # Load the structured relations we built in Step 2 & 3 into an active network
    G = nx.DiGraph()
    if os.path.exists("graph_data.json"):
        with open("graph_data.json", "r", encoding="utf-8") as f:
            triplets = json.load(f)
        for item in triplets:
            G.add_edge(item["source"], item["target"], label=item["relation"])
            
    return app_llm, guard_llm, eval_llm, G

app_llm, guard_llm, eval_llm, knowledge_graph = setup_ai_backend()

# Helper function to traverse the graph for relevant connections
def get_graph_context(query_node, graph):
    context_lines = []
    # Clean string input to check against nodes match
    matched_node = None
    for node in graph.nodes:
        if query_node.lower() in node.lower():
            matched_node = node
            break
            
    if matched_node:
        # Find all paths leaving our destination node
        for neighbor in graph.neighbors(matched_node):
            relation = graph[matched_node][neighbor]['label']
            context_lines.append(f"- {matched_node} {relation} {neighbor}")
            
            # Sub-query lookup: Get secondary connections (e.g., Montmartre details)
            for sub_neighbor in graph.neighbors(neighbor):
                sub_relation = graph[neighbor][sub_neighbor]['label']
                context_lines.append(f"  * Note: {neighbor} {sub_relation} {sub_neighbor}")
    
    if context_lines:
        return "\n".join(context_lines)
    return "No matching specific agency secret spots found in the Knowledge Graph repository."

# 3. Define Prompt Templates
guardrail_template = ChatPromptTemplate.from_messages([
    ("system", "You are a safety filter for a travel app. Check if the location is safe, real, and appropriate for a vacation."),
    ("user", "Analyze this destination: '{destination}'. Reply with exactly one word: SAFE or UNSAFE.")
])

# Travel Template modified for explicit Graph Structure Context
travel_template = ChatPromptTemplate.from_messages([
    ("system", """You are an expert travel guide. Create a concise, day-by-day itinerary with key highlights.
    You MUST study the Knowledge Graph context block provided below and explicitly weave those linked entities and secrets into the itinerary structure."""),
    ("user", """
    Knowledge Graph Context Network Maps:
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
st.sidebar.header("🧪 QA Testing Suite")
test_cases = [
    {"label": "Manual Input (Type your own)", "dest": "", "days": 3},
    {"label": "GraphRAG Test 1: Paris Network Traversal", "dest": "Paris", "days": 3},
    {"label": "GraphRAG Test 2: Tokyo Network Traversal", "dest": "Tokyo", "days": 2},
    {"label": "GraphRAG Test 3: Rome Network Traversal", "dest": "Rome", "days": 4},
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
            # --- STAGE 2: GRAPHRAG RETRIEVAL & GENERATION ---
            with col1:
                st.subheader("🗺️ Your Custom Itinerary")
                
                # Fetch related data paths using graph traversal maps
                with st.spinner("🕸️ Traversing Knowledge Graph entities..."):
                    graph_context = get_graph_context(destination_input, knowledge_graph)
                
                # Generate Itinerary combining inputs + Graph relationships
                with st.spinner("🤖 Generating trip contents..."):
                    response = travel_chain.invoke({
                        "graph_context": graph_context,
                        "destination": destination_input, 
                        "days": str(days_input)
                    })
                    itinerary_output = response.content
                    st.success("Generation Complete!")
                    st.markdown(itinerary_output)
                    
                    # Graph Traversal Diagnostic Log Visualizer
                    with st.expander("📂 View Extracted Knowledge Graph Fact Links"):
                        st.code(graph_context, language="text")
            
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