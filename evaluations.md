# Compare

## Qualitative Comparisons

- Naive compare is not at all detailed, more of an overview and doesn't give much insight (prompt changes might make it much better though).

- SectionWise is better and gives some details but messes up facts sometimes. The section detailing is poor.

- Agentic compare gives a much more verbose and impactful answer. The section detailing that it has is great.

- Naive with o1-mini shows promise, it includes some details but isn't as comprehensive. Impact analysis is good.

#### Some comparisons

From Agentic:

- **2015**: Customers could cancel their order within 14 days of receiving their receipt without providing a reason.
- **2023**: Cancellation rights remain largely the same, but specifies that subscription services can only be canceled after the initial subscription, not at each automatic renewal.
- **Impact**: Clarification regarding subscription services provides consumers with a better understanding of their rights concerning ongoing payments.
  
From SectionWise:

- The 2023 report includes a right of cancellation within 14 days of receiving a receipt, which is a new consumer protection feature not present in the 2015 report.

.......

Agentic also comes up with good impact insights:
- Governing law insight - Affects users outside the U.S. as they are now subject to California law, potentially increasing legal costs for non-U.S. users
- Privacy insight - May enhance user trust but could limit personalization that users previously experienced.

........


Where agentic suffers? 

- Entity detection is not perfect:
  - | **Contract Creation** | "These terms and conditions create a contract between you and Apple (the “Agreement”)." | Not mentioned | Establishes a formal legal relationship, emphasizing the binding nature of the terms. |
    This gets mentioned in Section-wise, not in entities.
.........


## Quantitative Comparisons


### Agentic -

policy: faithfulness (0.8571428571428571, "The score is 0.86 because the actual output misidentifies the entities involved in the cancellation notice. It mentions 'iTunes S.à r.l. in 2015' instead of the correct 'iTunes Sarl' and erroneously includes 'Apple Distribution International Ltd.' for 2023, which contradicts the retrieval context.")

product: faithfulness (1.0, 'The score is 1.00 because there are no contradictions, indicating that the actual output is perfectly aligned with the retrieval context.')

overall: Faithfulness Score: (1.0, 'The score is 1.00 because there are no contradictions present, indicating complete alignment between the actual output and the retrieval context. Great job on maintaining consistency!')

Time taken: 9984.11525201797485 seconds

### SectionWise -

Faithfulness Score: (0.6041666666666666, "The score is 0.60 because there are multiple inconsistencies between the actual output and the retrieval context, including the erroneous claim about a 2023 report, missing definitions, and unsupported assertions regarding the 2015 report's content on various topics such as payment methods and service availability.")

Time taken: 993.9237010478973 seconds

### Naive -

4o-mini

faithfulness (1.0, 'The score is 1.00 because there are no contradictions present, indicating that the actual output completely aligns with the retrieval context.')

Time taken: 16.149780988693237 seconds

o1-mini

Time taken: 24.97355318069458 seconds


##Conclusion

Agentic workflow seems like the better suited as it breaks the problem down into bits that can be compared properly.
It has several missing pieces that can be improved.

# Suggest Structure

## Qualitative Comparisons

- Naive
  - Quite verbose and detailed in its suggestion. Breaks it down into important sections and doesn't skip any section.
  - FAMILY SHARING not a separate section
  - Focuses more on policy sections
  - Time taken: 16.12815499305725 seconds
- Structured
  - As detailed as previous but skips some sections (Governing Law for example).
  - But the breakdown is nicer in terms of sections and subsections.
  - FAMILY SHARING a separate section
  - Includes some product specific sections
  - Time taken: 71.2936282157898 seconds

## Conclusion

Naive will work pretty well with prompt engineering tailored to what we want, and is much faster.

