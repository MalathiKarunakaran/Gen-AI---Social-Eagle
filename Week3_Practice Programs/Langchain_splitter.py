from langchain_community.document_loaders import PyPDFLoader
splittext = PyPDFLoader("7.pdf")
texttex = splittext.load()

fulltext = "/n".join([doc.page_content for doc in texttex])

