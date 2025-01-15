from openai import OpenAI
from .models import dataRecivedModel
import json

# OpenAI API Initialization
# client = OpenAI(api_key="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")
def analyze_heart_rate(data_to_send):
    client = OpenAI(api_key="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")



    # Prepare the prompt for OpenAI
    prompt = (
        "You are a health monitoring assistant. Analyze the following data "
        "to detect potential health issues and provide recommendations. "
        "Format the output as JSON with 'illnesses' and 'recommendations'. "
        f"Here is the data: {json.dumps(data_to_send)}"
    )
    # Send request to OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": "You are a medical assistant that analyzes health data to identify illnesses and provide recommendations, make understanable for every people who has no medical degree. Return results in JSON format."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "health_analysis_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "illnesses": {
                            "description": "A list of potential illnesses detected based on the input data.",
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "recommendations": {
                            "description": "Recommendations for managing or addressing the detected illnesses.",
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        }
                    },
                    "required": ["illnesses", "recommendations"],
                    "additionalProperties": False
                }
            }
        }
    )

    # Extract and print the response
    response_content = response.choices[0].message.content  # Accessing the content attribute
    response_json = json.loads(response_content)  # Parse the JSON content

    return json.dumps(response_json, indent=4)
