from datasets.evaluation_dataset import (EVALUATION_DATASET,)

from models.benchmark_message import (BenchmarkMessage,)
class BenchmarkService:

    def __init__(self,conversational_rag_service,):

        self.conversational_rag_service = (conversational_rag_service)

    async def run_benchmark(self,):

        results = []

        for item in (EVALUATION_DATASET):

            question = (item["question"])

            expected = (item["expected"])

            messages = [BenchmarkMessage(role="user",content=question,)]

            answer = await (self.conversational_rag_service.answer_question(messages))

            results.append(
            {
                "question":
                    question,

                "expected":
                    expected,

                "answer":
                    answer,
            }
        )

        summary = self.calculate_summary(results)

        return {"summary": summary,"results": results,}

    def calculate_summary(self, results):
        total_questions = len(results)

        total_score = 0
        hallucinations = 0

        for item in results:
            evaluation = item["answer"]["evaluation"]

            total_score += evaluation["groundedness"]["score"]

            if evaluation["hallucination"]["hallucination"]:
                hallucinations += 1

        average_score = total_score / total_questions
        pass_rate = ((total_questions - hallucinations) / total_questions) * 100

        return {
        "total_questions": total_questions,
        "average_score": average_score,
        "hallucinations": hallucinations,
        "pass_rate": pass_rate,
        }