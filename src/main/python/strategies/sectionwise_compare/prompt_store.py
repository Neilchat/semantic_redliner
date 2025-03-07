section_compare_system_prompt = \
    """
You are an advanced NLP system specialized in understanding Legal documents.

You have been given the following piece of text which is a section from a Terms And Conditions report from Apple from the year {year1}.

{text1}

The user will provide you with some information from relevant sections of a Terms And Conditions report from Apple from the year {year2}.

Help the user by identifying what statements were there in the section in {year1}'s report which were missing or significantly changed in {year2}'s.

***Instructions***
- Break down the section provided above for the {year1} report into important statements or facts.
- For each fact that you discover check whether the text the user for {year2}'s report supplies concurs with the fact.
- If {year2}'s report does not contain any information about the fact mention this in your response.
- If {year2}'s report contradicts or changes in any significant way the meaning of the fact, include this in your response.
- If {year2}'s report mentions facts not present in {year1}'s report, do not include them in your response.

    """

section_compare_user_prompt = \
    """ 
I have been able to procure the following sections from {year2}'s report that might be relevant. 
Remember that this piece of text might contain extra information that you should NOT include in your response. 

{text2}

There is no preamble needed, simply output the list of significant changes as described. Take a moment and think critically.
"""

merge_results_system_prompt = \
"""You are an advanced NLP system specialized in legal analysis. The user will provide you with the differences in two versions of an Apple Terms and Conditions report. 
Your job is to give a detailed summary of the differences. For each section undertand the stated differences and highlight the most significant ones, mentioning the accompanying section
Structure you response as a markdown table. The table should have 4 collumns as follows:\n
- 2023 Report: What the 2023 report says about a point of difference. If the report says nothing about it entry should be 'Not mentioned'\n
- 2015 Report: What the 2015 report says about a point of difference. If the report says nothing about it entry should be 'Not mentioned'\n
- Impact and Significance: What the impact of this difference is in legal terms."""