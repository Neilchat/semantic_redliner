#Semantic Redliner

###Observations
- The texts are pretty small
- 8193 words, 15105 words
- So they are also very different to each other - traditional redlining will likely fail.

##Initial Plan
- First lets just pass it all into gpt4o and see what it says. That is baseline.
- Next lets do entity extraction and semantic chunking to see what the layouts are and compare section wise.
- Then we go for multihop QA tool can reach into web to get sources to expand knowledge.

###Observations
- The layouts are very different.
- 2015 breaks down product wise, 2023 combines them
- Direct comparison fails via title matching. Aggregation of sections is needed.

##Sectionwise Compare
- New plan - take section of 2023, find matching sections from 2015 and form diff.
  - Retrieve via semantic + metadata
    - metadata compares section names (rouge score) and entities
    - semantic similarity on top
  - Format prompt accordingly to generate what is mentioned in section in 2023 that is different in 2013
- Do opposite
- Aggregate everything

###Observations
Why this isn't working well?
- Things are in various places in the documents (same section in 2015 is under both itunes and not, leading to incomplete reporting)
- We are generating a lot of noise
- Final summary report is bland
- Rather do it entity wise

##Entitywise Compare
- New plan - extract entities from both documents, compare each individually, build up report
  - Entities - Product, Policy
  - For each product create Agent that compares them
    - Get relevant chunks (similarity + metadata for product)
    - Click through url?
    - Form summary
  - Create final product report
  - Repeat for Policy
  - Create final report

##Qualitative Comparisons
First iteration worked better. Qualitative example:
From Agentic
- 1. **Right of Cancellation**:
   - **2015**: Customers could cancel their order within 14 days of receiving their receipt without providing a reason. Specific exceptions were noted for iTunes Gifts, which could not be refunded once redeemed.
   - **2023**: The right of cancellation remains the same, allowing cancellation within 14 days without a reason. However, the exceptions have been streamlined, with a specific mention of "Complete My Season" for subscription services, which must be canceled through iTunes Support.
From SectionWise
- The 2023 report includes a right of cancellation within 14 days of receiving a receipt, which is a new consumer protection feature not present in the 2015 report.
Later is incorrect