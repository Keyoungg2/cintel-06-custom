import plotly.express as px
from shiny.express import input, ui
from shinywidgets import render_plotly
import pandas as pd
import random
from datetime import datetime
from faicons import icon_svg
from shiny import reactive, render, req
from collections import deque
import requests

# Path to the CSV file on the local drive
file_path = r'C:\Users\keyou\Documents\CSIS 44630 - Continuous Intelligence\cintel-06-custom\dashboard\Heart_Disease_Mortality_Data_2019-2021.csv'

# Read the CSV file into a pandas DataFrame
cardio_death_df = pd.read_csv(file_path)

state_name = ['AR', 'FL', 'IN', 'KS', 'NM', 'NV', 'OR', 'PA', 'SC', 'TX', 'UT', 'WV', 'ID', 'AL', 'AK', 'CA', 'GA', 'GU', 'CO', 'IA', 'AZ', 'DE', 'CT', 'HI', 'AS', 'DC', 'OH', 'MI', 'IL', 'MN', 'LA', 'MD', 'ME', 'KY', 'MA', 'NC', 'NY', 'MO', 'MS', 'NE', 'MT', 'NJ', 'ND', 'NH', 'MP', 'TN', 'SD', 'PR', 'RI', 'OK', 'VA', 'WY', 'WI', 'WA', 'VT', 'VI', 'US']

DEQUE_SIZE: int = 3
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

MAX_DEQUE_SIZE = 10

@reactive.calc()
def reactive_calc():


    # generate data for death count
    deaths = round(random.uniform(3, 10), 1)
    #generates timestamp data
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #generates log of deaths and timestaps captured 
    new_dictionary_entry = {" Number of deaths":deaths, "timestamp":timestamp}
    #  append the new entr of deques
    reactive_value_wrapper.get().append(new_dictionary_entry)
    # Snapshot of the deques
    deque_snapshot = reactive_value_wrapper.get()
    # Convert deque to DataFrame 
    df = cardio_death_df
    # Display the latest entry
    latest_dictionary_entry = new_dictionary_entry

    return deque_snapshot, df, latest_dictionary_entry

# Naming page
ui.page_opts(title="K.Young Heart Diease Mortality Visualization", fillable=True)

# Add a Shiny UI sidebar
with ui.sidebar(open="open", title= "Sidebar", style="background-color: red; color: white;"):

    ui.h1("Heart Diease Mortality")

# Create a dropdown input to choose a column with ui.input_selectize()
    ui.input_selectize("LocationAbbr","State", choices= state_name, selected="unknown")

# Add checkbox group input to filter the species
    ui.input_checkbox_group(
    "select_Gender",
    "Gender",
    ["Male", "Female", "Unknown"],
    selected=["Unkown"],
    inline=True)

# Adding a horizontal rule to the sidebar
    ui.hr()

# Using ui.a() to add a hyperlink to the sidebar
    ui.a("K.Young GitHub", href="https://github.com/Keyoungg2/cintel-06-custom", target="_blank", style="color: white")

    ui.a("Heat Disease Mortality 2019 - 2021 dataset", href="https://data.cdc.gov/Heart-Disease-Stroke-Prevention/Heart-Disease-Mortality-Data-Among-US-Adults-35-by/55yu-xksw/data_preview", target="_blank", style="color: white")
