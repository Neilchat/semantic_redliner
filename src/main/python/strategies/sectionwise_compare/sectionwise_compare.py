import json
from pathlib import Path

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from rouge_score import rouge_scorer
from openai import OpenAI
from graph_extractor.combined_extractor import CombinedExtractor
from strategies.base.base_strategy import BaseStrategy
from strategies.base.strategy_config import StrategyConfig
from strategies.sectionwise_compare.prompt_store import section_compare_system_prompt, section_compare_user_prompt, \
    merge_results_system_prompt
from text_extraction.tika_parser import TikaParser

class SectionWiseCompare(BaseStrategy):
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        self.llm = OpenAI(api_key=config.openai_api_key)
        self.tika_parser = TikaParser()
        self.config = config
        self.rouge_scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=False)
        self.embedder = OpenAIEmbeddings(
            deployment = config.openai_embedding_model_name,
            api_key = config.openai_api_key
        )

    def get_related_sections(self, section, vectorstore):
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        results = {}

        sections_heading = retriever.get_relevant_documents(section.heading)
        if section.content:
            sections_content = retriever.get_relevant_documents(section.content)
            for s in sections_content:
                if s.metadata["path"] in results:
                    pass
                else:
                    results[s.metadata["path"]] = s.page_content

        for s in sections_heading:
            if s.metadata["path"] in results:
                pass
            else:
                results[s.metadata["path"]] = s.page_content

        return results


    def compare_a_section(self, section1, relevant_sections, year1, year2):
        system_prompt = section_compare_system_prompt.format(year1=year1, year2=year2, text1 = section1.content)

        user_prompt = section_compare_user_prompt.format(year1=year1, year2=year2, text2 = str(relevant_sections))
        completion_parameters = {"model": self.config.openai_model_name,
                                 "messages": [{"role": "system",
                                               "content": system_prompt},
                                              {"role": "user",
                                               "content": user_prompt}],
                                 "temperature": 0.0}

        ans = self.llm.chat.completions.create(**completion_parameters)
        return ans.choices[0].message.content

    def merge_results(self, comparisons2023, comparisons2015):
        prompt = "First lets go over the changes from the 2023 report to the 2015 report. Outlining all that was mentioned in the 2023 report but was missing/changed in the 2015 one.\n"
        for key in comparisons2023:
            if not comparisons2023[key]["comparison"] == "None.":
                prompt += f"For the section {comparisons2023[key]['path']} the differences were:\n {comparisons2023[key]['comparison']} \n"
        prompt += "\n\n................\n\n Next lets go over the changes from the 2015 report to the 2023 report. Outlining all that was mentioned in the 2015 report but was missing/changed in the 2015 one.\n"
        for key in comparisons2015:
            if not comparisons2015[key]["comparison"] == "None.":
                prompt += f"For the section {comparisons2015[key]['path']} the differences were:\n {comparisons2015[key]['comparison']}"
        prompt += "\n\n................\n\n Please provide me with a summary of all the differnces stated above, focusing on their significance and impact."
        completion_parameters = {"model": "gpt-4o-mini",
                                 "messages": [{"role": "system",
                                               "content": merge_results_system_prompt},
                                              {"role": "user",
                                               "content": prompt}],
                                 "temperature": 0.0}
        ans = self.llm.chat.completions.create(**completion_parameters)
        return ans.choices[0].message.content



    def compare_docs(self, docpath1, docpath2) -> str:
        extractor = CombinedExtractor(self.config)
        contents2015, graph2015 = extractor.get_datapoints(docpath1, "2015")
        contents2023, graph2023 = extractor.get_datapoints(docpath2, "2023")

        section_2023_path = "/Users/saswata/Documents/semantic_redliner/src/main/python/data/results/section_compares2023.json"
        comparisons2023 = {}
        my_file = Path(section_2023_path)
        if my_file.is_file():
            with open(section_2023_path) as f:
                comparisons2023 = json.load(f)
        else:
            vectorstore2015 = QdrantVectorStore.from_documents(
                documents=[Document(page_content=s.content or "", metadata={"path": s.path}) for s in contents2015],
                embedding=self.embedder,
                location=":memory:",
                collection_name="2015"
            )
            for sec2023 in contents2023:
                relevant_sections = self.get_related_sections(sec2023, vectorstore2015)
                comparison = self.compare_a_section(sec2023, relevant_sections, "2023", "2015")
                compares={"comparison": comparison,
                         "sections": list(relevant_sections.keys()),
                         "path": sec2023.path
                         }
                comparisons2023[sec2023.path] = compares
                print(compares)

                with open(section_2023_path, 'w') as f:
                    json.dump(comparisons2023, f, indent=2)

        section_2015_path = f"/Users/saswata/Documents/semantic_redliner/src/main/python/data/results/section_compares2015.json"
        comparisons2015 = {}
        my_file = Path(section_2015_path)
        if my_file.is_file():
            with open(section_2015_path) as f:
                comparisons2015 = json.load(f)
        else:
            for sec2015 in contents2015:
                vectorstore2023 = QdrantVectorStore.from_documents(
                    documents=[Document(page_content=s.content or "", metadata={"path": s.path}) for s in contents2023],
                    embedding=self.embedder,
                    location=":memory:",
                    collection_name="2023"
                )
                relevant_sections = self.get_related_sections(sec2015, vectorstore2023)
                comparison = self.compare_a_section(sec2015, relevant_sections, "2015", "2023")
                compares = \
                    {"comparison": comparison,
                     "sections": list(relevant_sections.keys()),
                     "path": sec2015.path
                     }
                comparisons2015[sec2015.path] = compares
                print(compares)

                with open(section_2015_path, 'w') as f:
                    json.dump(comparisons2015, f, indent=2)

        ans = self.merge_results(comparisons2023, comparisons2015)
        with open("/Users/saswata/Documents/semantic_redliner/src/main/python/data/results/sectionWise_compare.txt",
                  'w') as f:
            f.write(ans)

        print(ans)

