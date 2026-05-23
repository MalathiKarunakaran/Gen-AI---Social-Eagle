import sys
sys.stdout.reconfigure(encoding='utf-8')
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
splittext = PyPDFLoader(r"d:\GenAI_Social_Eagle\GENAI_All_Weeks\Week3_Practice Programs\7.pdf")
texttex = splittext.load()

fulltext = "\n".join([doc.page_content for doc in texttex])



text_splitter = CharacterTextSplitter.from_tiktoken_encoder(encoding_name = "cl100k_base", chunk_size =100, chunk_overlap = 0)
texts = text_splitter.split_text(fulltext)
print(texts)