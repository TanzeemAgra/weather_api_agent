import os
import streamlit as st
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain.llms import openai
from langchain.chains.llm_math.base import LLMMathChain
from langchain.utilities import WikipediaAPIWrapper
from langchain.memory import ConversationBufferMemory
from fpdf import FPDF
import requests

# Streamlit Page Config
st.set_page_config(page_title="AI Travel Assistant", page_icon="🛩️")
st.title(" AI Travel Assistant Agent")

#API Inputs
api_key = st.text_input("Enter Your OpenAI API Key:", type="password")
weather_api_key = st.text_input("Enter Your OpenWeatherMap API Key:(Optional)", type="password")

#Initialise the memory
memory = ConversationBufferMemory(memory_key="chat_history")

#Define the Whether Tool

def get_weather(location):
    if not weather_api_key:
        return "weather API Key not provided."
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={weather_api_key}&units=metric"
        response = requests.get(url).json()
        if response.get("main"):
            temp = response["main"]["temp"]
            desc = response["whether"][0]["describtion"]
            return f"The current weather in {location} is {temp}°C with {desc}."
        else:
            return "Couldn't fetach weather"
    except Exception as e:
        return f"Error fetching weather: {e}"
    
        

