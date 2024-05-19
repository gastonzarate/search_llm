
from dataclasses import dataclass, field

from agents.base_agent.models import BaseModel, LangfuseTrace
from agents.search.tools import TermsToSearchAgent, ResultsSelectionAgent, ResultsUrlsAgent
from langfuse import Langfuse
from googlesearch import search
import re


def extract_urls(text):
    # Expresión regular para encontrar URLs
    url_pattern = r'https?://\S+|www\.\S+'

    # Encontrar todas las coincidencias de URLs en el texto
    urls = re.findall(url_pattern, text)

    # Agregar 'http://' a las URLs que no lo tienen
    full_urls = []
    for url in urls:
        if not url.startswith('http'):
            url = 'http://' + url
        full_urls.append(url)

    return full_urls

@dataclass
class SearchModel(BaseModel):
    input: str

    # Monitoring
    _monitoring: LangfuseTrace

    # Log attributes
    title: str = ''

    def success(self) -> bool:
        """
        Checks if the script execution was successful.

        Returns:
            bool: True if the script execution was successful, False otherwise.
        """
        return bool(True)

    def start_monitoring(self, input: str):
        langfuse = Langfuse()
        trace = langfuse.trace(
            name="Search Agent",
            user_id=self._monitoring.user_id,
            session_id=self._monitoring.session_id,
            tags=self._monitoring.tags,
            input=input,
        )
        self._monitoring._id = trace.id
        return trace

    def end_monitoring(self, trace, output: str):
        trace.update(output=output)


    def resolve(self) -> None:
        trace = self.start_monitoring(input=self.input)

        terms_to_search = TermsToSearchAgent(self._monitoring).run(
            context={"input": self.input})
        terms_to_search = terms_to_search[1:-1]

        google = search(terms_to_search, advanced=True, num_results=15)
        terms_to_search_advanced = ResultsSelectionAgent(self._monitoring).run(
            context={"input": self.input,
                     "results": google})
        
        google = search(terms_to_search_advanced,
                        advanced=True, num_results=15)
        
        urls_response = ResultsUrlsAgent(self._monitoring).run(
            context={"input": self.input,
                     "results": google})
        
        urls = extract_urls(urls_response)
        [print(urls)]

        self.end_monitoring(trace, terms_to_search)
