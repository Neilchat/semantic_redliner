# Semantic Document Comparison

## Project structure

### Strategies module host all the strategies for compare and suggest

### Compare

- Naive Compare
  - Give both docs to model and optimize prompt
- SectionWise Compare
  - Extract Graph structure from both docs (Sections - subsection, entities)
  - Extract content for each section (LLM sherpa)
  - For document A sections search Document B for related sections (semantic+metadata) and compare
  - For document B sections search Document A for related sections (semantic+metadata) and compare
  - Combine both comparisons into unified report with LLM call
- Agentic Compare
  - Extract all entities from each document (Policy, Product)
  - For each entity search both docs for related chunks (semantic + metadata) and compare
  - Entity comparison is agentic and performs multihop retrieval and URL text detection
  - Build overall report off of differences in all entities

### Suggest

- Naive Structure Suggestion
  - Feed both docs to LLM and get structure suggestion
- Structured Structure Suggestion
  - Extract graph as before for both documents
  - Feed said graph into LLM to get suggestion

###Evals module hosts logic for all evals.
- Faithfulness (DeepEval)
- Rubric Based (Expected Score calculation based on Logits)

###Graph extractor 
Contains all document text structure extracting abilities

###Text Extraction 
Contains Tika module to extract doc text

###Scripts 
Contain all runnables to perform comparison/suggestion and evaluation

###Markdowns:
- `evaluations.md` contain all details of the evals
- `poa.md` contains my chain of thought while executing this build

## How to run

To run SectionWiseCompare you need to run a llmsherpa server locally. Run via docker:

`docker pull ghcr.io/nlmatics/nlm-ingestor:latest`

`docker run -p 5010:5001 ghcr.io/nlmatics/nlm-ingestor:latest`

Run `scripts/run_end_to_end.py` to run any strategy end to end with result generation and eval.
Specify strategy key, results folder path, doc paths in `scripts/run_end_to_end.py` and openai API_KEY in `config.py`

## Results

`data` folder contain the results for all strategies