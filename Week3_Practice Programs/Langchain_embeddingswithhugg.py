from langchain_huggingface import HuggingFaceEmbeddings

hf_embed = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

textembed = "This is the one of most wonderful AI Course"

embeded = hf_embed.embed_query(textembed)

print(embeded[:5])