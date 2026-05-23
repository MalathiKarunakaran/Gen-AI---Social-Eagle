import os
from langchain_openai import OpenAIEmbeddings

os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"  # Replace with your real key

openai_embed = OpenAIEmbeddings(model="text-embedding-3-small")

textembed = "This is the one of most wonderful AI Course"

embeded = openai_embed.embed_query(textembed)

print(embeded[:5])