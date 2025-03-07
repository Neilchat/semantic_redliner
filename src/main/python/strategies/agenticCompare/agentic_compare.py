import json
from enum import Enum
from pathlib import Path
from typing import List, Annotated, Optional

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_core.tools import tool, BaseTool, Tool
from langchain_core.tools.base import ArgsSchema
from langchain_qdrant import QdrantVectorStore
from langchain.agents import create_react_agent, AgentExecutor, initialize_agent, AgentType
from langchain_openai import ChatOpenAI

from langchain.tools.retriever import create_retriever_tool
from langchain import hub
from openai import OpenAI
from pydantic import BaseModel, Field

from config import config
from strategies.agenticCompare.prompt_store import entities_system_prompt
from strategies.agenticCompare.react_compare import compare_entities
from strategies.agenticCompare.utils import get_text_splits
from strategies.base.base_strategy import BaseStrategy
from strategies.base.strategy_config import StrategyConfig
from text_extraction.tika_parser import TikaParser


class EntityType(str, Enum):
    PRODUCT = "product"
    AMOUNT = "amount"
    POLICY = "policy"

class Entity(BaseModel):
    type: EntityType
    name: str
    description: str

class Entities(BaseModel):
    entities: List[Entity]




class AgenticCompare(BaseStrategy):
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        self.llm = ChatOpenAI(api_key=config.openai_api_key)
        self.openai_client = OpenAI(api_key=config.openai_api_key)
        self.tika_parser = TikaParser()
        self.embedder = OpenAIEmbeddings(
            deployment=config.openai_embedding_model_name,
            api_key=config.openai_api_key
        )


    def create_vector_stores(self, text2015, text2023):
        splits2015 = get_text_splits(text2015)
        splits2023 = get_text_splits(text2023)

        self.vectorstore2015 = QdrantVectorStore.from_documents(
            documents=splits2015,
            embedding=self.embedder,
            location=":memory:",
            collection_name="2015"
        )

        self.vectorstore2023 = QdrantVectorStore.from_documents(
            documents=splits2023,
            embedding=self.embedder,
            location=":memory:",
            collection_name="2023"
        )


    def compare_docs(self, docpath1, docpath2) -> str:

        self.text2015 = self.tika_parser.get_text(docpath1)
        self.text2023 = self.tika_parser.get_text(docpath2)

        self.create_vector_stores(self.text2015, self.text2023)

        self.entities2015 = self.extract_entities(self.text2015, "2015")
        self.entities2023 = self.extract_entities(self.text2023, "2023")
        self.entities2023.entities.extend(self.entities2015.entities)

        combined_entities = {}
        for entity in self.entities2023.entities:
            if entity.name in combined_entities:
                pass
            else:
                combined_entities[entity.name] = {"description": entity.description, "type": entity.type.title()}
        results_path = "/Users/saswata/Documents/semantic_redliner/src/main/python/data/results/agenticComparePolicy.txt"
        with open(results_path, 'w') as f:
            f.write("Difference Summaries\n\n\n POLICY \n")
        with open(results_path, 'r') as f:
            contents = f.read()

        for name in combined_entities:
            desc = combined_entities[name]["description"]
            type = combined_entities[name]["type"]
            if type.lower() == "policy" and "__________________"+name+"_____________________" not in contents:
                with open(results_path, 'a') as f:
                    f.write("\n\n__________________"+name+"_____________________\n\n")
                res = compare_entities(name, self.vectorstore2015, self.vectorstore2023)
                with open(results_path, 'a') as f:
                    f.write(res)
                    f.write("\n\n")

        with open(results_path, 'r') as f:
            contents = f.read()
        return contents

        # self.create_vector_stores(self.text2015, self.text2023)
        #
        # return self.compare_entity(query="What are the difference in two versions (2015 and 2023) in terms of family sharing. "
        #                                  "Explain the difference using bullet points, expanding on the signifcance and impact of difference.")


    def extract_entities(self, text, year):

        user_prompt = \
            f""" 
        Please help me extract the entities following piece of text into a graph using the structured output format.

        ***Document Text***
        {text}

        """
        completion_parameters = {"model": self.config.openai_model_name,
                                 "messages": [{"role": "system",
                                               "content": entities_system_prompt},
                                              {"role": "user",
                                               "content": user_prompt}],
                                 "temperature": 0.0,
                                 "response_format": Entities}

        my_file = Path(f"/Users/saswata/Documents/semantic_redliner/src/main/python/data/entities_{year}.json")
        if my_file.is_file():
            with open(f'/Users/saswata/Documents/semantic_redliner/src/main/python/data/entities_{year}.json') as f:
                entities_json = json.load(f)
            entities = Entities(**entities_json)

        else:
            entities = self.openai_client.beta.chat.completions.parse(**completion_parameters).choices[0].message.parsed
            print(entities)
            dict = entities.dict()
            json_data = json.dumps(dict)
            with open(f"/Users/saswata/Documents/semantic_redliner/src/main/python/data/entities_{year}.json",
                      "w") as file:
                file.write(json_data)

        return entities

