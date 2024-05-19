from agents.search.models import SearchModel
from agents.base_agent.models import LangfuseTrace

search = SearchModel(input='no encuentro el precio de llama 3 en bedrock',
                     _monitoring = LangfuseTrace("1","1",['test']))

search.run()
