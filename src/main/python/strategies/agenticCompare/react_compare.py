import json
import config
from langchain.agents import initialize_agent, AgentType, create_react_agent, AgentExecutor
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings

def compare_entities(aspect, vectorstore2015, vectorstore2023, filter = False):

    retriever_2015 = vectorstore2015.as_retriever(search_type="similarity_score_threshold",
                                                  search_kwargs={"score_threshold": .5, "k": 3})
    retriever_2023 = vectorstore2023.as_retriever(search_kwargs={"score_threshold": .5, "k": 3})

    # Define retrieval tools
    def retrieve_context_2015(query):
        """Retrieve relevant context from Document 1"""
        results = retriever_2015.get_relevant_documents(query, k=3)
        q = query.strip().replace("\"", "").lower()
        if filter:
            r = "\n".join([doc.page_content for doc in results if q in doc.page_content.lower()])
        else:
            r = "\n".join([doc.page_content for doc in results])
        if len(r) == 0:
            return f"The 2015 report does not mention {q} at all."
        return r



    def retrieve_context_2023(query):
        """Retrieve relevant context from Document 2"""
        results = retriever_2023.get_relevant_documents(query, k=3)
        q = query.strip().replace("\"", "").lower()
        if filter:
            r = "\n".join([doc.page_content for doc in results if q in doc.page_content.lower()])
        else:
            r = "\n".join([doc.page_content for doc in results])
        if len(r) == 0:
            return f"The 2023 report does not mention {q} at all."
        return r

    # Define comparison tool
    def compare_contexts(context_2015, context_2023, aspect):
        """Compare the two contexts based on a given aspect"""
        prompt = f"""
        Compare the following two texts based on the aspect: {aspect}

        2015 Terms and Conditions Context:
        {context_2015}

        2023 Terms and Conditions Context:
        {context_2023}

        Provide a structured summary of differences. Explaining the impact and significance of each difference.
        """
        llm = ChatOpenAI(openai_api_key=config.API_KEY, model="gpt-4o-mini", temperature=0)
        return llm.predict(prompt)


    def compare_contexts_tool(input_dict):
        """Wrapper function to allow multi-input comparison"""
        json_ = json.loads(input_dict)
        return compare_contexts(json_["context_2015"], json_["context_2023"], json_["aspect"])


    # Define Langchain tools
    retrieve_2015_tool = Tool(
        name="RetrieveContext2015",
        func=retrieve_context_2015,
        description="Retrieves relevant context from Document 1 based on a query."
    )

    retrieve_2023_tool = Tool(
        name="RetrieveContext2023",
        func=retrieve_context_2023,
        description="Retrieves relevant context from Document 2 based on a query."
    )

    compare_tool = Tool(
        name="CompareContexts",
        func=compare_contexts_tool,
        description="Compares two contexts based on an aspect. Input: (context_2015, context_2023, aspect)."
    )

    # Initialize Langchain ReAct Agent
    llm = ChatOpenAI(openai_api_key=config.API_KEY, model="gpt-4o-mini", temperature=0)
    from langchain import hub
    prompt = hub.pull("hwchase17/react")
    print(prompt.template)
    prompt.template = """
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format. Follow the step EXACTLY and in SEQUENCE:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action

Final Answer: A structured and detailed summary of the difference in the two documents regarding the given aspect.

Begin!

Question: {input}
Thought:{agent_scratchpad}
    """
    react_agent = create_react_agent(llm, [retrieve_2015_tool, retrieve_2023_tool], prompt)
    agent_executor = AgentExecutor(
        agent=react_agent,
        tools=[retrieve_2015_tool, retrieve_2023_tool],
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=4  # useful when agent is stuck in a loop
    )

    # Run agent
    response = agent_executor.invoke({"input":f"""Compare the 2015 and 2023 version of Apple's Terms and Conditions report
                          with respect to information on {aspect}.\n
                         Please respond with structured summary of differences you find explaining the impact and significance of each difference.
                         """
    })
    return response["output"]
