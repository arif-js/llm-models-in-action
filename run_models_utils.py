
def run_sql_query(sql_chain, query: str) -> str:
    return sql_chain.invoke({ "question": query })

def run_conversational_tool(llm, query: str) -> str:
    return llm.invoke(query)
