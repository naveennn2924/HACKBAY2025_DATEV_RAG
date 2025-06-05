from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from .prompts import get_prompt

def get_qa_chain(temperature=0.7, max_tokens=1024):
    llm = OpenAI(temperature=temperature, max_tokens=max_tokens)
    prompt = get_prompt()
    chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)
    return chain

def get_answer(docs, question):
    chain = get_qa_chain()
    response = chain({"input_documents": docs, "question": question}, return_only_outputs=True)
    return response["output_text"]
