
import json
from ...utils import clean_code_snippet
from llmx import TextGenerator, TextGenerationConfig, TextGenerationResponse

from lida.datamodel import Goal

'''
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    Reduced the number of evaluation dimensions
    Modified system_prompt so it assumes we have a valid dataset along with our Vega-Lite chart specification
    Modified message content in the generate function for Vega-Lite compatibility
'''

system_prompt = """
You are a helpful assistant highly skilled in evaluating the quality of a given visualization code by providing a score from 1 (bad) - 10 (good) while providing clear rationale. YOU MUST CONSIDER VISUALIZATION BEST PRACTICES for each evaluation. Specifically, you can carefully evaluate the code across the following dimensions
- bugs (bugs):  are there bugs, logic errors, syntax error or typos? Are there any reasons why the code may fail to compile? How should it be fixed? If ANY bug exists, the bug score MUST be less than 5.
- Visualization type (type): CONSIDERING BEST PRACTICES, is the visualization type appropriate for the data and intent? Is there a visualization type that would be more effective in conveying insights? If a different visualization type is more appropriate, the score MUST be less than 5.
- Data encoding (encoding): Is the data encoded appropriately for the visualization type?
- aesthetics (aesthetics): Are the aesthetics of the visualization appropriate for the visualization type and the data?

You must provide a score for each of the above dimensions.  Assume that we have a valid dataframe with data used for the analysed visualization.

Your OUTPUT MUST BE A VALID JSON LIST OF OBJECTS in the format:

```[
{ "dimension":  "bugs",  "score": x , "rationale": " .."}, { "dimension":  "type",  "score": x, "rationale": " .."}, { "dimension":  "encoding",  "score": x, "rationale": " .."}, { "dimension":  "aesthetics",  "score": x, "rationale": " .."}
]
```
"""


class VizEvaluator(object):
    """Generate visualizations Explanations given some code"""

    def __init__(
        self,
    ) -> None:
        pass

    def generate(self, code: str, goal: Goal,
                 textgen_config: TextGenerationConfig, text_gen: TextGenerator, library='altair'):
        """Generate a visualization explanation given some code"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant",
             "content": f"Generate an evaluation given the goal and code below in Vega Lite. The visualization code is \n\n {code} \n\n. Now, evaluate the code based on the 4 dimensions above. \n. THE SCORE YOU ASSIGN MUST BE MEANINGFUL AND BACKED BY CLEAR RATIONALE. A SCORE OF 1 IS POOR AND A SCORE OF 10 IS VERY GOOD. The structured evaluation is below ."},
        ]

        # print(messages)
        completions: TextGenerationResponse = text_gen.generate(
            messages=messages, config=textgen_config)

        completions = [clean_code_snippet(x['content']) for x in completions.text]
        evaluations = []
        for completion in completions:
            try:
                evaluation = json.loads(completion)
                evaluations.append(evaluation)
            except Exception as json_error:
                print("Error parsing evaluation data", completion, str(json_error))
        return evaluations
