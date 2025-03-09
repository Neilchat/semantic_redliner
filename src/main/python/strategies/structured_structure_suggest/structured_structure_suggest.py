from openai import OpenAI

from graph_extractor.llm_graph_extractor import GraphExtractor
from strategies.base.base_strategy import BaseStrategy
from strategies.base.strategy_config import StrategyConfig
from text_extraction.tika_parser import TikaParser


class StructuredStructureSuggest(BaseStrategy):
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        self.llm = OpenAI(api_key=config.openai_api_key)
        self.tika_parser = TikaParser()

    def compare_docs(self, docpath1, docpath2, results_folder) -> str:
        text1 = self.tika_parser.get_text(docpath1)
        text2 = self.tika_parser.get_text(docpath2)

        extractor = GraphExtractor(self.config)

        graph2015 = extractor.get_or_create_graph(text1, "2015", results_folder)
        graph2023 = extractor.get_or_create_graph(text2, "2023", results_folder)

        system_prompt = \
            """
You are an advanced NLP system specialized in understanding Legal documents.
Your job is to compare two structures for legal documents in terms of their structure and suggest a better structure that combines the qualities of both.

The user will supply you with two graphs representing Apple's Terms and Conditions from 2015 and 2023. 
Please understand the structure of the graphs, and suggest a better unified structure.

The Graphs the user will supply is formed of the following schema:

***Schema***
- The Graph consist of a List of Section objects. Each section object represents an actual section in the document. All the Sections are in sequence and, combined together represent the entire document.
- Each Section has the following properties:
    - heading: String that is the exact name of the section heading as mentioned in the document.
    - parent: String denoting the heading of the parent of this section
    - subsections: List of strings denoting the headings of subsections of this section.
    - entities: A List of Entity objects representing all the entities mentioned in the section content. Each entity has the following properties:
        - type: Enum representing the type of entity. Must be one of ["geographic_location", "legal_act", "date", "product", "url", "dollar]
        - name: String denoting the name of the entity, for example the date or the dollar amount of corresponding entitiy types.

Your job is to take as input from the user two graphs representing Apple's Terms and Conditions from the year 2015 and 2023 and output a comprehensive report on a unified structure.
Format you answer in a structured way, explaining the sections, and why this is a better structure.
Remember you don't need to included **entities** in your response. Simply Headings, subsections, and descriptions of each.
            """

        user_prompt = \
            f""" 
Graph extracted from Apple Music's terms and conditions from 2015: 
{str(graph2015)}

Graph extracted from Apple Music's terms and conditions from 2023: 
{str(graph2023)}

Please provide suggestions for standardizing the Terms and Conditions to create a more consistent format.
        """
        completion_parameters = {"model": self.config.openai_model_name,
                                 "messages": [{"role": "system",
                                               "content": system_prompt},
                                              {"role": "user",
                                               "content": user_prompt}],
                                 "temperature": 0.0}

        ans = self.llm.chat.completions.create(**completion_parameters).choices[0].message.content

        with open(f"{results_folder}/structured_structure_suggest.txt",
                  'w') as f:
            f.write(ans)
        return ans