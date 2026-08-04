from langchain_components.chains.evaluation_chain import evaluation_chain
from langchain_components.chains.hallucination_chain import hallucination_chain

import json
import json

class EvaluationService:

    def __init__(self):

        pass

    async def evaluate_groundedness(self,question,context,answer,):
        prompt = f"""
        
            Question:

            {question}

            Context:

            {context}

            Answer:

            {answer}

            Determine whether the answer
            is fully supported by the context.

            Return JSON only:

            {{
            "score": 0-10,
            "grounded": true or false,
            "reason": "short explanation"
            }}
            """

        evaluation = await evaluation_chain.ainvoke(
    {
        "question": question,
        "context": context,
        "answer": answer,
    }
)

        return json.loads(evaluation)
    
    async def detect_hallucination(self,context,answer,):

        prompt = f"""
Context:

{context}

Answer:

{answer}

Determine whether the answer
contains information not present
in the context.

Return JSON only:

{{
    "hallucination": true or false,
    "reason": "short explanation"
}}
"""

        result = await hallucination_chain.ainvoke(
    {
        "context": context,
        "answer": answer,
    }
)

        return json.loads(result)


    async def evaluate(self,question,context,answer,):

        groundedness = await (self.evaluate_groundedness(question,context,answer,))

        hallucination = await (
        self.detect_hallucination(context,answer,))

        return {"groundedness":groundedness,"hallucination":hallucination,}
    
