from langchain.prompts import PromptTemplate

COMPLIANCE_PROMPT_TEMPLATE = """
🚀 Hello developer!

You are an AI assistant specialized in software compliance and code optimization.

Given:

1. Relevant excerpts from company policy documents (compliance context).
2. A code snippet submitted by a developer.

Please analyze the code and respond with the following sections:

---

### Critical Compliance Issues (must fix)

- List each compliance violation by exact line(s) or function(s).
- Provide concise, actionable fix suggestions.
- Suggest alternative compliant code snippets if applicable.

---

### Code Optimization Suggestions

- Provide brief tips to improve code quality or performance.

---

### Improved and Optimized Code

- Provide the full improved and optimized version of the original code snippet.
- The code should comply with all policies and incorporate optimization tips.

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
