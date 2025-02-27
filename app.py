# -*- coding: utf-8 -*-
"""app.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1HUDXAV10iyWeGLW0dehYxhbj1rWHvfSI
"""

!pip install langchain
!pip install langchain-core
!pip install langchain-huggingface
!pip install huggingface_hub
!pip install transformers
!pip install accelerate
!pip install bitsandbytes
!pip install google_search_results
!pip install --upgrade langchain langchain-community
!pip install gradio

import os
import re
import random
import warnings
from typing import Optional

import langchain
from langchain_huggingface import ChatHuggingFace
from langchain_huggingface import HuggingFaceEndpoint
from langchain.agents import AgentType, initialize_agent
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.agents import load_tools
from langchain.tools import Tool
from langchain.output_parsers import RegexParser
from langchain.agents import AgentOutputParser
from langchain.schema import AgentAction, AgentFinish
from langchain.utilities import SerpAPIWrapper
from dotenv import load_dotenv

load_dotenv()
# from google.colab import userdata
# HUGGING_FACE = userdata.get('HuggingAPI')
# SERPAPI = userdata.get('SerpApi')

# os.environ["HUGGINGFACEHUB_API_TOKEN"]= HUGGING_FACE
# os.environ["SERPAPI_API_KEY"] = SERPAPI

# model_name = "deepseek-ai/DeepSeek-R1"
# serp_api_key = os.getenv(SERPAPI)

model_name = "deepseek-ai/DeepSeek-R1"
serp_api_key = os.getenv("SERPAPI")
HuggingFace = os.getenv("HuggingFace")

os.environ["HUGGINGFACEHUB_API_TOKEN"]= HuggingFace
os.environ["SERPAPI_API_KEY"] = serp_api_key

# Ignore all FutureWarning messages from the 'huggingface_hub' module
warnings.filterwarnings('ignore', category=FutureWarning, module='huggingface_hub')

#Simulates an e-commerce product search with filtering options.
def e_commerce_search(query, color=None, price_range=None, size=None):
    colors = ["red", "blue", "black", "white", "green"]
    sizes = ["S", "M", "L", "XL"]
    products = []

    # Parse price range from string if provided
    if isinstance(price_range, str):
        try:
            if "under" in price_range.lower():
                max_price = float(re.findall(r'\d+', price_range)[0])
                price_range = (0, max_price)
            elif "-" in price_range:
                min_price, max_price = map(float, re.findall(r'\d+', price_range))
                price_range = (min_price, max_price)
        except:
            price_range = None

    for _ in range(10):
        product = {
            "name": f"{query.title()} {random.choice(['Shirt', 'Dress', 'Jacket', 'Pants'])}",
            "color": random.choice(colors),
            "price": random.randint(20, 150),
            "size": random.choice(sizes),
            #"site": random.choice(["ShopA", "ShopB", "ShopC"])
        }
        products.append(product)

    filtered = products
    if color:
        filtered = [p for p in filtered if p["color"].lower() == color.lower()]
    if price_range:
        filtered = [p for p in filtered if price_range[0] <= p["price"] <= price_range[1]]
    if size:
        filtered = [p for p in filtered if p["size"].lower() == size.lower()]

    return filtered

def shipping_time_estimator(location="default", delivery_date="2025-03-01"):
    from datetime import datetime, timedelta
    estimated_days = random.randint(2, 7)
    estimated_delivery = datetime.now() + timedelta(days=estimated_days)
    feasible = estimated_delivery.date() <= datetime.strptime(delivery_date, "%Y-%m-%d").date()
    return {
        "feasible": feasible,
        "cost": f"${random.randint(5, 20)}",
        "estimated_delivery": estimated_delivery.strftime("%Y-%m-%d")
    }

def discount_checker(price_info):
    try:
        if isinstance(price_info, str):
            base_price = float(re.findall(r'\d+', price_info)[0])
        else:
            base_price = float(price_info)

        promo_codes = {
            "SAVE10": 0.10,
            "SAVE20": 0.20,
            "FREESHIP": 0
        }

        discounts = []
        for code, discount in promo_codes.items():
            final_price = base_price * (1 - discount)
            savings = base_price - final_price
            discounts.append({
                "code": code,
                "final_price": round(final_price, 2),
                "savings": round(savings, 2)
            })

        return {
            "original_price": base_price,
            "available_discounts": discounts
        }
    except:
        return "Invalid price format provided"

def return_policy_checker(site_name):
    policies = {
        "ShopA": "30-day return policy with free returns.",
        "ShopB": "14-day return policy, shipping fees apply.",
        "ShopC": "No returns on sale items, 30-day policy otherwise."
    }
    return policies.get(site_name, "Return policy not available.")

#Custom parser to interpret LLM outputs for agent actions or final responses.
class CustomOutputParser(AgentOutputParser):

    def parse(self, llm_output: str) -> AgentAction | AgentFinish:

      # Parses the LLM output to determine if it's a final answer or an action.
      # llm_output (str): The raw output from the LLM.
      # Returns: AgentAction | AgentFinish: Parsed result indicating either an action to perform or the final response.

        try:
            if "Final Answer:" in llm_output:
                return AgentFinish(
                    return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                    log=llm_output,
                )

            action_match = re.search(r"Action: (.*?)\nAction Input: (.*)", llm_output, re.DOTALL)
            if not action_match:
                raise ValueError("Could not parse LLM output: " + llm_output)

            action = action_match.group(1).strip()
            action_input = action_match.group(2).strip()

            return AgentAction(tool=action, tool_input=action_input, log=llm_output)
        except Exception as e:
            raise ValueError(f"Could not parse LLM output: {llm_output}. Error: {str(e)}")

def setup_shopping_assistant(model_name, serp_api_key):
    # Initialize SerpAPI
    serp = SerpAPIWrapper(serpapi_api_key=serp_api_key)

    # Define tools
    tools = [
        Tool(
            name="E-Commerce Search",
            func=e_commerce_search,
            description="Search for products with optional filters (color, price_range, size). Input should be product query string or JSON with filters."
        ),
        Tool(
            name="Shipping Estimator",
            func=shipping_time_estimator,
            description="Get shipping cost and delivery estimate. Input should be location and delivery date (YYYY-MM-DD)."
        ),
        Tool(
            name="Discount Checker",
            func=discount_checker,
            description="Check available discounts for a price. Input should be the price as a number."
        ),
        Tool(
            name="Return Policy",
            func=return_policy_checker,
            description="Check store return policy. Input should be store name (ShopA, ShopB, or ShopC)."
        ),
        Tool(
            name="Real Product Search",
            func=serp.run,
            description="Search for real products online when other tools don't find matches. Use as last resort."
        )
    ]

    # Define prompt
    prompt = PromptTemplate(
        input_variables=["query"],
        template="""You are a helpful Shopping Assistant. Your task is to help users find products and provide relevant information.

Available tools:
- E-Commerce Search: Find products with filters (color, price, size)
- Shipping Estimator: Get shipping costs and delivery dates
- Discount Checker: Find available discounts
- Return Policy: Check store return policies
- Real Product Search: Search real products online (use only if other tools fail)

User Query: {query}

Follow these steps:
1. Analyze the query to identify product requirements (type, color, price, size)
2. Use E-Commerce Search first to find matching products
3. For found products, check discounts and shipping
4. Provide return policy information for the store
5. Only use Real Product Search if no matches found


After getting results, provide a Final Answer with:
- Found products (give similar products if no matches found)
- Available discounts
- Shipping information
- Return policy
- Recommendations
- Website Link (optional)

Begin answering the query:"""
    )

    # Initialize LLM
    llm = HuggingFaceEndpoint(
        repo_id=model_name,
        task="text-generation",
        temperature=0.5,
        model_kwargs={"max_length": 100}
    )


    #Initialize agent
    agent = initialize_agent(
        tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        agent_kwargs={
        "prompt": prompt,
        "output_parser": CustomOutputParser()
    }


    )

    return agent

def run_shopping_assistant(query):
    try:
        agent = setup_shopping_assistant(model_name, serp_api_key)

        try:

          # Initialize the shopping assistant agent

            print("\nSearching for products...")
            response = agent.run(query).strip()
            print("\nResults:")
            return response

            # If no products found, manually raise an exception
            if "Unfortunately, I couldn't find any" in response:
              raise ValueError("No products found.")


        except Exception as e:
            try:
                    # Fallback to SerpAPI if agent fails or finds no products
                    serp = SerpAPIWrapper(serpapi_api_key=serp_api_key,task="text-generation",model_kwargs={"max_length": 100})
                    real_products = serp.run(query).strip()
                    print("\nFound these real products:")
                    return real_products

            except Exception as serp_error:

                    # Handle failure in the fallback search
                    return "Sorry, I couldn't find any matching products. Please try a different search."

    except Exception as e:

      # Handle errors during setup or API key issues
        print(f"Error: {str(e)}")
        print("Please check your configuration and try again.")

#Testing Code
# query = input("\nYour query: ")
# run_shopping_assistant(query)

import gradio as gr

def chatbot_response(query):
    assistant = run_shopping_assistant(query)
    return assistant

# Create Gradio interface
iface = gr.Interface(
    fn=chatbot_response,
    inputs=gr.Textbox(lines=2, placeholder="Ask your shopping assistant..."),
    outputs=gr.Textbox(label="Assistant Response"),
    title="Shopping Assistant Chatbot",
    description="A simple shopping assistant chatbot."
)

# Launch the app
iface.launch(share=True)
