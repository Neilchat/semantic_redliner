import json

from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer

import config
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI

from strategies.agentic_compare.prompt_store import agent_with_url_prompt, agent_without_url_prompt


def compare_entities(aspect, vectorstore2015, vectorstore2023, filter=False, use_url=False):
    retriever_2015 = vectorstore2015.as_retriever(search_type="similarity_score_threshold",
                                                  search_kwargs={"score_threshold": .5, "k": 3})

    retriever_2023 = vectorstore2023.as_retriever(search_kwargs={"score_threshold": .5, "k": 3})

    bs_transformer = BeautifulSoupTransformer()

    # Define retrieval tools
    def retrieve_context_2015(query):
        """Retrieve relevant context from 2015 report"""
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
        """Retrieve relevant context from 2023 report"""
        results = retriever_2023.get_relevant_documents(query, k=3)
        q = query.strip().replace("\"", "").lower()
        if filter:
            r = "\n".join([doc.page_content for doc in results if q in doc.page_content.lower()])
        else:
            r = "\n".join([doc.page_content for doc in results])
        if len(r) == 0:
            return f"The 2023 report does not mention {q} at all."
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
        llm = ChatOpenAI(openai_api_key=config.API_KEY, model=config.config.openai_model_name, temperature=0)
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

    retrieve_text_from_url_tool = Tool(
        name="RetrieveURLText",
        func=get_text_from_url,
        description="Retrieves relevant context from any url found in the retrieved document contexts"
    )

    compare_tool = Tool(
        name="CompareContexts",
        func=compare_contexts_tool,
        description="Compares two contexts based on an aspect. Input: (context_2015, context_2023, aspect)."
    )

    # Initialize Langchain ReAct Agent
    llm = ChatOpenAI(openai_api_key=config.API_KEY, model=config.config.openai_model_name, temperature=0)
    from langchain import hub
    prompt = hub.pull("hwchase17/react")
    if use_url:
        prompt.template = agent_with_url_prompt
        tools = [retrieve_2015_tool, retrieve_2023_tool, retrieve_text_from_url_tool]
    else:
        prompt.template = agent_without_url_prompt
        tools = [retrieve_2015_tool, retrieve_2023_tool]

    react_agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=react_agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5  # useful when agent is stuck in a loop
    )

    # Run agent
    response = agent_executor.invoke({"input": f"""Compare the 2015 and 2023 version of Apple's Terms and Conditions report
                          with respect to information on {aspect}.\n
                         Please respond with structured summary of differences you find explaining the impact and significance of each difference.
                         """
                                      })
    return response["output"]
