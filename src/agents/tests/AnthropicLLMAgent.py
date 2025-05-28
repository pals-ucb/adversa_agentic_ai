# llm_agent.py
import boto3

class AnthropicLLMAgent:
    def __init__(self, model_id="anthropic.claude-3-sonnet-20240229-v1:0", region="us-east-1"):
        self.client = boto3.client("bedrock-runtime", region_name=region)
        self.model_id = model_id

    def prompt_llm(self, prompt: str) -> str:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512
        }

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )
        result = json.loads(response["body"].read())
        return result["content"][0]["text"]
