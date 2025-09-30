import json
from ai_agents.suggestion_provider.tools.deepscraper_tool import DeepScraper
from ai_agents.suggestion_provider.tools.querysearch_tools import QuerySearcher
from ai_agents.suggestion_provider.prompts import TOOLS_SCHEMA,context
from ai_agents.suggestion_provider.utils_fuctions import parse_llm_response,classify_intent
from data.data_cleaner.date_formating import json_serializable
# Initialize tools
scraper = DeepScraper()
query_db = QuerySearcher()

TOOLS = {
    "scrape_deal": lambda args: scraper.get_deal_details(scraper.get_html(args["url"])),
    "scrape_comments": lambda args: scraper.get_comments(scraper.get_html(args["url"])),
    "search_by_url": lambda args: query_db.search_by_url(args["url"]),
    "search_by_title": lambda args: query_db.search_by_title(args["keyword"], args.get("limit", 5)),
    "search_under_price": lambda args: query_db.search_under_price(
    args.get("keyword"), args["max_price"], args.get("limit", 5)
),
    "search_closest_price": lambda args: query_db.search_closest_price(args["keyword"],args["price"],args.get("limit",5)),
    "search_recent_deals":lambda args:query_db.search_recent_deals(args["keyword"],args["days_ago"],args.get("limit",5)),
}

#---- Agent ----
class SalesAssistantAgent:
    def __init__(self, llm):
        self.llm = llm
        self.tools = TOOLS

    def run(self, user_input: str,history: list):

        conversation = "\n".join(
            [f"{m['role'].capitalize()}: {m['content']}" for m in history]
        )

        prompt = (
            f"{TOOLS_SCHEMA}\n\n"
            f"Conversation so far:\n{conversation}\n\n"
            f"User request: {user_input}"
        )
        normal_prompt = f"You are an friendly sales assistant.Tasked to help users gain high value of there money."
        response = self.llm.ask(prompt)
        tool_calls = parse_llm_response(response)

        if not tool_calls:
            retry_prompt = (
                f"{TOOLS_SCHEMA}{context}\n\n"
                f"Your previous response was not valid JSON.\n"
                f"Please respond ONLY with a JSON array of tool calls.\n"
                f"User request: {user_input}"
            )
            response = self.llm.ask(retry_prompt)
            tool_calls = parse_llm_response(response)

        if not tool_calls:
            intent = classify_intent(user_input)
            if intent == "greeting":
                return "Hey there! 👋 I'm your deal-finding assistant. Just let me know what you're shopping for today."
            elif intent == "gratitude":
                return "You're welcome! Let me know if you'd like help finding a great deal."
            elif intent == "farewell":
                return "Take care! Hope you score something awesome next time."
            elif intent == "short":
                return "Could you tell me a bit more about what you're looking for? I can help you find deals, compare prices, or explore product info."
            else:
                return self.llm.ask(normal_prompt)

        results_summary = []
        for call in tool_calls:
            tool_fn = self.tools.get(call.get("tool"))
            if not tool_fn:
                results_summary.append({"error": f"Unknown tool: {call.get('tool')}"})
                continue

            try:
                result = tool_fn(call["args"])
                results_summary.append({call["tool"]: result})
            except Exception as e:
                results_summary.append({call["tool"]: f"Error during execution: {str(e)}"})

        annotated_results = []
        for result in results_summary:
            for tool_name, output in result.items():
                annotated_results.append(
                    f"Tool used: {tool_name}\nResult:\n{json.dumps(output, indent=2, default=json_serializable)}"
                )

        followup_prompt = (
                "You are a helpful sales assistant.\n"
                "The following tool results were obtained:\n\n" +
                "\n\n".join(annotated_results) +
                "\n\nPlease summarize clearly for the user, and mention which tools were used."
                "\n\nPlease also provide the url of the deals."
        )
        return self.llm.ask(followup_prompt)

# ----- The LLM interface -----
import subprocess

class DummyLLM:
    def __init__(self, model="llama3"):
        self.model = model

    def ask(self, prompt: str):
        process = subprocess.run(
            ["ollama", "run", self.model],
            input=prompt.encode("utf-8"),
            capture_output=True
        )
        return process.stdout.decode("utf-8").strip()

# ----- Example Usage -----
if __name__ == "__main__":
    llm = DummyLLM()
    agent = SalesAssistantAgent(llm)

    queries = [
        "Get me details and comments for https://slickdeals.net/f/18164845-metro-by-t-mobile-iphone-13-128gb-125",
        "Get me some iphone deals.",
        "show me iphone of $700 and there urls"
    ]
    history = []

    for query in queries:
        print("\nUser:", query)
        print("SalesAssistant:", agent.run(query,history))