from .agents.domain import DomainAgent
# Will import others as we build them

class MarketingAgency:
    """
    Main Orchestrator for the ADK-style Marketing Agency.
    """
    def __init__(self):
        self.domain_agent = DomainAgent("DomainAgent")
        # self.web_agent = WebDevAgent("WebDevAgent")
        # self.strategist = StrategistAgent("Strategist")
        # self.creator = CreatorAgent("Creator")

    def run_domain_search(self, topic):
        print(f"Agency: Finding perfect domain for '{topic}'...")
        return self.domain_agent.suggest_domains(topic)

    # Future methods for full pipeline
    # def launch_brand(self, topic): ...
