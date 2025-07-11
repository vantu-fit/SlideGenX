from .deep_research.graph import agent_graph

import uuid
import os
from typing import Optional

class DeepResearchAgent:
    def __init__(self, logs_dir="logs", reports_dir="reports"):
        self.logs_dir = logs_dir
        self.reports_dir = reports_dir
        self.report_file = os.path.join(self.reports_dir, "final_report.md")
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)

    def _generate_thread_config(self):
        return {
            "configurable": {
                "thread_id": str(uuid.uuid4()),
                "max_queries": 3,
                "search_depth": 2,
                "num_reflections": 1,
                "temperature": 0.3
            }
        }

    def _log_event(self, event):
        with open(os.path.join(self.logs_dir, "deep_research_agent_logs.txt"), "a", encoding="utf-8") as f:
            f.write(str(event))
            f.write("\n\n\n")

    def _get_report_content(self) -> Optional[str]:
        """Retrieve the content of the final report if it exists."""
        if not os.path.exists(self.report_file):
            return None
        
        try:
            with open(self.report_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading report file: {e}")
            return None

    def run(self, topic: str, audience: str = "University students and researchers", purpose: str = "Education"):
        outline = f"Explore the {topic} to prepare a report on the topic, toward the audience of {audience} in order to {purpose}."
        thread_config = self._generate_thread_config()

        print("🔍 Starting deep research...")
        try:
            for event in agent_graph.stream({"topic": topic, "outline": outline}, config=thread_config):
                self._log_event(event)
                print(f"DEBUG: Event keys: {list(event.keys())}")

                if "report_structure_planner" in event:
                    print("📋 Planning report structure...")
                elif "human_feedback" in event:
                    print("💭 Processing feedback...")
                elif "section_formatter" in event:
                    print("🔧 Formatting sections...")
                    # Debug: check sections
                    sections = event.get("section_formatter", {}).get("sections", [])
                    print(f"DEBUG: Found {len(sections)} sections")
                elif "finalizer" in event:
                    print("✅ Research completed!")
                    break
                elif any(k in event for k in ["parallel_research_agent", "queue_next_section"]):
                    continue
                # else:
                #     print("<<< UNKNOWN EVENT >>>")
                #     print("\n", "="*100, "\n")

            # Retrieve the final report content
            research_content = self._get_report_content()
            if research_content:
                print(f"📄 Research report: {self.report_file} ({len(research_content)} characters)")
                return research_content
            else:
                print("⚠️ No research report found")
                return None
        except Exception as e:
            print(f"An error occurred during the research process: {e}")


if __name__ == "__main__":
    topic = "Reinforcement learning and the future of AGI"
    audience = "AI researchers and enthusiasts"
    purpose = "Education"

    agent = DeepResearchAgent()
    result = agent.run(topic, audience=audience, purpose=purpose)
    if result:
        print("Research content preview:")
        print(result[:500] + "..." if len(result) > 500 else result)
