import re
from abc import ABC
from typing import Dict, Tuple

import boto3
from agents.base_agent.constants import LLM
from agents.base_agent.models import LangfuseTrace
from colorama import Fore, Style
from jinja2 import Environment, FileSystemLoader
from langchain_aws import BedrockLLM, ChatBedrock
from langchain_openai import ChatOpenAI, OpenAI
from langfuse import Langfuse


class BaseAgent(ABC):
    model: LLM = LLM.GPT4
    temperature: int = 0.5
    template: str = ''
    search_params: list = []
    many_search_params: bool = False
    list_flat: bool = False
    bool_param: bool = False

    _monitoring: LangfuseTrace

    llm = None
    verbose: bool = True

    _env = Environment(loader=FileSystemLoader('agents/prompts'))
    _env.filters['s'] = lambda input: input.replace(
        '{', '{{').replace('}', '}}')

    def __init__(self, _monitoring: LangfuseTrace):
        self._monitoring = _monitoring
        self._generate_llm()

    def _generate_llm(self) -> None:
        """
        The function `generate_llm` initializes a language model based on the specified model name and
        temperature.
        """
        if self.model in LLM.OPENAI:
            self.llm = OpenAI(model_name=self.model,
                              temperature=self.temperature)
        elif self.model in LLM.CHAT_OPENAI:
            self.llm = ChatOpenAI(model_name=self.model,
                                  temperature=self.temperature)
        elif self.model in LLM.BEDROCK:
            self.llm = BedrockLLM(
                model_id=self.model,
                client=self.client_aws(),
                model_kwargs={"temperature": self.temperature})
        elif self.model in LLM.BEDROCK_CHAT:
            self.llm = ChatBedrock(model_id=self.model,
                                   client=self.client_aws(),
                                   model_kwargs={"temperature": self.temperature})

    def client_aws(self):
        return boto3.client('bedrock-runtime', 'us-east-1')

    def run(self, context: Dict = {}) -> Tuple:
        reply = self.reply(context)
        if self.search_params and self.many_search_params:
            return self.normalize_reply_many(reply, self.search_params)
        elif self.search_params and not self.many_search_params:
            return self.normalize_reply(reply, self.search_params)
        elif self.list_flat:
            return self.normalize_list(reply)
        elif self.bool_param:
            return self.normalize_bool(reply)
        return reply

    def normalize_bool(self, reply: str) -> bool:
        return 'true' in reply.lower()

    def normalize_list(self, reply: str) -> list:
        pattern_string = re.search(r'\[(.*?)\]', reply, re.DOTALL)
        sanitize_list = pattern_string.group(1)
        pattern = r'"(.*?)"'
        items = re.findall(pattern, sanitize_list)
        return items

    def normalize_reply_many(self, reply: str, search_params: list) -> Tuple:
        """
        The `normalize_reply_many` function takes a reply string and a list of search parameters, and
        returns a tuple of matches found in the reply string, after removing the search parameters from each
        match.

        @param reply A string containing multiple lines of text.
        @param search_params A list of strings representing the search parameters.

        @return The function `normalize_reply_many` returns a tuple of matches found in the `reply` string
        based on the search parameters provided in the `search_params` list. Each match is a tuple of
        strings, where each string corresponds to a group captured by the regular expression pattern.
        """
        pattern_string = r''.join(
            fr"{param} \d+: (.+?)\n" for param in search_params)
        pattern = re.compile(pattern_string, re.DOTALL)
        matches = pattern.findall(reply)
        return matches

    def normalize_reply(self, reply: str, search_params: list):
        """
        The `normalize_reply` function extracts values from a string based on a list of search parameters.

        :param reply: The `reply` parameter is a string that contains the reply or response from a search
        query
        :type reply: str
        :param search_params: A list of strings representing the parameters you want to extract from the
        reply
        :type search_params: list
        :return: The function `normalize_reply` returns a tuple of matched groups if there is a match for
        the given search parameters in the reply string. If there is no match, it returns `None`.
        """
        pattern_string = '\n'.join(
            fr"{param}:(.+?)" for param in search_params)+'$'
        pattern = re.compile(pattern_string, re.DOTALL)
        matches = pattern.search(reply)
        return [m.strip() for m in matches.groups()] if matches else None

    def reply(self, context: Dict) -> str:
        """
        The `predict` function takes a template and a context dictionary as input, creates a prompt from the
        template, runs a language model chain using the prompt and context, and returns the search result.

        :param template: A string that represents a template for generating a prompt. It may contain
        placeholders that will be replaced with values from the context dictionary
        :type template: str
        :param context: The `context` parameter is a dictionary that contains the necessary information or
        variables needed for the prediction. It provides the values for the placeholders in the `template`
        string
        :type context: Dict
        :return: The `predict` method returns a string.
        """
        template = self._env.get_template(self.template)
        prompt = template.render(**context)
        if self.verbose:
            print(Fore.LIGHTBLUE_EX +
                  f'\n\n{"#"*20} PROMPT {"#"*20}\n{prompt}\n{"#"*20} END PROMPT {"#"*20}\n'
                  + Style.RESET_ALL)

        return self.invoke(prompt)

    def usage(self, response: dict) -> dict:
        if self.model in LLM.BEDROCK_CHAT:
            return response.response_metadata['usage']
        elif self.model in LLM.CHAT_OPENAI:
            return response.response_metadata['token_usage']
        else:
            raise ValueError('Model not supported')

    def invoke(self, prompt: str) -> str:
        """
        The `invoke` function takes a prompt, a language model chain, and a context dictionary as input, runs
        the language model chain using the prompt and context, and returns the search result.

        :param prompt: A string that represents a prompt for the language model chain
        :type prompt: str
        :param chain: The `chain` parameter is a language model chain that will be used to generate the
        search result
        :type chain: LLMChain
        :param context: The `context` parameter is a dictionary that contains the necessary information or
        variables needed for the prediction. It provides the values for the placeholders in the `prompt`
        string
        :type context: Dict
        :return: The `invoke` method returns a string.
        """
        langfuse = Langfuse()
        generation = langfuse.trace(
            id=self._monitoring._id,
        ).generation(
            name=self.__class__.__name__,
            model=LLM.LANGFUSE[self.model],
            model_parameters={'temperature': self.temperature},
            input=[{"role": "system", "content": prompt}],
        )

        response = self.llm.invoke(input=prompt)
        output = response.content

        generation.end(
            output=output,
            usage=self.usage(response),
        )
        if self.verbose:
            print(Fore.BLUE + Style.BRIGHT +
                  f'\n\n{"#"*20} RESPONSE {"#"*20}\n{output}\n{"#"*20} END RESPONSE {"#"*20}\n\n'
                  + Style.RESET_ALL)
        return output
