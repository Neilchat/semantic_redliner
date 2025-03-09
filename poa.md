# Semantic Redliner

### Observations
- The texts are pretty small
- 8193 words, 15105 words
- So they are also very different to each other - traditional redlining will likely fail.

## Initial Plan
- First lets just pass it all into gpt4o and see what it says. That is baseline.
- Next lets do entity extraction and semantic chunking to see what the layouts are and compare section wise.
- Then we go for multihop QA tool can reach into web to get sources to expand knowledge.

### Observations
- The layouts are very different.
- 2015 breaks down product wise, 2023 combines them
- Direct comparison fails via title matching. Aggregation of sections is needed.

## Sectionwise Compare
- New plan - take section of 2023, find matching sections from 2015 and form diff.
  - Retrieve via semantic + metadata
    - metadata compares section names (rouge score) and entities
    - semantic similarity on top
  - Format prompt accordingly to generate what is mentioned in section in 2023 that is different in 2013
- Do opposite
- Aggregate everything

### Observations
Why this isn't working well?
- Things are in various places in the documents (same section in 2015 is under both itunes and not, leading to incomplete reporting)
- We are generating a lot of noise
- Final summary report is bland
- Rather do it entity wise

## Entitywise Compare
- New plan - extract entities from both documents, compare each individually, build up report
  - Entities - Product, Policy
  - For each product create Agent that compares them
    - Get relevant chunks (similarity + metadata for product)
    - Click through url?
    - Form summary
  - Create final product report
  - Repeat for Policy
  - Create final report

## Evals
- qualitative
- deepeval faithfulness
- rubric with geval expected score WIP


## Further steps
- Fix up the sections generator
  - This is one reason the SectionWiseCompare is suffering
  - New plan:
    - LLM to extract section titles in sequence as a tree
    - Iterate over words and regex match to fill out contents instead of LLM sherpa
- Use section contents with link to branch in section tree as chunking (AgenticCompare)
  - The issue right now:
    - Say I get a relevant chunk on Privacy, I might not know what product it is for
    - Chunks are not semantic boxes - worse retrieval
- Fix URL text generation
  - Needs to expand to take as input the document year, return that with the response
  - It also needs to check when the page was last updated and that it corresponds to the year asked for
  - It also needs to extract all the text well, currently just p which seems to work for most of these apple links
  - If text is too large a semantic similarity search over it is required
- Fix rubric evals
  - The eval prompt is not reading the markdown table well
  - Extract answer from markdown as paragraph and pass to eval
