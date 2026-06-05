import os
from dotenv import load_dotenv
from groq import Groq
from pipeline import search

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def ask(question, k=4):
    # Step 1: Retrieve relevant chunks
    results = search(question, k)
    
    docs = results["documents"][0]
    metas = results["metadatas"][0]

    # Step 2: Build numbered context blocks with clear separators
    context_blocks = []
    for i, (doc, meta) in enumerate(zip(docs, metas)):
        context_blocks.append(
            f"[Document {i+1} | Source: {meta['source']} | Type: {meta['type']}]\n{doc}"
        )
    context = "\n\n---\n\n".join(context_blocks)

    # Step 3: Tight grounding prompt
    system_prompt = """You are a helpful advisor for students researching UT Austin majors.
You have been given exactly 4 documents retrieved from student Reddit posts, blogs, and official UT sources.

You MUST follow these rules:
1. Read ALL 4 documents before writing your answer
2. Synthesize information across all 4 documents — do not just summarize one and ignore the rest
3. Cite sources naturally inline like "according to a student on Reddit" or "one blog notes" or "per official UT documentation" — use the source type and filename context to determine how to refer to it naturally. Never say "Doc 1" or "Document 2"
4. If two documents disagree, naturally note it like "some students feel... while others say..."
5. If a document is only loosely related to the question, still weave in what it contributes
6. NEVER use outside knowledge or general assumptions — only what is written in the documents
7. If the documents do not contain enough information to answer, say exactly: "I don't have enough information on that in my sources." """

    user_prompt = f"""Here are all 4 retrieved documents:

{context}

---

The person asking this question is a prospective or current UT Austin student seeking advice for THEMSELVES.
Answer directly to them using ALL 4 documents above.
Do not refer to "the original poster" or "the OP" — address the user directly as "you".

Question: {question}

End your response with a newline and then:
Sources used: [list the exact filenames]"""

    # Step 4: Call Groq
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )

    answer = response.choices[0].message.content

    # Step 5: Programmatically guarantee source attribution
    unique_sources = list(dict.fromkeys(m["source"] for m in metas))

    return {
        "answer": answer,
        "sources": unique_sources
    }