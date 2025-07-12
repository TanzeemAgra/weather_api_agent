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
            desc = response["weather"][0]["description"]
            return f"The current weather in {location} is {temp}°C with {desc}."
        else:
            return "Couldn't fetch weather"
    except Exception as e:
        return f"Error fetching weather: {e}"
    
#PDF Exporter
def export_to_pdf(question, answer):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Travel Query: {question}\n\nAgent Response:\n{answer}")
    file_path = "/data/travel_plan.pdf"
    pdf.output(file_path)
    return file_path

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
    query = st.text_input("Ask Your Travel Question")

    if query:
        # LLMS and Tools
        llm = OpenAI(temprature=0)
        wikipedia = WikipediaAPIWrapper()
        math_chain = LLMMathChain(llm=llm)

        tools = [
            Tool(name="Wekipedia Search", func=wikipedia.run, description="useful for getting location or place details"),
            Tool(name="Calculator", func=math_chain.run, description="Useful for doing travel budget calculations"),
            Tool(name="Weather Info", func=get_weather, description="Get real-time weather information for a city")

        ]

        #Initialise agent with Memory
        agent_executor = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory= memory,
            verbose = True
        )

        with st.spinner("Thinking ..."):
            result = agent_executor.run(query)
            st.success(result)

        #PDF Export Button
        if st.button("Export this plan as PDF"):
            pdf_path = export_to_pdf(query, result)
            with open(pdf_path, "rb") as file:
                st.download_button("Download PDF", file, file_name="travel_pla.pdf")
    
else:
    st.info("Please enter your OpenAI API Key to Start")
        

