# The Unofficial Guide — Project 1

> **Repository note:** This repository is forked from the CodePath Applied AI Engineering Fellowship course template for Project 1: building a production RAG system from scratch.
> The template ONLY provided the planning.md scaffolding and document structure used for spec planning.
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

### Sample Chunks

**Chunk 1 — `sds_degree_plan_official.txt` (official)**
```
The Bachelor of Science in Statistics and Data Science equips students to execute all stages
of data analysis, apply common techniques in statistics and machine learning, respect the
principles and best practices of reproducible data science and articulate the role of
statistics and data science in a just and ethical society. The program provides a strong
foundation in the established field of statistics while reaching into the modern and emerging
field of data science.

Admissions

The Bachelor of Science in Statistics and Data Science is available to Fall Freshman
applicants. We are currently not accepting transfer applications.
```

**Chunk 2 — `sds_degree_plan_official.txt` (official)**
```
Degree Requirements

The bachelor's degree requirements total 120 credit hours comprised of the following:

1. Seven courses in the major (22 credit hours) beginning in the first semester
   SDS 313 Introduction to Data Science
   SDS 315 Statistical Thinking
   SDS 431 Probability & Statistical Inference
   SDS 334 Intermediate Statistical Methods
   SDS 336 Practical Machine Learning
   SDS 354 Advanced Statistical Methods
   SDS 357 Case Studies in Data Science

2. Five foundational courses in Mathematics and Computer Science (17 credit hours)
   M 408C Differential Calculus
   M 408D Sequences, Series and Multivariable Calculus
   M 340L Matrices & Matrix Calculations or M 341 Linear Algebra and Matrix Theory
   C S 303E Elements of Computers and Programming
   C S 327E Elements of Databases
```

**Chunk 3 — `sds_degree_plan_official.txt` (official)**
```
Graduates of this program may be hired as statisticians or data scientists who are able to
collect and curate large volumes of data, bring statistical and machine learning methods to
bear on new questions and create data pipelines and workflows that transform digital
information into actionable insights. Perhaps most importantly, employers are looking for
individuals who are equipped with the foundational training needed to ensure that the
individuals they hire into these roles are readily able to learn and critically assess new
tools as they become available. Students will also be prepared to succeed in graduate studies.
```

**Chunk 4 — `cs_competitive_alternatives_blog.txt` (blog)**
```
It might surprise you to hear that computer science majors at UT and other top universities
have only recently become extremely competitive. During the first year that I worked at UT
in 2011, UT CS received fewer than 600 applications and admitted over 50% of its applicants.
Back then, petroleum engineering was the most desirable and competitive major since the price
of oil was around $100. However, five years later, CS received more than five times the
number of applications for around 2,700, but even then, the admissions rate was still over
20%.

UT refuses to make the CS admissions statistics public, but I suspect the range is 10,000 to
13,000 CS applicants in recent cycles while admitting 700 students.
```

**Chunk 5 — `cs_competitive_alternatives_blog.txt` (blog)**
```
UT-Austin has many programs that are adjacent to computer science. Moderately competitive
alternatives include the McCombs Management Information Systems program, Statistics and Data
Science in the College of Natural Sciences, applied math, computational biology, and physics.
The demand for data science and information-oriented careers are likely to exceed software or
computer engineering jobs over the next decade.

Somewhat less competitive majors are Informatics, the Arts and Entertainment Technologies
(AET) program in Fine Arts, and the new major in the College of Liberal Arts BS in Behavioral
and Social Data Sciences.
```

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`

I chose this model because it runs entirely locally — no API key, no rate limits, no cost per embedding call — which made iterating on chunking strategies fast and cheap. It is small enough to embed the full corpus on a laptop in under a minute and is well-suited to short-to-medium English text. For a student-opinion corpus where most queries are asking about vibes, comparisons, and advice ("is MIS respected?", "how hard is SDS?"), the semantic distinctions it captures are sufficient.

**Production tradeoff reflection:** For a real deployed system, I would weigh at least three tradeoffs. First, context length: `all-MiniLM-L6-v2` silently truncates at 256 tokens, meaning it only embeds the first ~36% of my 700-token chunks and ignores the rest. This is a meaningful loss of signal. A longer-context model — OpenAI's `text-embedding-3-large` (8,191 tokens) or `bge-large-en-v1.5` (~512 tokens with better coverage for my chunk size) — would embed the entire chunk. Second, accuracy on domain-specific nuance: MiniLM is a general-purpose model and may not cleanly distinguish between "MIS is a backup major" and "MIS is underrated" since both involve the same vocabulary. A larger model fine-tuned on opinion or academic text might produce more discriminative embeddings for these stance-heavy queries. Third, latency vs. quality: an API-hosted model like `text-embedding-3-large` adds a network round-trip but removes the local compute constraint — acceptable for a real deployment where the corpus is embedded once offline, and query-time latency is only one embedding call per user request.

---

## Retrieval — Relevant Chunks Returned for Queries

### Retrieval Test 1: "How good is MIS for product management?"

**Top 4 returned chunks (sources):**
- chunk_54 — `mis_how_is_the_major_student.txt`
- chunk_53 — `mis_how_is_the_major_student.txt`
- chunk_26 — `mis_favorite_courses_student.txt`
- chunk_5 — `mis_vs_other_majors_student.txt`

**Why these chunks are relevant:** All four chunks come from Reddit threads where students directly discuss MIS career outcomes. chunk_54 contains a current MIS major saying the degree "mostly prepares students to land tech consulting and analytics positions" and that PM roles are possible but not the natural outcome. chunk_53 contains the original post asking about MIS for product/project management plus multiple student replies weighing in on the transfer process and career fit. These are exactly the chunks needed to answer the query — they surface the dominant student opinion that MIS helps with PM interviews but CS is the stronger choice if PM at a top tech company is the goal.

---

### Retrieval Test 2: "How hard is SDS coursework?"

**Top 4 returned chunks (sources):**
- chunk_30 — `sds_coursework_student.txt`
- chunk_8 — `sds_questions_student.txt`
- chunk_1 — `sds_degree_plan_official.txt`
- chunk_2 — `sds_degree_plan_official.txt`

**Why these chunks are relevant:** chunk_30 is from a thread where a parent asks specifically about SDS coursework difficulty and CS crossover options — directly on-topic. chunk_8 comes from a student who just got into SDS asking about difficulty; it contains the key quote that "freshman SDS courses are pretty easy" but "sophomore ones are a lot harder," and also the advice to lightly brush up on Python beforehand. The two official catalog chunks (chunk_1, chunk_2) provide the formal degree requirements that contextualize what "hard" means structurally. Together these four chunks cover both the student experience angle and the official curriculum angle for this query.

---

### Retrieval Test 3: "What is the Informatics major like?"

**Top 4 returned chunks (sources):**
- chunk_57 — `informatics_new_degree_blog.txt`
- chunk_34 — `informatics_degree_plan_official.txt`
- chunk_33 — `informatics_degree_plan_official.txt`
- chunk_38 — `informatics_major_opinions_student.txt`

**Why these chunks are relevant:** chunk_57 is the texadmissions.com blog post explaining what Informatics is, who it fits, and what makes it distinctive as its own school rather than a department. chunk_38 is a Reddit post from a transfer student accepted into Informatics asking what the major is like and whether Austin's job market supports it — the exact student perspective the query is looking for. The two official catalog chunks provide the formal degree structure including concentration options (Cultural Heritage, Human-Centered Data Science, Social Justice, Health Informatics). The retrieval correctly mixed blog, official, and student sources to give a complete picture of the major.

---

## Grounded Generation with Source Attribution

**System prompt grounding instruction:**

```
You are an assistant that helps prospective UT Austin students understand the CS, MIS, SDS,
and Informatics majors.

Answer ONLY using the context passages provided below. Do not use any outside knowledge.
If the provided context does not contain enough information to answer the question, respond with:
"I don't have enough information in my sources to answer that question."

After your answer, list the source files you drew from under the heading "Sources:".
Do not cite a source unless you actually used information from it in your answer.
```

This instruction does three things: it defines the scope (only the four majors), hard-prohibits going outside the retrieved context, specifies the exact fallback phrase so the system has a consistent "I don't know" behavior rather than hallucinating, and requires post-hoc source attribution so the answer is auditable.

**How source attribution is surfaced in the response:** Source attribution is handled structurally, not left to the model's judgment. Each retrieved chunk is passed to the LLM with its source filename prepended as a label (e.g., `[SOURCE: reddit_cs_vs_mis_ece.txt]`). The system prompt instructs the model to list any source labels it drew from under a "Sources:" heading at the end of its response. Because the labels are embedded in the context itself rather than described abstractly, the model does not need to infer which document it is citing — it simply echoes the label it was given. In the Gradio interface, these sources are also displayed separately in a "Retrieved from these sources" panel beneath the answer box.

---

### Example System Response 1: "How hard is it to get into CS at UT Austin?"

> Getting into the Computer Science (CS) program at the University of Texas at Austin (UT Austin) is extremely competitive. According to (Doc 3), the number of CS applications has skyrocketed since 2015, with the program now receiving between 10,000 to 13,000 applications and admitting only around 700 students. This puts the admission rate at around 5–7%, which is significantly lower than the 20% admission rate in 2016 (Doc 3). In fact, (Doc 3) states that if you rank outside the top 10%, it's almost impossible to get into UT CS.
>
> The competitive nature of the program is also reflected in the experiences shared by students on Reddit. For example, (Doc 2) features a student who has been involved in various extracurricular activities such as CS Club, programming for a CTF competition, and NASA HUNCH, yet still expresses uncertainty about their chances of getting into the program. Another student in (Doc 4) shares their impressive academic credentials, including a 3.98 unweighted GPA and a 1500 on the SAT, but still feels anxious about the competition.
>
> While (Doc 1) provides information on the graduation requirements for the CS program, it does not offer insight into the admission process. However, (Doc 4) provides some advice from a student who has a friend currently in the UT CS program, suggesting that taking AP classes, participating in Science Olympiad, and having a strong background in math and science can be helpful.
>
> It's worth noting that UT Austin does not make its CS admissions statistics public, as mentioned in (Doc 3). However, based on the information available, it's clear that getting into the CS program at UT Austin is highly competitive and requires a strong academic record, as well as meaningful extracurricular experiences.
>
> In terms of specific advice, (Doc 2) and (Doc 4) suggest that having a strong passion for CS, demonstrated through extracurricular activities and experiences, can help increase one's chances of getting into the program. Additionally, (Doc 4) recommends showing a strong background in math and science, and taking AP courses or CS courses if available.

**Sources:**
- cs_degree_plan_official.txt
- cs_increase_chances_student.txt
- cs_competitive_alternatives_blog.txt
- cs_dream_admission_student.txt

---

### Example System Response 2: "How good is UT Austin CS?"

> You're considering the Computer Science program at UT Austin, and you want to know how good it is. According to a student on Reddit, the CS program at UT Austin is "one of the best in the nation, definitely top 10." Another student notes that the program is highly ranked across all of its specialties and has involvement from top companies like IBM, Dell, Microsoft, and Google. The Friends of Computer Science program also connects students to jobs, internships, and opportunities in big tech, which can be a huge benefit.
>
> However, some students feel that the prestige of graduating from a competitive university like UT Austin may not be as important as the effort you put into learning and your side projects. As one student on Reddit puts it, "the effort you put into learning and your side projects has a bigger impact than who is teaching or which university you attended."
>
> It's also worth noting that the CS building at UT Austin is highly regarded, with one student commenting that it's "gorgeous in and out" thanks to a $60M donation from Bill Gates. However, another student notes that the building "smells really bad."
>
> Per official UT documentation, the CS program has a rigorous set of requirements, including a University grade point average of at least 3.25 and a grade point average of at least 3.25 in computer science courses to graduate with honors.
>
> Overall, it seems that the CS program at UT Austin is highly regarded by students and has a strong reputation in the industry. However, it's also important to consider your own goals and motivations, and to remember that the quality of your education is not solely determined by the university you attend.
>
> Sources used: cs_program_quality_student.txt, informatics_major_opinions_student.txt, cs_program_quality_student.txt, cs_degree_plan_official.txt

**Retrieved from these sources:**
- cs_program_quality_student.txt
- informatics_major_opinions_student.txt
- cs_degree_plan_official.txt

---

### Out-of-Scope Query Example: "What are the best dorms at UT Austin?"

> You're looking for advice on the best dorms at UT Austin. However, I don't have enough information on that in my sources. The documents I have access to discuss the Informatics major, the quality of the CS program, and degree requirements, but they don't mention dorms. According to a student on Reddit, you're likely concerned about getting settled in Austin, but unfortunately, the conversation doesn't touch on dorms. One blog notes the new Informatics degree and its potential benefits, while another discussion among students praises the CS program, but again, no mention of dorms. Per official UT documentation, there are details on graduation and degree requirements, but nothing about dorms.
>
> Sources used: informatics_major_opinions_student.txt, informatics_new_degree_blog.txt, cs_program_quality_student.txt, cs_degree_plan_official.txt

**Note on this refusal:** The system correctly identified that dorm information is outside its source corpus and stated it lacked sufficient information. The response demonstrates the grounding instruction working as intended — the model did not invent dorm recommendations. However, it slightly over-explained by summarizing what the sources do cover rather than returning the clean fallback phrase. This is a known behavior of the LLM rationalizing around the constraint rather than obeying it strictly, and could be tightened with a more directive system prompt.

---

## Query Interface

The system is built as a Gradio web app with the following layout:

**Input fields:**
- A labeled text box: *"Ask a question about UT Austin majors"* — accepts free-text natural language questions from the user
- A large orange **Ask 🔍** button to submit the query
- A sidebar panel labeled *"💡 Try asking:"* with five clickable example questions that auto-populate the input field: "How good is MIS for product management?", "How hard is it to get into CS at UT Austin?", "Should I pick CS, MIS, or Informatics?", "What are the best MIS electives?", and "Is ECE worth it for software engineering?"

**Output fields:**
- An **Answer** panel displaying the full LLM-generated response, grounded in the retrieved context
- A collapsible **📄 Retrieved from these sources** panel listing the filenames of the source documents used

**Stack displayed in footer:** ChromaDB · LangChain · Groq LLaMA 3.3 · Sentence Transformers

---

### Sample Interaction Transcript

**Query:** `how hard is it to get into CS at UT Austin?`

**Answer:**
Getting into the Computer Science (CS) program at the University of Texas at Austin (UT Austin) is extremely competitive. According to (Doc 3), the number of CS applications has skyrocketed since 2015, with the program now receiving between 10,000 to 13,000 applications and admitting only around 700 students. This puts the admission rate at around 5–7%, which is significantly lower than the 20% admission rate in 2016 (Doc 3). In fact, (Doc 3) states that if you rank outside the top 10%, it's almost impossible to get into UT CS.

The competitive nature of the program is also reflected in the experiences shared by students on Reddit. For example, (Doc 2) features a student involved in CS Club, a CTF competition, and NASA HUNCH, yet still uncertain about their chances. Another student in (Doc 4) has a 3.98 unweighted GPA and a 1500 SAT but still feels anxious about the competition.

In terms of specific advice, (Doc 2) and (Doc 4) suggest that demonstrating a strong passion for CS through extracurriculars can help. Additionally, (Doc 4) recommends a strong background in math and science and taking AP or CS courses if available.

**Retrieved from these sources:**
- cs_degree_plan_official.txt
- cs_increase_chances_student.txt
- cs_competitive_alternatives_blog.txt
- cs_dream_admission_student.txt

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | How competitive is direct admission to UT CS, and what do students say about realistic odds? | Extremely competitive; many strong applicants rejected; advised to have a backup major or plan an internal transfer | Described CS direct admission as highly selective, cited stats like top 6% class rank being insufficient alone, mentioned internal transfer as a common fallback path, and noted the admissions blog's advice to consider MIS or SDS as alternatives | Relevant | Accurate |
| 2 | What career outcomes or job paths do students associate with the MIS major? | Product management, tech consulting, analytics | Mentioned product management, business analyst roles, tech consulting, and data analytics; one retrieved chunk noted that MIS grads tend to end up at "Big 4 consulting or mid-size tech companies" rather than FAANG | Relevant | Accurate |
| 3 | When UT students compare CS, MIS, and ECE for someone wanting "software with business," what do they recommend? | Major in CS or ECE, add business via a minor/certificate; CS + business minor beats MIS; ECE is not hardware-only | Correctly surfaced the dominant advice to major in CS and add the Elements of Computing certificate or a business minor; noted ECE is flexible; accurately captured that multiple commenters pushed back on MIS as a primary path for someone who wants to be a software engineer | Relevant | Accurate |
| 4 | What do students say about the difficulty of SDS coursework and whether you need prior coding experience? | Not especially hard but coding-heavy; prior coding not required; freshman courses teach R; Python suggested | Retrieved two chunks from the SDS coursework thread. Response said freshman courses are "pretty easy" and get harder sophomore year, that no prior coding experience is required since the program teaches R, and that a MacBook works fine — all consistent with expected answer. Did not surface the Python brushup suggestion from one commenter. | Partially relevant | Partially accurate |
| 5 | What do students say about UT's Informatics program and job prospects for it? | Small program (~100 undergrads), launched Fall 2021, positive but candid about the field being new and unknown to employers; student hadn't landed an internship yet | Surfaced the Informatics thread and the texadmissions blog post. Correctly noted the program launched Fall 2021, is small, and that Austin's tech market is growing. Did not surface the detail that the student posting hadn't landed an internship yet — that comment was in a lower-ranked chunk that fell outside top-k. | Partially relevant | Partially accurate |

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

---

## AI Usage

**Instance 1 — Planning and spec outline:** I used Claude to help structure planning.md before implementation began. I described the domain (UT Austin major comparisons, Reddit + official sources) and the four pipeline stages I was planning, and asked it to help think through what sections the spec should cover and what risks were worth naming in the anticipated challenges section. I then reviewed the output and revised it significantly — I added the specific boilerplate patterns I had already noticed in the Reddit source files (the r/banjo link, the nav header text), sharpened the expected answers in the evaluation plan to be more specific and verifiable, and cut two generic risks that didn't actually apply to this corpus. The final planning.md reflects my own judgments about this specific domain; the AI helped me not miss any structural sections.

**Instance 2 — Chunking and retrieval strategy:** I talked through the chunking tradeoff with Claude before writing the pipeline. Specifically, I described the two document shapes in my corpus — short Reddit comments and dense catalog blocks — and asked whether a single chunk size could reasonably serve both. The AI walked through the tradeoff between preserving comment-level granularity and keeping catalog requirements intact, which confirmed my intuition toward 700 tokens and helped me articulate why recursive splitting was the right splitter choice over character-based splitting. I wrote all the pipeline code myself; this conversation informed the reasoning I later documented in the README, but the actual implementation decisions and code were mine.

---

> **Note on repository structure:** The project repo is forked from the course-provided template, which supplied the planning.md scaffolding, the folder structure, and a bare-bones JS starter file. No pipeline logic was pre-written in the template — the starter file was an empty shell with placeholder comments. All pipeline code in the repo (ingestion, chunking, embedding, retrieval, generation, and the Gradio interface) was written by me from scratch using the template only as a structural starting point.
