from .agents.domain import DomainAgent
from .agents.strategist import StrategistAgent
from .agents.creator import CreatorAgent
from .agents.web_dev import WebDevAgent
from .agents.logo import LogoDesignAgent
from .agents.visual import VisualDesignAgent

class MarketingAgency:
    """
    Main Orchestrator for the ADK-style Marketing Agency.
    """
    def __init__(self):
        self.domain_agent = DomainAgent("DomainAgent")
        self.strategist = StrategistAgent("Strategist")
        self.creator = CreatorAgent("Creator")
        self.web_dev = WebDevAgent("WebDev")
        self.logo_designer = LogoDesignAgent("LogoDesigner")
        self.visual_designer = VisualDesignAgent("VisualDesigner")

    def run_domain_search(self, topic):
        print(f"Agency: Finding perfect domain for '{topic}'...")
        return self.domain_agent.suggest_domains(topic)

    def create_strategy(self, topic, brand_info):
        print(f"Agency: Developing strategy for '{topic}'...")
        return self.strategist.plan_marketing_campaign(topic, brand_info)

    def generate_day_content(self, day_plan, brand_info, critique=None):
        print(f"Agency: Creating content for {day_plan.get('day', 'Day')}...")
        return self.creator.draft_content(day_plan, brand_info, critique)

    def build_website(self, strategy, brand_info, topic):
        print(f"Agency: Designing landing page for '{topic}'...")
        return self.web_dev.build_landing_page(strategy, brand_info, topic)

    def design_logo(self, brand_info):
        print(f"Agency: Designing logo for '{brand_info.get('name', 'Brand')}'...")
        return self.logo_designer.design_brand_logo(brand_info)

    def generate_visual(self, topic, title, style_preset, brand_info):
        print(f"Agency: Designing '{style_preset}' visual for '{title}'...")
        return self.visual_designer.generate_social_visual(topic, title, style_preset, brand_info)

    # Future methods for full pipeline
    # def launch_brand(self, topic): ...
