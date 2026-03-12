from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from src.common.config import get_settings

settings = get_settings()


class RAGState(TypedDict):
    question: str
    context: str
    answer: str


def _build_graph():
    llm = ChatGroq(
        api_key=settings.groq_api_key, model=settings.groq_model, temperature=0.1
    )

    def answer_node(state: RAGState):
        prompt = (
            "You are a helpful assistant for retrieval-augmented QA. "
            "Answer using the context. If not enough context, say that clearly.\n\n"
            f"Context:\n{state['context']}\n\n"
            f"Question: {state['question']}"
        )
        out = llm.invoke(prompt)
        return {"answer": out.content}

    graph = StateGraph(RAGState)
    graph.add_node("generate_answer", answer_node)
    graph.add_edge(START, "generate_answer")
    graph.add_edge("generate_answer", END)
    return graph.compile()


def ask_rag(question: str, docs: list) -> str:
    if not settings.groq_api_key:
        return "GROQ_API_KEY is missing. Add it to backend/.env."
    context = "\n\n".join(d.page_content for d in docs) if docs else ""
    graph = _build_graph()
    out = graph.invoke({"question": question, "context": context, "answer": ""})
    return out.get("answer", "No answer generated")
