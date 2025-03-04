from abc import ABC, abstractmethod


class StrategyConfig:
    def __init__(self,
                 openai_api_key: str,
                 openai_url: str,
                 openai_api_version: str,
                 openai_model_name: str,
                 openai_embedding_model_name: str
                 ):
        self.openai_api_key = openai_api_key
        self.openai_url = openai_url
        self.openai_api_version = openai_api_version
        self.openai_model_name = openai_model_name
        self.openai_embedding_model_name = openai_embedding_model_name
