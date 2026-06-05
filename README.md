# The Unofficial Guide — Project 1

> **Repository note:** This repository is forked from the CodePath Applied AI Engineering Fellowship course template for Project 1: building a production RAG system from scratch.
>The template ONLY provided the planning.md scaffolding and document structure used for spec planning.
> All pipeline code (document ingestion, preprocessing, chunking, embedding, vector store construction, retrieval, and grounded generation) was written independently by me as part of this project.

---

## Domain

This system covers the unofficial student knowledge surrounding UT Austin's four overlapping tech-adjacent majors: Computer Science (CS), Management Information Systems (MIS), Statistics and Data Science (SDS), and Informatics. Specifically, it surfaces information about admission competitiveness, actual coursework difficulty, career outcomes, and how students and advisors compare these programs against each other.

This knowledge is valuable because it is almost entirely absent from official channels. The official degree catalogs list required courses and career "outcomes" in vague terms but say nothing about realistic admission odds, which program has better recruiter recognition, or whether students feel their degree was worth it. The real picture lives in Reddit threads where students argue about whether MIS is a "backup major" or an underrated path, in admissions blogs that openly critique UT's CS selectivity, and in forum posts from students mid-degree describing what upper-division classes actually feel like. For any Texas high schooler deciding between these four programs, this is the information that actually matters — and there is no single official place to find it.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | texadmissions.com blog — UT CS alternatives | Blog | https://www.texadmissions.com/blog/2025/6/5/ut-austin-computer-science-is-highly-competitive-consider-these-alternatives |
| 2 | r/UTAustin — upper-division MIS classes | Reddit thread | https://www.reddit.com/r/UTAustin/comments/jmwxll/what_are_upperdivision_mis_classes_like/ |
| 3 | r/UTAustin — MIS vs other majors | Reddit thread | https://www.reddit.com/r/UTAustin/comments/1glze40/question_about_mis_vs_other_majors/ |
| 4 | r/UTAustin — general opinions on MIS | Reddit thread | https://www.reddit.com/r/UTAustin/comments/sqknkh/how_is_the_mis_major/ |
| 5 | r/UTAustin — CS vs MIS vs ECE | Reddit thread | https://www.reddit.com/r/UTAustin/comments/vkrjsp/cs_vs_mis_vs_ece/ |
| 6 | r/UTAustin — honest CS program review | Reddit thread | https://www.reddit.com/r/UTAustin/comments/mr4igd/cs_majors_can_you_give_me_an_honest_review_of_uts/ |
| 7 | r/UTAdmissions — lowest stats admitted to UT CS | Reddit thread | https://www.reddit.com/r/UTAdmissions/comments/1c7hynv/lowest_stats_youve_seen_get_into_ut_cs/ |
| 8 | r/UTAdmissions — how competitive is SDS | Reddit thread | https://www.reddit.com/r/UTAdmissions/comments/1qkg5r6/how_comp_is_ut_sds_and_how_hard_to_get_in/ |
| 9 | r/UTAustin — SDS coursework breakdown | Reddit thread | https://www.reddit.com/r/UTAustin/comments/1jmny50/statistics_and_data_science_major_coursework/ |
| 10 | r/UTAustin — Informatics major opinions | Reddit thread | https://www.reddit.com/r/UTAustin/comments/rq94p0/informatics_major_in_university_of_texas_at_austin/ |
| 11 | texadmissions.com blog — UT Informatics explainer | Blog | https://www.texadmissions.com/blog/2021/04/27/ut-austin-announces-new-degree-bachelors-in-informatics-in-the-ischool |
| 12 | catalog.utexas.edu — official MIS degree plan | Official catalog | https://catalog.utexas.edu/undergraduate/business/degrees-and-programs/bachelor-of-business-administration/management-information-systems/ |
| 13 | catalog.utexas.edu — official Informatics degree plan | Official catalog | https://catalog.utexas.edu/undergraduate/information/degrees-and-programs/bachelor-of-science/ |
| 14 | catalog.utexas.edu — official CS degree plan | Official catalog | https://catalog.utexas.edu/undergraduate/natural-sciences/degrees-and-programs/bs-computer-science/ |
| 15 | catalog.utexas.edu — official SDS degree plan | Official catalog | https://catalog.utexas.edu/undergraduate/natural-sciences/degrees-and-programs/bs-statistics-and-data-sciences/ |

---

## Chunking Strategy

**Chunk size:** 700 tokens

**Overlap:** 100 tokens (~14%)

**Why these choices fit your documents:** The corpus contains two very different document shapes: short, multi-voice Reddit threads where each comment is typically 50–200 tokens, and dense official catalog pages where a block of degree requirements can run 400–600 tokens without a natural break. A 700-token chunk is a deliberate compromise between these extremes — large enough to keep a complete student comment or a catalog requirements block intact as a single unit, but small enough to avoid fusing two or three contradictory student opinions into one diluted embedding. Fused opinions would hurt queries like "is MIS respected?", because the embedding would average out the stance rather than preserve it. I used recursive splitting (paragraph → sentence → character), so the splitter always breaks at the largest natural boundary first, which is important for messy forum text where hard line breaks are meaningful. The 100-token overlap (~14%) ensures that any idea that spills across a chunk boundary stays recoverable in at least one of the two adjacent chunks, without over-duplicating content.

**Preprocessing:** Before chunking, I stripped common Reddit boilerplate: navigation headers ("Skip to main content"), promoted ad blocks, the "People also ask" sections, and the trailing lists of unrelated subreddit links (e.g., r/banjo, r/UIUC) that appear at the bottom of every saved thread. Official catalog pages had their HTML tags removed and section headers normalized to plain text.

**Final chunk count:** 312 chunks across all 15 documents.

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`

I chose this model because it runs entirely locally — no API key, no rate limits, no cost per embedding call — which made iterating on chunking strategies fast and cheap. It is small enough to embed the full corpus on a laptop in under a minute and is well-suited to short-to-medium English text. For a student-opinion corpus where most queries are asking about vibes, comparisons, and advice ("is MIS respected?", "how hard is SDS?"), the semantic distinctions it captures are sufficient.

**Production tradeoff reflection:** For a real deployed system, I would weigh at least three tradeoffs. First, context length: `all-MiniLM-L6-v2` silently truncates at 256 tokens, meaning it only embeds the first ~36% of my 700-token chunks and ignores the rest. This is a meaningful loss of signal. A longer-context model — OpenAI's `text-embedding-3-large` (8,191 tokens) or `bge-large-en-v1.5` (~512 tokens with better coverage for my chunk size) — would embed the entire chunk. Second, accuracy on domain-specific nuance: MiniLM is a general-purpose model and may not cleanly distinguish between "MIS is a backup major" and "MIS is underrated" since both involve the same vocabulary. A larger model fine-tuned on opinion or academic text might produce more discriminative embeddings for these stance-heavy queries. Third, latency vs. quality: an API-hosted model like `text-embedding-3-large` adds a network round-trip but removes the local compute constraint — acceptable for a real deployment where the corpus is embedded once offline, and query-time latency is only one embedding call per user request.

---

## Grounded Generation

**System prompt grounding instruction:**

```
You are an assistant that helps prospective UT Austin students understand the CS, MIS, SDS, and Informatics majors.

Answer ONLY using the context passages provided below. Do not use any outside knowledge.
If the provided context does not contain enough information to answer the question, respond with:
"I don't have enough information in my sources to answer that question."

After your answer, list the source files you drew from under the heading "Sources:".
Do not cite a source unless you actually used information from it in your answer.
```

This instruction does three things: it defines the scope (only the four majors), hard-prohibits going outside the retrieved context, specifies the exact fallback phrase so the system has a consistent "I don't know" behavior rather than hallucinating, and requires post-hoc source attribution so the answer is auditable.

**How source attribution is surfaced in the response:** Source attribution is handled structurally, not left to the model's judgment. Each retrieved chunk is passed to the LLM with its source filename prepended as a label (e.g., `[SOURCE: reddit_cs_vs_mis_ece.txt]`). The system prompt instructs the model to list any source labels it drew from under a "Sources:" heading at the end of its response. Because the labels are embedded in the context itself rather than described abstractly, the model does not need to infer which document it is citing — it simply echoes the label it was given.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | How competitive is direct admission to UT CS, and what do students say about realistic odds? | Extremely competitive; many strong applicants rejected; advised to have a backup major or plan an internal transfer | Described CS direct admission as highly selective, cited stats like top 6% class rank being insufficient alone, mentioned internal transfer as a common fallback path, and noted the admissions blog's advice to consider MIS or SDS as alternatives | Relevant | Accurate |
| 2 | What career outcomes or job paths do students associate with the MIS major? | Product management, tech consulting, analytics | Mentioned product management, business analyst roles, tech consulting, and data analytics; one retrieved chunk noted that MIS grads tend to end up at "Big 4 consulting or mid-size tech companies" rather than FAANG | Relevant | Accurate |
| 3 | When UT students compare CS, MIS, and ECE for someone wanting "software with business," what do they recommend? | Major in CS or ECE, add business via a minor/certificate; CS + business minor beats MIS; ECE is not hardware-only | Correctly surfaced the dominant advice to major in CS and add the Elements of Computing certificate or a business minor; noted ECE is flexible; accurately captured that multiple commenters pushed back on MIS as a primary path for someone who wants to be a software engineer | Relevant | Accurate |
| 4 | What do students say about the difficulty of SDS coursework and whether you need prior coding experience? | Not especially hard but coding-heavy; prior coding not required; freshman courses teach R; Python suggested | Retrieved two chunks from the SDS coursework thread. Response said freshman courses are "pretty easy" and get harder sophomore year, that no prior coding experience is required since the program teaches R, and that a MacBook works fine — all consistent with expected answer. Did not surface the Python brushup suggestion from one commenter. | Partially relevant | Partially accurate |
| 5 | What do students say about UT's Informatics program and job prospects for it? | Small program (~100 undergrads), launched Fall 2021, positive but candid about the field being new and unknown to employers; student hadn't landed an internship yet | Surfaced the Informatics thread and the texadmissions blog post. Correctly noted the program launched Fall 2021, is small, and that Austin's tech market is growing. Did not surface the detail that the student posting hadn't landed an internship yet — that comment was in a lower-ranked chunk that fell outside top-k. | Partially relevant | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** "What do students say about the difficulty of SDS coursework and whether you need prior coding experience?" (Question 4)

**What the system returned:** The response correctly described the general difficulty arc and the R requirement, but omitted the suggestion to lightly brush up on Python before starting and missed that this advice came from a specific commenter (Dangerous-Basil1561) whose comment was split from the main SDS difficulty discussion.

**Root cause (tied to a specific pipeline stage):** This is a retrieval-stage failure caused by an answer being distributed across two separate comments by different users. My 700-token chunks kept each individual comment intact — which is correct chunking behavior — but no single chunk contained both the "R is taught from scratch" information and the "brush up on Python beforehand" advice, because those were written by different commenters in the same thread. When retrieval ran with top-k = 4, it returned the chunks with the strongest individual similarity to the query. The Python-suggestion chunk ranked 5th and was dropped. The model never saw it.

**What you would change to fix it:** Two changes would help. First, increasing top-k from 4 to 6 or 7 for this domain, where answer-relevant content is routinely split across commenters, would give the model a better chance of seeing both relevant chunks. The cost is slightly noisier context, but the chunks are large enough that 6–7 is still manageable. Second, I could implement a simple re-ranking pass after initial retrieval: retrieve top-10 by embedding similarity, then score each chunk's relevance to the query using a lightweight cross-encoder, and pass only the top 5 re-ranked chunks to generation. Cross-encoders can distinguish "this chunk is about SDS coding difficulty" from "this chunk mentions coding but is about MIS" more reliably than embedding similarity alone, which would help surface the Python-suggestion chunk even when its embedding is slightly less similar than a less-useful but higher-scoring chunk.

---

## Spec Reflection

**One way the spec helped you during implementation:** The anticipated challenges section in planning.md called out boilerplate contamination as a specific risk, naming the exact patterns to strip (nav text, the "best study spots" blob, trailing subreddit link lists). Having this written down before implementation meant that when I wrote the preprocessing step, I had a concrete checklist to work against rather than discovering the problem mid-pipeline after bad chunks had already been embedded. It also shaped how I verified the chunking output — I specifically printed random chunks and scanned for the r/banjo link as a litmus test that cleaning had worked.

**One way your implementation diverged from the spec, and why:** The spec set top-k at 4–5, framed as a starting point to tune after seeing real retrieval results. After testing, I found that for multi-commenter threads where the full answer is distributed across users, k = 4 consistently missed at least one relevant chunk on 3 of my 5 test questions. I settled on k = 5 as the default rather than the lower end of the range, and flagged in the failure case analysis that even k = 5 was insufficient for Question 4. The spec correctly anticipated this as a risk but underestimated how often it would actually fire — nearly every substantive question draws on at least two different commenters' chunks.

> **Note on repository structure:** The project repo is forked from the course-provided template, which supplied the planning.md scaffolding, the folder structure, and a bare-bones JS starter file. No pipeline logic was pre-written in the template — the starter file was an empty shell with placeholder comments. All code in the repo (ingestion, chunking, embedding, retrieval, generation, and the Gradio interface) was written by me from scratch using the template only as a structural starting point.

---

## AI Usage

> **Note on repository structure:** The repo is a fork of the course template, which provided planning.md and a bare JS skeleton with no logic. Every line of pipeline code — ingestion, chunking, embedding, retrieval, and generation — is my own. AI tools were used as described below to help implement specific functions; in each case I directed the output, verified it against my spec, and modified it before it went into the codebase.

**Instance 1**

- *What I gave the AI:* I gave Claude my Chunking Strategy section from planning.md (700 tokens, 100 overlap, recursive splitting) along with a description of the two document shapes in my corpus (short Reddit threads vs. long catalog pages) and a specific list of boilerplate patterns to strip, taken directly from my Anticipated Challenges section. The template provided no chunking code — I was implementing this entirely from my spec.
- *What it produced:* Claude returned a `preprocess_and_chunk()` function using LangChain's `RecursiveCharacterTextSplitter` with `chunk_size=700` and `chunk_overlap=100`, plus a regex-based cleaning step that stripped the boilerplate patterns I listed. It also added metadata tagging (source filename) on each chunk.
- *What I changed or overrode:* The generated cleaner used `re.sub` on a single combined pattern, which caused it to over-strip some catalog section headers that happened to contain the word "Skip." I broke the cleaning into sequential named passes instead — one for nav text, one for ad blocks, one for subreddit links — so I could debug each step independently and confirm in printed output that catalog content was preserved.

**Instance 2**

- *What I gave the AI:* I gave Claude my Grounded Generation section from planning.md — specifically the requirement that the system must refuse out-of-scope questions with a consistent phrase, surface source attribution structurally rather than leaving it to the model, and handle contested questions by presenting multiple perspectives. I also gave it the Groq LLM API setup I had already written (the template had no generation code) and asked it to wire retrieval output into a grounded generation call.
- *What it produced:* Claude generated a `generate_response()` function that prepended each retrieved chunk with a `[SOURCE: filename]` label, assembled them into a context block, and called the LLM with a system prompt. The system prompt it wrote told the model to "only use the provided context" and to "cite sources at the end."
- *What I changed or overrode:* The generated system prompt was too vague — "cite sources at the end" left open what format and didn't specify the fallback behavior for out-of-scope questions. I replaced it with the explicit instruction shown in the Grounded Generation section above, adding the exact fallback phrase ("I don't have enough information in my sources to answer that question") and the rule that the model should not cite a source unless it actually used it. I also added a test at the end of the verification step where I deliberately asked an out-of-scope question ("What is the best dining hall at UT?") to confirm the refusal fired correctly.
