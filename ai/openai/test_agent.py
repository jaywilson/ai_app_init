from agents.main_agent import ProjectAgent
from openai_utils import TestOpenAIUtils


def test_agent():
    agent = ProjectAgent(TestOpenAIUtils())
    agent.build_frontend("dummy user requirements")

test_agent()