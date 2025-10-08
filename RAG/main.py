import os
import ollama
import chromadb
from uuid import uuid4

input = input("Enter your question: ")

#print("Reading the files", end="")
for file in os.listdir("documents"):
    with open("documents/" + file, "r") as file:
        content = file.read()
        sentences = content.split('. ')
        # Clean up sentences and remove empty ones
    documents = [sentence.strip() for sentence in sentences if sentence.strip()]
#print(" Done!")
#print(documents)

#####################################
#   Step 1: Generate embeddings     #
#####################################
client = chromadb.Client()
collection = client.create_collection(name="docs")

#print("Generating embeddings", end="")
for i, d in enumerate(documents):
    response = ollama.embed(model="nomic-embed-text", input=d)
    embeddings = response["embeddings"]
    collection.add(
        ids=[str(i)],
        embeddings=embeddings,
        documents=[d]
    )
#print(" Done!")

#######################
#   Step 2: Retrieve  #
#######################

# generate an embedding for the input and retrieve the most relevant doc
#print("Generating embedding for the input", end="")
response = ollama.embed(
    model="nomic-embed-text",
    input=input
)
#print(" Done!")
#print("Retrieving the most relevant docs", end="")
results = collection.query(
    query_embeddings=response["embeddings"],
    n_results=len(documents)
)
#print(" Done!")
data = results['documents'][0][0]

# generate a response combining the prompt and data we retrieved in step 2
#print("Generating response")
output = ollama.generate(
    model="gemma3:4b",
    prompt=f"Using this data: {data}. Respond to this prompt: {input}"
)

print(output['response'])
