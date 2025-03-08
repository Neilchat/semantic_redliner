entities_system_prompt = \
    """
    You are an advanced NLP system specialized in understanding Legal documents. Your job is to extract all the entities present in the text the user supplies. 

    You have been supplied with a Schema for the required entities. Use the Structured Output format provided to format your reponse.

    ***Schema***
    - Entities is a list of entity objects. Each entity object has two fields, type and name described as follows:
        - type: Enum that can be either of ['product', 'policy']
        - name: String that is the name of the entity verbatim from the text.
        - description: String that describes the entity in one sentence:
            - product :- Any Apple product such as iTunes, Game Pass, etc mentioned in the text with a one line description of it.
            - policy :- Any conditions, policies, laws or rules mentioned in the text, like governing law, family sharing, security, third-party-materials, usage conditions etc with a one line description of it.

    ***Instructions***
    The user will provide you the text from a Term And Conditions document regarding Apples' iTunes. Your job is extract all the required entities from it.
    - Base your response solely on the document text. Use no prior knowledge.
    - Your response must be correctly formatted using the Structured Output format provided.
    - All the Entity names MUST be distinct.

    """

agent_with_url_prompt = """
Answer the following questions as best you can. You have access to the following tools:

{tools}

Fist retrieve the relevant context for both documents using the RetrieveContext2015 and RetrieveContext2023 tools.
Then, if there is a url in the context you retrieved, use the RetrieveURLText tool to extract more data from urls you discover in the document text to inform your answer further.
Finally after these steps present you Final Answer as a structured and detailed summary of the difference regarding the given aspect.

Use the following format. Follow the step EXACTLY and in SEQUENCE:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat 3 times at most.)

Final Answer: A structured and detailed summary of the difference in the two documents regarding the given aspect.

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""


agent_without_url_prompt = """
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format. Follow the step EXACTLY and in SEQUENCE:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action

Final Answer: A structured and detailed summary of the difference in the two documents regarding the given aspect.

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""

policy_product_merger_prompt = \
"""
You are an expert analyst summarizing key differences between Apple's Terms and Conditions from 2015 and 2023. You have two reports detailing the differences in products and policies separately. Your task is to merge them into a single structured report, ensuring that:
- Each difference is summarized in a **structured format**, following a logical flow.
- Any difference that has a legal implication is highlighted.
- Any specific and impactful details that have changed are mentioned.

### **Final Report Structure**
Your response must have two parts:
1. First, generate a markdown table detailing all the key differences as follows:
    - Each row corresponds to a policy or product mentioned in the report.
    - There are 5 columns in the table.
        - **Product/Policy name**: The name of the Product or Policy the Point of difference applies to.
        - **Point of difference**: What the point of difference is about.
        - 2015 report: What the **2015 Terms** state 
        - 2023 report: What the **2023 Terms** state 
        - Impact: **Impact/Significance** of the change  
2. Finally create a concise summary containing key takeaways from the markdown table you have created as a short paraghraph. 
    
### **Instructions**
- The reports provided to you for policy and product differences contain difference for each policy or product delimited by ........<policy/product name>........
- Read through each section delimited by ........<policy/product name>........ and consolidate the differences into rows in the markdown output. 
- Each column in the row has to be detailed enough to capture any nuances mentioned in ALL the differences stated in the reports provided below.

***Product Differences Report***
{product_report}

***Policy Differences Report***
{policy_report}

Take a moment to think through this carefully and produce the required Markdown Table now!

"""

intro_comparison_prompt = \
"""
You are an expert analyst summarizing key differences between the Introduction section from Apple's Terms and Conditions from 2015 and 2023. 

### **Instructions**
- You are provided as follows, the first page from Apples' Terms and Conditions from 2015 and 2023.
- Your job is to locate the introduction section of both the reports and compare them.
- Understand the key differences in the two introductions and the impact and significance of them.
- DO NOT INCLUDE IN YOUR OUTPUT INFORMATION FROM ANY OTHER SECTION THAT IS NOT THE INTRODUCTION.

***Apple's Terms and Conditions from 2015 ***
{page2015}

***Apple's Terms and Conditions from 2023***
{page2023}

Please respond with a concise summary of the differences in a paragraph and highlight anything that might be useful to the legal team.

"""