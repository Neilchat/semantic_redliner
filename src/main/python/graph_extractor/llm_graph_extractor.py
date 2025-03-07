import json
from enum import Enum
from pathlib import Path
from typing import List

from openai import OpenAI
from pydantic import BaseModel

from strategies.base.strategy_config import StrategyConfig


class EdgeType(str, Enum):
    SUBHEADING = "subsection"
    MENTIONS = "mentions"

class EntityType(str, Enum):
    GEOGRAPHIC_LOCATION = "geographic_location"
    LEGAL_ACT = "legal_act"
    DATE = "date"
    PRODUCT = "product"
    URL = "url"
    DOLLAR = "dollar"


class Edge(BaseModel):
    type: EdgeType
    name: str

class Entity(BaseModel):
    type: EntityType
    name: str

class Section(BaseModel):
    heading: str
    parent: str
    subsections: List[str]
    entities: List[Entity]

class Graph(BaseModel):
    sections: List[Section]


class GraphExtractor:
    def __init__(self, config: StrategyConfig):
        self.llm = OpenAI(api_key=config.openai_api_key)
        self.config = config

    def get_or_create_graph(self, text, year):
        system_prompt = \
"""
You are an advanced NLP system specialized in understanding Legal documents. Your job is to decompose the document the User supplies into a Graph. 

You have been supplied with a Schema for the required decomposition. Use the Structured Output format provided to format your reponse.

***Schema***
- The Graph consist of a List of Section objects. Each section object represents an actual section in the document the user provides. All the Sections combined together represent the entire document.
- Each Section has the following properties:
    - heading: String that is the exact name of the section heading as mentioned in the document.
    - parent: String denoting the heading of the parent of this section
    - subsections: List of strings denoting the headings of subsections of this section.
    - entities: A List of Entity objects representing all the entities mentioned in the section content. Each entity has the following properties:
        - type: Enum representing the type of entity. Must be one of ["geographic_location", "legal_act", "date", "product", "url", "dollar]
        - name: String denoting the name of the entity, for example the date or the dollar amount of corresponding entitiy types.

***Instructions***
The user will provide you the text from a Term And Conditions document regarding Apples' iTunes. Your job is to decompose the ducment text into a Graph following the Schema provided.
- Base your response solely on the document text. Use no prior knowledge.
- Your response must be correctly formatted using the Structured Output format provided.
- All the Sections headings MUST be distinct.
- The union of all the Section headings MUST make up all the sections in the document. 
- The Section objects in your report must be in the same order as they appear in the document text.

***Steps to help you***
- Read through each section of the document text.
- Make a note of each heading of each section, its parent section and the subsections it has.
- Extract all relevant entities from the section.
- Add the Section entry to your response in the order that they appear in the document.
"""

        user_prompt = \
f""" 
Please help me decompose the following piece of text into a graph using the structured output format.

***Document Text***
{text}

"""
        completion_parameters = {"model": self.config.openai_model_name,
                                 "messages": [{"role": "system",
                                               "content": system_prompt},
                                              {"role": "user",
                                               "content": user_prompt}],
                                 "temperature": 0.0,
                                 "response_format": Graph}

        graph_path = f"/Users/saswata/Documents/semantic_redliner/src/main/python/data/graph_{year}.json"
        my_file = Path(graph_path)
        if my_file.is_file():
            with open(graph_path) as f:
                graph_json = json.load(f)
            graph = Graph(**graph_json)

        else:
            graph = self.llm.beta.chat.completions.parse(**completion_parameters).choices[0].message.parsed

            dict = graph.dict()
            json_data = json.dumps(dict)
            with open(graph_path, "w") as file:
                file.write(json_data)

        return graph
