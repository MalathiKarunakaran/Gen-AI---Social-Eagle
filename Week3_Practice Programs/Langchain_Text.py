from langchain_community.document_loaders import TextLoader

text = TextLoader ("nodes.txt")
print(text)
