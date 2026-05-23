from langchain_community.document_loaders import ArxivLoader

loader = ArxivLoader(query = "7606.03762")
text = loader.load()
print(text)