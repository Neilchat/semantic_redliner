#Semantic Document Comparison

##Project structure

Strategies module host all the strategies for compare and suggest
- Naive Compare
- SectionWise Compare
- Agentic Compare (Entity wise)
- Naive Structure Suggestion

Evals module hosts logic for all evals.

Graph extractor contains all document parsing and structure extracting abilities

Text Extraction contains Tika module to extract doc text

Scripts contain all runnables to perform comparison/suggestion

##How to run

Run scripts/run_end_to_end.py to run any strategy end to end with result generation and eval.
Specify strategy key, results folder path, doc paths.

##Results

data module contain the results for all strategies