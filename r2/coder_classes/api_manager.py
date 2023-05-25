from __future__ import annotations
import time

import openai
from openai.error import RateLimitError, APIConnectionError, APIError, Timeout

from r2.config import Config
from r2.coder_classes.api_models_info import MODELS
import tiktoken


def extract_content(messages):
    content = ''
    for message in messages:
        if 'content' in message:
            content += message['content'] + ' '
    return content.strip()


class ApiManager:
    def __init__(self, total_cost=float):
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = total_cost
        self.total_budget = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0

    def reset(self):
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0
        self.total_budget = 0.0

    def create_chat_completion(
        self,
        messages: list,  # type: ignore
        model: str | None = None,
        temperature: float = 0,
        max_tokens: int | None = None,
        stream: bool | True = True,
    ) -> str:
        """
        Create a chat completion and update the cost.
        Args:
        messages (list): The list of messages to send to the API.
        model (str): The model to use for the API call.
        temperature (float): The temperature to use for the API call.
        max_tokens (int): The maximum number of tokens for the API call.
        stream (boolean): stream from API. 
        Returns:
        str: The AI's response.
        """
        cfg = Config()

        if temperature is None:
            temperature = cfg.temperature

        self.update_prompt_tokens(messages, model)

        # TODO: Check token size against model. Will need to break up message  if too big.
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=cfg.openai_api_key,
                stream=stream
            )
            return response
        except RateLimitError:
            retry_after = 1
            time.sleep(retry_after)
        except APIConnectionError:
            retry_after = 1
            time.sleep(retry_after)
        except (APIError, Timeout):
            retry_after = 5
            time.sleep(retry_after)
        finally:
            self.update_cost(model)

    def update_cost(self, model):
        """
        Update the total cost, prompt tokens, and completion tokens.

        Args:
        model (str): The model used for the API call.
        """
        self.total_prompt_tokens += self.prompt_tokens
        self.total_completion_tokens += self.completion_tokens

        self.prompt_tokens = 0
        self.completion_tokens = 0

        self.total_cost += (
            self.total_prompt_tokens * MODELS[model]["prompt"]
            + self.total_completion_tokens * MODELS[model]["completion"]
        ) / 1000

    def get_approx_prompt_tokens(self, messages, model):
        prompt = extract_content(messages)
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(prompt))

    def update_prompt_tokens(self, messages, model):
        prompt_tokens = self.get_approx_prompt_tokens(messages, model)
        max_tokens = MODELS[model]["max_tokens"]

        if max_tokens < prompt_tokens:
            raise TokensExceedsModel(
                f'Model: {model}, Tokens(Sent/Max) {prompt_tokens}/{MODELS[model]["max_tokens"]}')
        else:
            self.prompt_tokens = prompt_tokens

    def update_completion_tokens(self, completion_tokens):
        self.completion_tokens += completion_tokens

    def set_total_budget(self, total_budget):
        """
        Sets the total user-defined budget for API calls.

        Args:
        total_budget (float): The total budget for API calls.
        """
        self.total_budget = total_budget

    def get_total_prompt_tokens(self):
        """
        Get the total number of prompt tokens.

        Returns:
        int: The total number of prompt tokens.
        """
        return self.total_prompt_tokens

    def get_total_completion_tokens(self):
        """
        Get the total number of completion tokens.

        Returns:
        int: The total number of completion tokens.
        """
        return self.total_completion_tokens

    def get_total_cost(self):
        """
        Get the total cost of API calls.

        Returns:
        float: The total cost of API calls.
        """
        return (f"Total running cost: ${self.total_cost:.3f}")

    def get_total_budget(self):
        """
        Get the total user-defined budget for API calls.

        Returns:
        float: The total budget for API calls.
        """
        return self.total_budget


class TokensExceedsModel(Exception):
    pass
