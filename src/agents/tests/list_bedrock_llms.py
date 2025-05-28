import boto3

def list_accessible_bedrock_models(region="us-east-1"):
    client = boto3.client("bedrock", region_name=region)

    try:
        response = client.list_foundation_models()
        models = response.get("modelSummaries", [])
        print(f"\n {len(models)} models found in region {region}:\n")

        for model in models:
            print(f"- ID: {model['modelId']}")
            print(f"  Provider: {model['providerName']}")
            print(f"  Output modalities: {model.get('outputModalities', [])}")
            print(f"  Customizable: {model.get('customizationsSupported', [])}")
            print(f"  Inference types: {model.get('inferenceTypesSupported', [])}")
            print()

        return [model["modelId"] for model in models]

    except Exception as e:
        print(f"Error fetching models: {e}")
        return []

def check_model_availability(target_model_id, region="us-east-1"):
    available_models = list_accessible_bedrock_models(region)
    if target_model_id in available_models:
        print(f"\nModel '{target_model_id}' is available!")
    else:
        print(f"\nModel '{target_model_id}' is NOT available. You may need to request access in the AWS Bedrock console.")

if __name__ == "__main__":
    # Customize this ID based on your desired LLM
    target_model = "anthropic.claude-3-sonnet-20240229-v1:0"
    check_model_availability(target_model)
