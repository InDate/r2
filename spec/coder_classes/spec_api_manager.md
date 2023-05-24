- Class Name: ApiManager
- Purpose: Manage API calls to OpenAI, track tokens, and handle errors.

- Properties:
    - `total_prompt_tokens`: The total number of prompt tokens used.
    - `total_completion_tokens`: The total number of completion tokens used.
    - `total_cost`: The total cost of API calls.
    - `total_budget`: The total user-defined budget for API calls.
    - `prompt_tokens`: The number of prompt tokens for the current API call.
    - `completion_tokens`: The number of completion tokens for the current API call.

- Methods:
    - `reset()`: Resets the total tokens and cost.
    - `create_chat_completion(messages, model, temperature, max_tokens, stream)`: Creates a chat completion and updates the cost.
    - `update_cost(model)`: Updates the total cost, prompt tokens, and completion tokens.
    - `get_approx_prompt_tokens(messages, model)`: Gets the approximate number of prompt tokens for the given messages and model.
    - `update_prompt_tokens(messages, model)`: Updates the number of prompt tokens for the current API call.
    - `update_completion_tokens(completion_tokens)`: Updates the number of completion tokens for the current API call.
    - `set_total_budget(total_budget)`: Sets the total user-defined budget for API calls.
    - `get_total_prompt_tokens()`: Returns the total number of prompt tokens.
    - `get_total_completion_tokens()`: Returns the total number of completion tokens.
    - `get_total_cost()`: Returns the total cost of API calls.
    - `get_total_budget()`: Returns the total user-defined budget for API calls.

- Example Usage:
api_manager = ApiManager()
api_manager.set_total_budget(10)
messages = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is the capital of France?"}]
response = api_manager.create_chat_completion(messages, model="text-davinci-002", temperature=0.5, max_tokens=50)
print(api_manager.get_total_cost())  # Outputs: Total running cost: $0.123
