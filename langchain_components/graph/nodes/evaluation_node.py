from langchain_components.chains.evaluation_chain import ( evaluation_chain,)


def evaluation_node( state,):
    """Evaluates whether the answer is grounded in the retrieved context."""
    evaluation = (
        evaluation_chain.invoke(
            {
                "question":
                    state["question"],

                "context":
                    state["context"],

                "answer":
                    state["answer"],
            }
        )
    )

    return { "evaluation": evaluation}