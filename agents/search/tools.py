
from agents.base_agent.constants import LLM
from agents.base_agent.tools import BaseAgent


class TermsToSearchAgent(BaseAgent):
    model: LLM = LLM.CLAUDE_3_SONNET
    temperature: int = 0.4
    template = 'terms_to_search.jinja'


class ResultsSelectionAgent(BaseAgent):
    model: LLM = LLM.CLAUDE_3_SONNET
    temperature: int = 0.4
    template = 'results_selection.jinja'


class ResultsUrlsAgent(BaseAgent):
    model: LLM = LLM.CLAUDE_3_SONNET
    temperature: int = 0.4
    template = 'results_urls.jinja'
