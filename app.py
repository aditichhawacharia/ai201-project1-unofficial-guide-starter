import gradio as gr
from query import ask

UT_THEME = gr.themes.Default(
    primary_hue=gr.themes.colors.orange,
    secondary_hue=gr.themes.colors.neutral,
    neutral_hue=gr.themes.colors.neutral,
    font=gr.themes.GoogleFont("Inter"),
).set(
    button_primary_background_fill="#BF5700",
    button_primary_background_fill_hover="#9E4700",
    button_primary_text_color="white",
    block_label_text_color="#BF5700",
    block_title_text_color="#BF5700",
)

EXAMPLE_QUESTIONS = [
    "How good is MIS for product management?",
    "How hard is it to get into CS at UT Austin?",
    "Should I pick CS, MIS, or Informatics?",
    "What are the best MIS electives?",
    "Is ECE worth it for software engineering?",
]

def handle_query(question):
    if not question.strip():
        return "Please enter a question.", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources

with gr.Blocks(title="UT Austin Major Guide") as demo:  # theme moved to launch()
    gr.Markdown("""
    # 🤘 UT Austin Unofficial Major Guide
    ### Your AI-powered guide to choosing the right major — built from real student experiences
    *Answers are grounded in Reddit posts, blogs, and official UT sources. Not affiliated with UT Austin.*
    """)

    with gr.Row():
        with gr.Column(scale=3):
            inp = gr.Textbox(
                label="Ask a question about UT Austin majors",
                placeholder="e.g. How good is MIS for product management?",
                lines=2
            )
            btn = gr.Button("Ask 🔍", variant="primary", size="lg")

        with gr.Column(scale=1):
            gr.Markdown("**💡 Try asking:**")
            gr.Examples(
                examples=[[q] for q in EXAMPLE_QUESTIONS],
                inputs=inp,
                label="Example questions"
            )

    with gr.Row():
        answer = gr.Textbox(
            label="Answer",
            lines=10,
            # show_copy_button removed — not supported in this version
        )

    with gr.Row():
        sources = gr.Textbox(
            label="📄 Retrieved from these sources",
            lines=3,
            interactive=False
        )

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

    gr.Markdown("---\n*Built with ChromaDB · LangChain · Groq LLaMA 3.3 · Sentence Transformers*")

demo.launch(theme=UT_THEME)  # theme goes here in Gradio 6