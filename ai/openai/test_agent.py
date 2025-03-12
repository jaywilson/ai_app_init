from agents.main_agent import ProjectAgent
from openai_utils import TestConversation


def test_agent():
    agent = ProjectAgent(TestConversation())
    agent.build_project("dummy user requirements")

test_agent()