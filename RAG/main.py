import os
import ollama
import chromadb
from uuid import uuid4

input = input("Enter your question: ")

client = chromadb.EphemeralClient()
collection = client.create_collection(name="docs")

def create_collection (file):
    with open("documents/" + file, "r") as file:
        content = file.read()
        sentences = content.split('. ')
        # Clean up sentences and remove empty ones
    return [sentence.strip() for sentence in sentences if sentence.strip()]


#####################################
#   Step 1: Generate embeddings     #
#####################################


for i, d in enumerate(create_collection("industrial_society_and_its_future.txt")):
    response = ollama.embed(model="mxbai-embed-large", input=d)
    embeddings = response["embeddings"]
    collection.add(
        ids=[str(i)],
        embeddings=embeddings,
        documents=[d]
    )


#######################
#   Step 2: Retrieve  #
#######################

# generate an embedding for the input and retrieve the most relevant doc
response = ollama.embed(
    model="mxbai-embed-large",
    input=input
)

results = collection.query(
    query_embeddings=response["embeddings"],
    n_results=1000
)

print(results)

# Step 1: Extract the INNER lists using the [0] index
ids = results['ids'][0]
documents = results['documents'][0]

# Now zip will work correctly, creating pairs of (id, document)
combined_results = list(zip(ids, documents))
# And the sort will work because item[0] is now a string like '1417'
sorted_combined_results = sorted(combined_results, key=lambda item: int(item[0]))
# Step 4: Create a NEW list containing only the documents, in the new sorted order
sorted_documents = [doc for id, doc in sorted_combined_results]

output = ollama.generate(
   model="gpt-oss:20b",
   prompt=f"""Answer the query strictly referring the provided context:
     {sorted_documents}
     Query:
     {input}
     In case you don't have any answer from the context provided, just say:
     I'm sorry I don't have the information you are looking for."""
)

print(output["response"])