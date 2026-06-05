from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

def clean(text):
    cutoff = text.find("New to Reddit?")
    if cutoff != -1:                 
        text = text[:cutoff] + text[cutoff+1:]       
    junk_phrases = [
        "Skip to main content",
        "Skip to Navigation",
        "Skip to Right Sidebar",
    ]
    for phrase in junk_phrases:
        text = text.replace(phrase, "")
    text = text.strip()
    return text                      # hand the cleaned string back out


#finding  every file from documents folder
files = list(Path("documents").glob("*.txt")) #list is creating a list of all files that have a path in document folder ending with .txt

#tell me how many files
print ("Number of files found is: ", len(files))
docs = [] 

for file in files:
    docs.append ({"source": file.name, 
    "type": file.stem.rsplit("_",1)[1], 
    "text": (clean(file.read_text(encoding="utf-8")))})

#print(len(docs))
#for doc in docs:
    #print(doc["source"])
    #print(doc["type"])
    #print(doc["text"][:900])

#chunking - recursive strategy

#create our splitter
text_splitter = RecursiveCharacterTextSplitter(
    #create our chunk size
    chunk_size = 2800, #maximum size of each chunk is 2800 characters
    #number of overlapping characters between chunks
    chunk_overlap = 400,
    #function to calculate length
    length_function = len,
)

#empty list for chunks
chunks = []
for doc in docs:
    pieces = text_splitter.split_text(doc["text"])
    for piece in pieces:
        chunks.append({
            "source": doc["source"],
            "type": doc["type"],
            "text": piece,
        })
#print("Total chunks:", len(chunks))
#print(chunks[0])
#print(chunks[1])
#print(chunks[2])
#print(chunks[3])
#print(chunks[4])

sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="Documents", embedding_function=sentence_transformer_ef)

chunk_text = []
metadata = []
ids = []
x = 0

for chunk in chunks:
    metadata.append({"source": chunk["source"], "type": chunk["type"], "position": x})    
    chunk_text.append(chunk["text"])
    ids.append("chunk_" + str(x))
    x = x + 1

#collection.add(
#    documents = chunk_text,
#    metadatas = metadata,
#    ids = ids,
#)

print("Loaded:", collection.count())

def search(query, k):
    results = collection.query(
        query_texts = [query],
        n_results = k)
    return results

