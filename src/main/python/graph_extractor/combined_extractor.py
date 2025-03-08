from typing import Optional, List

from openai import OpenAI
from pydantic import BaseModel

from graph_extractor.llm_graph_extractor import GraphExtractor, Entity
from graph_extractor.llmsherpa_extractor import get_structure
from strategies.base.strategy_config import StrategyConfig
from text_extraction.tika_parser import TikaParser


class SectionContents(BaseModel):
    heading: str
    path: str
    parent: str
    content: Optional[str] = None
    entities: List[Entity]

class CombinedExtractor:
    def __init__(self, config: StrategyConfig):
        self.llm = OpenAI(api_key=config.openai_api_key)
        self.config = config

    def get_datapoints(self, docpath, year, results_folder):
        ge = GraphExtractor(self.config)
        tika_parser = TikaParser()

        text = tika_parser.get_text(docpath)

        graph = ge.get_or_create_graph(text, year, results_folder)

        sections_structure = [SectionContents(heading= s.heading, path=s.parent + " ._. " + s.heading, parent=s.parent, entities=s.entities) for s in graph.sections if
                        len(s.subsections) == 0]


        content_structure = get_structure(docpath.replace("docx", "pdf"))

        for sec in sections_structure:
            for section in content_structure.sections():
                if section.title.lower() == sec.heading.lower():
                    sec.content = section.to_text(include_children=True)

        return sections_structure, graph