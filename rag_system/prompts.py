from langchain.prompts import PromptTemplate

COMPLIANCE_PROMPT_TEMPLATE = """
🚀 Hello developer!

You are an AI assistant specialized in software compliance and code optimization.

Given:

1. Relevant excerpts from company policy documents (compliance context).
2. A code snippet submitted by a developer.

Please analyze the code and respond in two sections:

---

### Critical Compliance Issues (must fix)

- Identify each compliance violation by exact line(s) or function(s).
- Provide a clear, concise explanation.
- For each issue, suggest an alternative compliant code snippet or approach.
- Keep it factual and easy to understand.

---

### Less Critical Optimization Suggestions

- Provide practical tips to improve code quality or performance.
- These are recommendations, not mandatory fixes.
- Keep suggestions brief and actionable.

---

### Context (policy excerpts):
{context}

### Code Snippet:
{question}

### Your detailed response below:
"""

def get_prompt():
    return PromptTemplate(
        template=COMPLIANCE_PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )
