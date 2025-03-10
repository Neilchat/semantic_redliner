import json

from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer

import config
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI

from strategies.agentic_compare.prompt_store import agent_with_url_prompt, agent_without_url_prompt


def compare_entities(aspect, vectorstore1, vectorstore2, filter=False, use_url=False):
    retriever_1 = vectorstore1.as_retriever(search_type="similarity_score_threshold",
                                                  search_kwargs={"score_threshold": .5, "k": 3})

    retriever_2 = vectorstore2.as_retriever(search_kwargs={"score_threshold": .5, "k": 3})

    bs_transformer = BeautifulSoupTransformer()

    # Define retrieval tools
    def retrieve_context_1(query):
        """Retrieve relevant context from 1 report"""
        results = retriever_1.get_relevant_documents(query, k=3)
        q = query.strip().replace("\"", "").lower()
        if filter:
            r = "\n".join([doc.page_content for doc in results if q in doc.page_content.lower()])
        else:
            r = "\n".join([doc.page_content for doc in results])
        if len(r) == 0:
            return f"The 1 report does not mention {q} at all."
        return r

    def retrieve_context_2(query):
        """Retrieve relevant context from 2 report"""
        results = retriever_2.get_relevant_documents(query, k=3)
        q = query.strip().replace("\"", "").lower()
        if filter:
            r = "\n".join([doc.page_content for doc in results if q in doc.page_content.lower()])
        else:
            r = "\n".join([doc.page_content for doc in results])
        if len(r) == 0:
            return f"The 2 report does not mention {q} at all."
        return r

    # TODO this needs to expand to take as input the document year, return that with the response
    #  It also needs to check when the page was last updated and that it corresponds to the year asked for
    #  It also needs to extract all the text well, currently just p which seems to work for most of these apple links
    #  If text is too large a semantic similarity search over it is required
    #  Disabled for now.

    def get_text_from_url(url):
        """Retrieve relevant context from url"""
        loader = AsyncChromiumLoader([url])
        html = loader.load()
        docs_transformed = bs_transformer.transform_documents(html, tags_to_extract=["p"])
        return docs_transformed[0].page_content[:5000]

    # Define comparison tool
    def compare_contexts(context_1, context_2, aspect):
        """Compare the two contexts based on a given aspect"""
        prompt = f"""
        Compare the following two texts based on the aspect: {aspect}

        1 Terms and Conditions Context:
        {context_1}

        2 Terms and Conditions Context:
        {context_2}

        Provide a structured summary of differences. Explaining the impact and significance of each difference.
        """
        llm = ChatOpenAI(openai_api_key=config.API_KEY, model=config.config.openai_model_name, temperature=0)
        return llm.predict(prompt)

    def compare_contexts_tool(input_dict):
        """Wrapper function to allow multi-input comparison"""
        json_ = json.loads(input_dict)
        return compare_contexts(json_["context_1"], json_["context_2"], json_["aspect"])

    # Define Langchain tools
    retrieve_1_tool = Tool(
        name="RetrieveContext1",
        func=retrieve_context_1,
        description="Retrieves relevant context from Document 1 based on a query."
    )

    retrieve_2_tool = Tool(
        name="RetrieveContext2",
        func=retrieve_context_2,
        description="Retrieves relevant context from Document 2 based on a query."
    )

    retrieve_text_from_url_tool = Tool(
        name="RetrieveURLText",
        func=get_text_from_url,
        description="Retrieves relevant context from any url found in the retrieved document contexts"
    )

    compare_tool = Tool(
        name="CompareContexts",
        func=compare_contexts_tool,
        description="Compares two contexts based on an aspect. Input: (context_1, context_2, aspect)."
    )

    # Initialize Langchain ReAct Agent
    llm = ChatOpenAI(openai_api_key=config.API_KEY, model=config.config.openai_model_name, temperature=0)
    from langchain import hub
    prompt = hub.pull("hwchase17/react")
    if use_url:
        prompt.template = agent_with_url_prompt
        tools = [retrieve_1_tool, retrieve_2_tool, retrieve_text_from_url_tool]
    else:
        prompt.template = agent_without_url_prompt
        tools = [retrieve_1_tool, retrieve_2_tool]

    react_agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=react_agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5  # useful when agent is stuck in a loop
    )

    # Run agent
    response = agent_executor.invoke({"input": f"""Compare the two version of a company's Terms and Conditions report with respect to information on {aspect}.\n
                         Please respond with structured summary of differences you find explaining the impact and significance of each difference.
                         """
                                      })
    return response["output"]
