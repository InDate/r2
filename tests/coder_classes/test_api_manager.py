import unittest
from unittest.mock import patch
from r2.coder_classes.api_manager import ApiManager, TokensExceedsModel

class TestApiManager(unittest.TestCase):
    def setUp(self):
        self.api_manager = ApiManager()

    def test_reset(self):
        self.api_manager.reset()
        self.assertEqual(self.api_manager.get_total_prompt_tokens(), 0)
        self.assertEqual(self.api_manager.get_total_completion_tokens(), 0)
        self.assertEqual(self.api_manager.get_total_cost(), "Total running cost: $0.000")

    @patch("r2.coder_classes.api_manager.openai.ChatCompletion.create")
    def test_create_chat_completion(self, mock_create):
        mock_create.return_value = {"choices": [{"text": "Paris"}]}
        messages = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is the capital of France?"}]
        response = self.api_manager.create_chat_completion(messages, model="text-davinci-002", temperature=0.5, max_tokens=50)
        self.assertEqual(response, {"choices": [{"text": "Paris"}]})
        self.assertNotEqual(self.api_manager.get_total_cost(), "Total running cost: $0.000")

    def test_update_cost(self):
        self.api_manager.update_cost("text-davinci-002")
        self.assertNotEqual(self.api_manager.get_total_cost(), "Total running cost: $0.000")

    def test_get_approx_prompt_tokens(self):
        messages = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is the capital of France?"}]
        prompt_tokens = self.api_manager.get_approx_prompt_tokens(messages, "text-davinci-002")
        self.assertEqual(prompt_tokens, 50)

    def test_update_prompt_tokens(self):
        messages = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is the capital of France?"}]
        self.api_manager.update_prompt_tokens(messages, "text-davinci-002")
        self.assertEqual(self.api_manager.prompt_tokens, 50)

    def test_update_completion_tokens(self):
        self.api_manager.update_completion_tokens(10)
        self.assertEqual(self.api_manager.completion_tokens, 10)

    def test_set_get_total_budget(self):
        self.api_manager.set_total_budget(10)
        self.assertEqual(self.api_manager.get_total_budget(), 10)

    def test_get_total_prompt_tokens(self):
        self.assertEqual(self.api_manager.get_total_prompt_tokens(), 0)

    def test_get_total_completion_tokens(self):
        self.assertEqual(self.api_manager.get_total_completion_tokens(), 0)

    def test_get_total_cost(self):
        self.assertEqual(self.api_manager.get_total_cost(), "Total running cost: $0.000")

if __name__ == "__main__":
    unittest.main()
