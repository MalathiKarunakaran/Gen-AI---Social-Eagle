from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("7.pdf")
text = loader.load()
print(text)