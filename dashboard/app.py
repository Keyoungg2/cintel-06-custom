# --------------------------------------------
# Imports at the top - PyShiny EXPRESS VERSION
# --------------------------------------------

# From shiny, import just reactive and render
from shiny import reactive, render
import plotly.graph_objs as go
from shiny.express import ui, input  
import random
from datetime import datetime
from collections import deque
import pandas as pd
import plotly.express as px
from shinywidgets import render_plotly
import seaborn as sns
from faicons import icon_svg
import ipywidgets as widgets
from IPython.display import display
# --------------------------------------------
DEQUE_SIZE: int = 7
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

MAX_DEQUE_SIZE = 35
# --------------------------------------------
# Initialize a REACTIVE CALC that all display components can call
# to get the latest data and display it.
# The calculation is invalidated every UPDATE_INTERVAL_SECS
# to trigger updates.
# It returns a tuple with everything needed to display the data.
# Very easy to expand or modify.
# --------------------------------------------
#Pandas pulling Data from local CSV file
cardio_mortality_df = pd.read_csv(r"C:\Users\keyou\Documents\CSIS 44630 - Continuous Intelligence\cintel-06-custom\dashboard\Heart_Disease_Mortality_Data_2019-2021.csv")
#Defining state name side bar
state_name = ['AR', 'FL', 'IN', 'KS', 'NM', 'NV', 'OR', 'PA', 'SC', 'TX', 'UT', 'WV', 'ID', 'AL', 'AK', 'CA', 'GA', 'GU', 'CO', 'IA', 'AZ', 'DE', 'CT', 'HI', 'AS', 'DC', 'OH', 'MI', 'IL', 'MN', 'LA', 'MD', 'ME', 'KY', 'MA', 'NC', 'NY', 'MO', 'MS', 'NE', 'MT', 'NJ', 'ND', 'NH', 'MP', 'TN', 'SD', 'PR', 'RI', 'OK', 'VA', 'WY', 'WI', 'WA', 'VT', 'VI', 'US']
#Creating total count for Scatter plot
cardio_mortality_df['Total_Count_Per_Year'] =cardio_mortality_df.groupby('State')['State'].transform('count')
cardio_mortality_df['Total_Count_Race'] =cardio_mortality_df.groupby('Race')['Race'].transform('count')

@reactive.calc()
def reactive_calc_combined():


    # Data generation logic
    deaths = round(random.uniform(0, 10), 1)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_dictionary_entry = {"deaths":deaths, "timestamp":timestamp}

    # get the deque and append the new entry
    reactive_value_wrapper.get().append(new_dictionary_entry)

    # Get a snapshot of the current deque for any further processing
    deque_snapshot = reactive_value_wrapper.get()

    # For Display: Convert deque to DataFrame for display
    df = cardio_mortality_df

    # For Display: Get the latest dictionary entry
    latest_dictionary_entry = new_dictionary_entry

    # Return a tuple with everything we need
    # Every time we call this function, we'll get all these values
    return deque_snapshot, df, latest_dictionary_entry

# Define the Shiny UI Page layout
# Call the ui.page_opts() function
# Set title to a string in quotes that will appear at the top
# Set fillable to True to use the whole page width for the UI
ui.page_opts(title="K.Young Heart Diease Mortality Visualization", fillable=True)

# Sidebar is typically used for user interaction/information
# Note the with statement to create the sidebar followed by a colon
# Everything in the sidebar is indented consistently
with ui.sidebar(open="open", title= "Sidebar", style="background-color: red; color: white;"):

    ui.h1("Heart Diease Mortality")

    # Create a dropdown input to choose a column with ui.input_selectize()
    ui.h2("Sidebar")
    ui.input_selectize("State","State", choices= state_name, selected='Unknown')
    
    ui.input_checkbox_group(
        "select_Race",
        "Race",
         ['American Indian', 'Alaska Native','Asian','Black','Hispanic','More than one race','Native Hawaiian or Other Pacific Islander','Unkown','White'],
        selected=["Unkown"],
        inline=True)

    ui.input_checkbox_group(
    "select_Gender",
    "Gender",
    ["Male", "Female", "Unknown"],
    selected=["Unkown"],
    inline=True)


   # Using ui.a() to add a hyperlink to the sidebar
    ui.a("K.Young GitHub", href="https://github.com/Keyoungg2/cintel-06-custom", target="_blank", style="color: white")

    ui.a("Heat Disease Mortality 2019 - 2021 dataset", href="https://data.cdc.gov/Heart-Disease-Stroke-Prevention/Heart-Disease-Mortality-Data-Among-US-Adults-35-by/55yu-xksw/data_preview", target="_blank", style="color: white")

# In Shiny Express, everything not in the sidebar is in the main panel

with ui.layout_columns():
    with ui.value_box (showcase=icon_svg('heart'),theme= 'text-red'):
    
        "Heart Diease Mortality Rates"
        @render.text
        def display_count():
            deque_snapshot, cardio_mortality_df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['deaths']}"            


with ui.navset_card_tab(id="tab"):
    # Creating Scatter plot
    with ui.nav_panel("Plotly scatterplot"):
        ui.card_header("Species Scatterplot")

        @render_plotly
        def plotly_scatterplot():
        # Scatterplot for state mortality
            return px.scatter(
                cardio_mortality_df,
                x=cardio_mortality_df["State"],
                y=cardio_mortality_df["Total_Count_Per_Year"],
                color="State",
                facet_col="Gender",
                title="Death Rates by year and Sex"
                )

    # Creating Seaborn Histogram Chart plot
    with ui.nav_panel("Seaborn Histogram Chart"):
        ui.card_header("Heart Disease Mortality by Race")

        @render.plot
        def seaborn_histogram():
            seaborn_hist = sns.histplot(cardio_mortality_df, x=cardio_mortality_df[cardio_mortality_df["Race"].isin(input.select_Race())],  y= cardio_mortality_df['Total_Count_Per_Year'])
            seaborn_hist.set_title("Seaborn Heart Disease Mortality Data")
            seaborn_hist.set_xlabel("Race")
            seaborn_hist.set_ylabel("Count")

        @reactive.calc
        def filtered_data():
         race_filtered = cardio_mortality_df[cardio_mortality_df["Race"].isin(input.select_Race())]
         return race_filtered
        
            
# Show Data
with ui.layout_columns(style="background-color: red; color: white;"):
    with ui.accordion():
        with ui.accordion_panel("Data Grid"):
            @render.data_frame
            def cardio_mortality_grid():
                return render.DataGrid(cardio_mortality_df)
            
