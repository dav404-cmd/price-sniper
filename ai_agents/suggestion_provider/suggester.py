import json
import re
from ai_agents.suggestion_provider.tools import DeepScraper, QuerySearcher

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
}

context = """You are an sales assistant that help users make good purchase.
You can scrape data from slick deals through provided scraping tools(scrape_comments,scrape_deal,etc) through url.
You can search deals from a database through provided search tools (search_by_url,search_by_title,search_under_price,etc).
Do remember to provide the names of the tools you used."""

TOOLS_SCHEMA = """
You can use these tools:

1. scrape_deal → { "tool": "scrape_deal", "args": { "url": "<deal page url>" } }
   - Use this to extract detailed information about a specific deal from its webpage.

2. scrape_comments → { "tool": "scrape_comments", "args": { "url": "<deal page url>" } }
   - Use this to extract user comments and discussions from a deal page.

3. search_by_url → { "tool": "search_by_url", "args": { "url": "<product url>" } }
   - Use this to find matching deals in the database using a product URL.

4. search_by_title → { "tool": "search_by_title", "args": { "keyword": "<text>", "limit": <int> } }
   - Use this to search for deals by keyword in the title. Useful for general queries like "iphone" or "laptop".

5. search_under_price → { "tool": "search_under_price", "args": { "keyword": "<text>", "max_price": <float>, "limit": <int> } }
   - Use this to find deals under a specific price, optionally filtered by keyword (e.g., "computer" under $500).

Rules:
- Only use the tools listed above. Do not invent results or reference other sources.
- Always respond in JSON when user data is required.
- You may return an array of tool calls if multiple tools are needed.
"""

def parse_llm_response(response: str):
    if not response.strip():
        return []

    try:
        parsed = json.loads(response)
        return parsed if isinstance(parsed, list) else [parsed]
    except json.JSONDecodeError:
        pass

    # Fallback: extract multiple JSON objects
    objects = re.findall(r'\{.*?\}', response, re.DOTALL)
    result = []
    for obj in objects:
        try:
            result.append(json.loads(obj))
        except json.JSONDecodeError:
            continue
    return result

class SalesAssistantAgent:
    def __init__(self, llm):
        self.llm = llm
        self.tools = TOOLS

    def run(self, user_input: str):
        prompt = f"{TOOLS_SCHEMA}\n\nUser request: {user_input}"
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
            return "Sorry, I couldn't parse any valid tool calls from the LLM response."

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
                annotated_results.append(f"Tool used: {tool_name}\nResult:\n{json.dumps(output, indent=2)}")

        followup_prompt = (
                "You are a helpful sales assistant.\n"
                "The following tool results were obtained:\n\n" +
                "\n\n".join(annotated_results) +
                "\n\nPlease summarize clearly for the user, and mention which tools were used."
        )
        return self.llm.ask(followup_prompt)

# ----- Example LLM interface -----
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
        "Show me computer deals under $500 and its information.",
        "Get me details and comments for https://slickdeals.net/f/18164845-metro-by-t-mobile-iphone-13-128gb-125",
        "Get me some iphone deals."
    ]

    for query in queries:
        print("\nUser:", query)
        print("SalesAssistant:", agent.run(query))