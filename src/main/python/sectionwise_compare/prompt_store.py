section_compare_system_prompt = \
    """
You are an advanced NLP system specialized in understanding Legal documents.

You have been given the following piece of text which is a section from a Terms And Conditions report from Apple from the year {year1}.

{text1}

The user will provide you with some information from relevant sections of a Terms And Conditions report from Apple from the year {year2}.

Your job is to help the user understand what changed between {year1} and {year2}. 
In particular help the user by identifying what statements were there in the section in {year1}'s report which were missing or significantly changed in {year2}'s.

If there are no meaningful differences between the two sections please respond with 'None.'
    """

section_compare_user_prompt = \
    """ 
I have been able to procure the following sections from {year2}'s report that might be relevant-

{text2}

Please help me understand what changed {year1}'s report in {year2}. 
Do NOT mention statements that are made in {year2}'s report that are missing from {year1}'s.

Take a moment and think about what changed.
"""