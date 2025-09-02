import json
import re
from ai_agents.suggestion_provider.tools import DeepScraper, QuerySearcher
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
}

context = """You are an sales assistant that help users make good purchase.
You can scrape data from slick deals through provided scraping tools(scrape_comments,scrape_deal,etc) through url.
You can search deals from a database through provided search tools (search_by_url,search_by_title,search_under_price,etc).
Do remember to provide the names of the tools you used."""

Example_return = """
🛒 **Deal Found!**

- **Product**: NXT Technologies UC-4000 Noise-Canceling Stereo USB Computer Headset (Black)
- **Price**: $11.99  
- **Original Price**: $39.99  
- **You Save**: $28.00 (70.02% off)
- **Store**: Woot!
- **Category**: Tech
- **Posted On**: August 13, 2025
- **Deal URL**: [View Deal](https://slickdeals.net/f/18516907-nxt-technologies-uc-4000-noise-canceling-stereo-usb-computer-headset-black-11-99-free-shipping-w-prime)

📌 Scraped on: August 27, 2025  
🛠️ Tool used: `search_under_price`

\n\n
"""

QuerySearcher_return = """
    - Returns: A dictionary with fields like 
        id,
        title,
        price,
        claimed_orig_price,
        discount,
        discount_percentage,
        store,
        category,
        time_stamp,
        url,
        scraped_at
    
    - Use all the fields data if you can. 
    """

DeepScraper_scheme = """
- Make sure to check data provided by tools for urls of deals.
   - Only use this if url is provide by user or tools.
   """

TOOLS_SCHEMA = f"""
You can use these tools:

1. scrape_deal → {{ "tool": "scrape_deal", "args": {{ "url": "<deal page url>" }} }}
   - Use this to extract detailed information about a specific deal from its webpage using its url.
   {DeepScraper_scheme}

2. scrape_comments → {{ "tool": "scrape_comments", "args": {{ "url": "<deal page url>" }} }}
   - Use this to extract user comments and discussions from a deal page.
   {DeepScraper_scheme}

3. search_by_url → {{ "tool": "search_by_url", "args": {{ "url": "<product url>" }} }}
   - Use this to find matching deals in the database using a product URL.
   - {QuerySearcher_return}

4. search_by_title → {{ "tool": "search_by_title", "args": {{ "keyword": "<text>", "limit": <int> }} }}
   - Use this to search for deals by keyword (e.g., keyboard, computer, iphone) in the title.
   - {QuerySearcher_return}

5. search_under_price → {{ "tool": "search_under_price", "args": {{ "keyword": "<text>", "max_price": <float>, "limit": <int> }} }}
   - Use this to find deals under a specific price, optionally filtered by keyword (e.g., "computer" under $500).
   - {QuerySearcher_return}

Rules:
- Only use the tools listed above. Do not invent results or reference other sources.
- Always respond in JSON when user data is required.
- You may return an array of tool calls if multiple tools are needed.
- Provide all useful data (eg. discounted price , price , discount percentage,store etc.)
- Always provide url of deals if url exists in data provided by tools.
"""

def classify_intent(user_input: str) -> str:
    lowered = user_input.lower()
    if any(greet in lowered for greet in ["hello", "hi", "hey", "yo", "good morning", "good evening"]):
        return "greeting"
    if any(thank in lowered for thank in ["thank you", "thanks", "appreciate"]):
        return "gratitude"
    if any(bye in lowered for bye in ["bye", "goodbye", "see you"]):
        return "farewell"
    if len(lowered.split()) <= 3:
        return "short"
    return "unknown"

def parse_llm_response(response: str):
    if not response.strip():
        return []

    try:
        parsed = json.loads(response)
        return parsed if isinstance(parsed, list) else [parsed]
    except json.JSONDecodeError:
        pass

    # Fallback: extract multiple JSON objects
    objects = re.findall(r'\{.*?\\}', response, re.DOTALL)
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
                "\n\nExample output: "+ Example_return + "use this format if possible"
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
        "Show me computer deals under $500 and its information. Give me all the details you can.",
        "Get me details and comments for https://slickdeals.net/f/18164845-metro-by-t-mobile-iphone-13-128gb-125",
        "Get me some iphone deals."
    ]

    for query in queries:
        print("\nUser:", query)
        print("SalesAssistant:", agent.run(query))