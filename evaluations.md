## Qualitative Comparisons
First iteration worked better. Qualitative example:

From Agentic
   1. **Right of Cancellation**:
   - **2015**: Customers could cancel their order within 14 days of receiving their receipt without providing a reason. Specific exceptions were noted for iTunes Gifts, which could not be refunded once redeemed.
   - **2023**: The right of cancellation remains the same, allowing cancellation within 14 days without a reason. However, the exceptions have been streamlined, with a specific mention of "Complete My Season" for subscription services, which must be canceled through iTunes Support.

From SectionWise
   - The 2023 report includes a right of cancellation within 14 days of receiving a receipt, which is a new consumer protection feature not present in the 2015 report.

Latter is incorrect

| **Contract Creation** | "These terms and conditions create a contract between you and Apple (the “Agreement”)." | Not mentioned | Establishes a formal legal relationship, emphasizing the binding nature of the terms. |
This gets mentioned in Section-wise, not in entities.
Better entity extraction is needed


Governing law insight.

Popular Near Me	Privacy and User Control	Users are informed that they can opt out of data collection by disabling Location Services or turning off “Popular Near Me.”	Implies a more generalized approach to user data and privacy, focusing on how apps are ranked and displayed.	May enhance user trust but could limit personalization that users previously experienced.

Ask to Buy comes up in section compare not in agent compare. Why? It is in family sharing just doesn't come up in diff, the 13 year age cut off does though.

## Quantitative Comparisons
Faithfulness scores-

### Agentic -

policy: faithfulness (0.8571428571428571, "The score is 0.86 because the actual output misidentifies the entities involved in the cancellation notice. It mentions 'iTunes S.à r.l. in 2015' instead of the correct 'iTunes Sarl' and erroneously includes 'Apple Distribution International Ltd.' for 2023, which contradicts the retrieval context.")

product: faithfulness (1.0, 'The score is 1.00 because there are no contradictions, indicating that the actual output is perfectly aligned with the retrieval context.')

### SectionWise -

overall: faithfulness (0.5675675675675675, "The score is 0.57 because the actual output contains multiple claims about the 2015 and 2023 reports that are not supported by the retrieval context, such as assertions regarding iTunes' terms modification, termination rights, privacy policy, and age requirements. These discrepancies highlight significant gaps between the actual output and the source material.")


### Naive -
faithfulness (1.0, 'The score is 1.00 because there are no contradictions present, indicating that the actual output completely aligns with the retrieval context.')
