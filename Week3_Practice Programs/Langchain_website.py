from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader(web_path = "https://www.geeksforgeeks.org/deep-learning/large-language-model-llm-tutorial/")
text = loader.load()
print(text)