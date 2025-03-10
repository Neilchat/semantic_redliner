import json
from enum import Enum
from pathlib import Path
from typing import List

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_openai import ChatOpenAI

from openai import OpenAI

from pydantic import BaseModel

from strategies.agentic_compare.final_report_generator import FinalReportGenerator
from strategies.agentic_compare.prompt_store import entities_system_prompt
from strategies.agentic_compare.react_compare_entity import compare_entities
from strategies.agentic_compare.utils import get_text_splits
from strategies.base.base_strategy import BaseStrategy
from strategies.base.strategy_config import StrategyConfig
from text_extraction.tika_parser import TikaParser


class EntityType(str, Enum):
    PRODUCT = "product"
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
        self.vectorstore2 = None
        self.vectorstore1 = None

    def create_vector_stores(self, text1, text2):

        # TODO here instead of random chunks using sections from graph extract module will make it better
        splits1 = get_text_splits(text1)
        splits2 = get_text_splits(text2)

        self.vectorstore1 = QdrantVectorStore.from_documents(
            documents=splits1,
            embedding=self.embedder,
            location=":memory:",
            collection_name="1"
        )

        self.vectorstore2 = QdrantVectorStore.from_documents(
            documents=splits2,
            embedding=self.embedder,
            location=":memory:",
            collection_name="2"
        )
    def extract_entities(self, text, year, result_folder):

        user_prompt = \
            f""" 
        Please help me extract the entities in following piece of text into a graph using the structured output format.

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

        entities_file_path = f"{result_folder}/entities_{year}.json"
        my_file = Path(entities_file_path)
        if my_file.is_file():
            with open(entities_file_path) as f:
                entities_json = json.load(f)
            entities = Entities(**entities_json)

        else:
            entities = self.openai_client.beta.chat.completions.parse(**completion_parameters).choices[0].message.parsed
            dict = entities.dict()
            json_data = json.dumps(dict)
            with open(entities_file_path, "w") as file:
                file.write(json_data)

        return entities

    def retry_entity_comparison(self, name, filter_enabled, use_url, retry_count):
        for i in range(retry_count):
            res = compare_entities(name, self.vectorstore1, self.vectorstore2, filter=filter_enabled,
                                   use_url=use_url)
            if not res == "Agent stopped due to iteration limit or time limit.":
                return res
        return "Agent stopped due to iteration limit or time limit."

    def create_entity_report(self, entity_type, combined_entities, results_folder, filter_enabled, use_url):
        results_path = f"{results_folder}/agentic_compare_{entity_type}.txt"
        results = Path(results_path)
        if results.is_file():
            with open(results_path) as f:
                results = f.read()
        else:

            if self.vectorstore2 is None:
                self.create_vector_stores(self.text1, self.text2)

            with open(results_path, 'w') as f:
                f.write(f"Difference Summaries\n\n\n {entity_type} \n")
            with open(results_path, 'r') as f:
                contents = f.read()

            for name in combined_entities:
                type = combined_entities[name]["type"]
                if type.lower() == entity_type.lower() and "__________________" + name + "_____________________" not in contents:

                    res = self.retry_entity_comparison(name, filter_enabled, use_url, 4)

                    if not res == "Agent stopped due to iteration limit or time limit.":
                        with open(results_path, 'a') as f:
                            f.write("\n\n__________________" + name + "_____________________\n\n")
                            f.write(res)
                            f.write("\n\n")

            with open(results_path, 'r') as f:
                results = f.read()

        return results

    def compare_docs(self, docpath1, docpath2, results_folder) -> str:

        self.text1 = self.tika_parser.get_text(docpath1)
        self.text2 = self.tika_parser.get_text(docpath2)

        self.entities1 = self.extract_entities(self.text1, "1", results_folder)
        self.entities2 = self.extract_entities(self.text2, "2", results_folder)
        self.entities2.entities.extend(self.entities1.entities)

        combined_entities = {}
        for entity in self.entities2.entities:
            if entity.name in combined_entities:
                pass
            else:
                combined_entities[entity.name] = {"description": entity.description, "type": entity.type.title()}
        policy_report = self.create_entity_report("Policy", combined_entities, results_folder, filter_enabled=False, use_url=False)
        product_report = self.create_entity_report("Product", combined_entities, results_folder, filter_enabled=True, use_url=False)

        final_report_generator = FinalReportGenerator(self.config)

        policy_product_report = final_report_generator.create_policy_product_report(product_report, policy_report)
        intro_compare = final_report_generator.compare_introductions(self.text1[:1500], self.text2[:1500])

        final_report = f"###Intoruduction\n\n{intro_compare}\n\n###Detailed Comparison Table\n\n{policy_product_report}"
        with open(f"{results_folder}/agentic_compare.txt", 'w') as f:
            f.write(final_report)

        return final_report

