import requests

# Define the API endpoint for the Ollama service
BASE_URL = "http://localhost:11434"  # Replace with the actual host if running remotely

# Function to interact with the Ollama API
def query_ollama(model_name, prompt):
    """
    Query the Ollama service API with a given model and prompt.

    Args:
        model_name (str): The name of the model to query (e.g., 'llama').
        prompt (str): The input text prompt.

    Returns:
        dict: The response from the Ollama API.
    """
    # API endpoint for the 'api' route
    url = f"{BASE_URL}/api/{model_name}"

    # Payload to send with the request
    payload = {
        "prompt": prompt
    }

    try:
        # Send the POST request
        response = requests.post(url, json=payload)

        # Check if the response is successful
        if response.status_code == 200:
            return response.json()  # Parse and return the JSON response
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


# Example usage
if __name__ == "__main__":
    # Replace 'llama' with the name of the model you're using
    model_name = "llama"

    # Input prompt for the model
    prompt = "Write a short story about an AI helping humanity."

    # Call the function and get the response
    response = query_ollama(model_name, prompt)

    # Print the response
    if response:
        print("Response from Ollama API:")
        print(response)

