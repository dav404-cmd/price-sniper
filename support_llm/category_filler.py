from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
from pathlib import Path
import json

project_root = Path(__file__).parents[1].resolve()

def fill_category(product):
    category_file = project_root/"data"/"helper_data"/"slick_category.json"
    with open(category_file, "r") as f:
        _categories = json.load(f)

    llm = OllamaLLM(model="llama3", temperature=0.0)

    # Better prompt format
    prompt = ChatPromptTemplate.from_template("""
    You are a product categorizer. 
    Classify the following product title into ONE category from this list:
    {categories}
    
    Rules:
    - Respond with ONLY the category name.
    - Do not invent new categories.
    - Be concise.
    
    Examples:
    Input: "rtx 4060"
    Output: Tech
    
    Input: "water bottle"
    Output: Grocery
    
    Input: "karpet"
    Output: Home
    
    Now classify:
    Input: {product}
    Output:
    """)

    chain = prompt | llm

    categories = _categories

    return chain.invoke({"product": product, "categories": categories})

if __name__ == "__main__":
    output = fill_category("choco")
    print(output)