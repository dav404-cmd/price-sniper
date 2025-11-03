from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path
import json

project_root = Path(__file__).parents[1].resolve()

import os

def is_in_docker() -> bool:
    """Detect if the script is running inside a Docker container."""
    # Method 1: check for the Docker environment file
    if os.path.exists("/.dockerenv"):
        return True
    # Method 2: check cgroup info (covers some edge cases)
    try:
        with open("/proc/1/cgroup", "rt") as f:
            return any("docker" in line or "containerd" in line for line in f)
    except Exception:
        pass
    return False


def fill_category(product):
    category_file = project_root/"data"/"helper_data"/"slick_category.json"
    with open(category_file, "r") as f:
        _categories = json.load(f)

    if is_in_docker():
        base_url = "http://host.docker.internal:11434"
    else:
        base_url = "http://localhost:11434"

    llm = OllamaLLM(model="llama3", temperature=0.0,base_url=base_url)

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