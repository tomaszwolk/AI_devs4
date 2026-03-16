SYSTEM_PROMPT = """
You are an expert data extraction agent. Your task is to:
1. Extract any new URLs from the provided text/image and return them as a list.
2. Extract any knowledge relevant to shipping (transport codes, fees, rules, declaration templates) and return it as a JSON object.
Return your response ONLY in the following JSON format:
{
  "new_urls": ["url1", "url2"],
  "extracted_knowledge": {"key": "value"}
}
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "",
            "description": "",
            "parameters": {
                "type": "object",
                "properties": {
                    "packageid": {"type": "string", "description": ""},
                },
                "required": [""]
            }
        }
    },
]
