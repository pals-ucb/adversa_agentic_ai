import argparse
import json
import requests
import sys
from pathlib import Path

def create_model(api_endpoint: str, input_json_file: str):
    # Load input JSON file
    input_path = Path(input_json_file)
    if not input_path.exists():
        print(f"Error: Input file '{input_json_file}' does not exist.")
        sys.exit(1)

    with open(input_path, "r") as f:
        try:
            model_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            sys.exit(1)

    # Call API
    url = f"{api_endpoint.rstrip('/')}/aaa/sim/models"
    try:
        response = requests.post(url, json=model_data)
        response.raise_for_status()
        print("✅ Model created successfully:")
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        if e.response is not None:
            print("Response:", e.response.text)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(prog="adversa", description="Adversa CLI Tool for managing SimModels")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create-model command
    create_parser = subparsers.add_parser("create-model", help="Create a new simulation model")
    create_parser.add_argument("--input-json-file", required=True, help="Path to the input JSON model file")
    create_parser.add_argument("--api-endpoint", default = "https://xzsu0uh2di.execute-api.us-east-1.amazonaws.com/Prod", help="Base URL of the REST API")

    args = parser.parse_args()

    if args.command == "create-model":
        create_model(api_endpoint=args.api_endpoint, input_json_file=args.input_json_file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
