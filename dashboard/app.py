# --------------------------------------------
# Imports at the top - PyShiny EXPRESS VERSION
# --------------------------------------------

# From shiny, import just reactive and render
from shiny import App,reactive, render

# From shiny.express, import just ui
from shiny.express import ui

# Imports from Python Standard Library to simulate live data
import random
from datetime import datetime
import pandas as pd
import plotly.express as px
from shinywidgets import render_plotly
from scipy import stats
from collections import deque

# --------------------------------------------
# Import icons as you like
# --------------------------------------------

from faicons import icon_svg

# --------------------------------------------
# FOR LOCAL DEVELOPMENT
# --------------------------------------------
# Add all packages not in the Std Library
# to requirements.txt:
# And install them into an active project virtual environment (usually in .venv)
# --------------------------------------------

# --------------------------------------------
# SET UP THE REACIVE CONTENT
# --------------------------------------------

# --------------------------------------------
# PLANNING: We want to get a fake temperature and 
# Time stamp every N seconds. 
# For now, we'll avoid storage and just 
# Try to get the fake live data working and sketch our app. 
# We can do all that with one reactive calc.
# Use constants for update interval so it's easy to modify.
# ---------------------------------------------------------

# --------------------------------------------
# First, set a constant UPDATE INTERVAL for all live data
# Constants are usually defined in uppercase letters
# Use a type hint to make it clear that it's an integer (: int)
# --------------------------------------------

UPDATE_INTERVAL_SECS: int = 4
# --------------------------------------------
# Initialize a REACTIVE VALUE with a common data structure
# The reactive value is used to store state (information)
# Used by all the display components that show this live data.
# This reactive value is a wrapper around a DEQUE of readings
# --------------------------------------------

DEQUE_SIZE: int = 7
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

# --------------------------------------------
# Initialize a REACTIVE CALC that our display components can call
# to get the latest data and display it.
# The calculation is invalidated every UPDATE_INTERVAL_SECS
# to trigger updates.
# It returns everything needed to display the data.
# Very easy to expand or modify.
# (I originally looked at REACTIVE POLL, but this seems to work better.)
# --------------------------------------------


@reactive.calc()
def reactive_calc_combined():
    # Invalidate this calculation every UPDATE_INTERVAL_SECS to trigger updates
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    # Data generation logic. Get random between 67 and 76 C, rounded to 1 decimal place
    temp = round(random.uniform(67, 76), 1)

    # Get a timestamp for "now" and use string format strftime() method to format it
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_dictionary_entry = {"temp":temp, "timestamp":timestamp}

    # get the deque and append the new entry
    reactive_value_wrapper.get().append(new_dictionary_entry)

    # Get a snapshot of the current deque for any further processing
    deque_snapshot = reactive_value_wrapper.get()

    # For Display: Convert deque to DataFrame for display
    df = pd.DataFrame(deque_snapshot)

    # For Display: Get the latest dictionary entry
    latest_dictionary_entry = new_dictionary_entry

    # Return a tuple with everything we need
    # Every time we call this function, we'll get all these values
    return deque_snapshot, df, latest_dictionary_entry




# ------------------------------------------------
# Define the Shiny UI Page layout - Page Options
# ------------------------------------------------

# Call the ui.page_opts() function
# Set title to a string in quotes that will appear at the top
# Set fillable to True to use the whole page width for the UI

ui.page_opts(title="Memphis Metro: Live Weather Data ", fillable=True,)

# ------------------------------------------------
# Define the Shiny UI Page layout - Sidebar
# ------------------------------------------------

# Sidebar is typically used for user interaction/information
# Note the with statement to create the sidebar followed by a colon
# Everything in the sidebar is indented consistently

with ui.sidebar(open="open"):
    with ui.card(style="background-color: blue; color: orange"):
        ui.h2("Mid South Explorer", class_="text-center", style="color: orange")
    
    with ui.card(style="background-color: blue; color: orange"):
        ui.p("A demonstration of real-time temperature Memphis Metro.", class_="text-center", style="color: orange;")
    ui.h6("Links:")

    ui.a(
        "GitHub Project Source",
        href="https://github.com/denisecase/cintel-05-cintel-basic",
        target="_blank",
    )

    ui.a(
        "GitHub For Currently Displaying  by K.Young",
        href="https://github.com/Keyoungg2/cintel-05-cintel/tree/main/dashboard",
        target="_blank",
    )


# In Shiny Express, everything not in the sidebar is in the main panel

with ui.layout_columns():
    with ui.value_box(
        showcase=icon_svg("table"),
        theme="text-orange",
        style ="blue"
    ):

        "Current Temperature"

        @render.text
        def display_temp():
            """Get the latest reading and return a temperature string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['temp']} C"

        "Get that grill a running. It's sunny with a side of Clouds"

  

    with ui.card(full_screen=True, style="background-color: blue; color: orange"):
        ui.card_header(
            "Current Date and Time",
            style="background-color: blue",
        )

        @render.text
        def display_time():
            """Get the latest reading and return a timestamp string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['timestamp']}"


#with ui.card(full_screen=True, min_height="40%"):
with ui.card(full_screen=True,  style="color: orange"):
    ui.card_header(
        "Most Recent Readings",
        style="background-color: white; color: orange;")

    @render.data_frame
    def display_df():
        """Get the latest reading and return a dataframe with current readings"""
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
        pd.set_option('display.width', None)        # Use maximum width
        return render.DataGrid( df,width="100%")

with ui.card(style="background-color: blue; color: orange"):
    ui.card_header(
        "Chart with Current Trend", style="background-color: blue")

    @render_plotly
    def display_plot():
        # Fetch from the reactive calc function
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()

        # Ensure the DataFrame is not empty before plotting
        if not df.empty:
            # Convert the 'timestamp' column to datetime for better plotting
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            # Create scatter plot for readings
            # pass in the df, the name of the x column, the name of the y column,
            # and more
        
            fig= px.scatter(df,
            x="timestamp",
            y="temp",
            title="Temperature Readings with Regression Line",
            labels={"temp": "Temperature (°C)", "timestamp": "Time"},
            color_discrete_sequence=["green"] )
            
            # Linear regression - we need to get a list of the
            # Independent variable x values (time) and the
            # Dependent variable y values (temp)
            # then, it's pretty easy using scipy.stats.linregress()

            # For x let's generate a sequence of integers from 0 to len(df)
            sequence = range(len(df))
            x_vals = list(sequence)
            y_vals = df["temp"]

            slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
            df['best_fit_line'] = [slope * x + intercept for x in x_vals]

            # Add the regression line to the figure
            fig.add_scatter(x=df["timestamp"], y=df['best_fit_line'], mode='lines', name='Regression Line')

            # Update layout as needed to customize further
            fig.update_layout(xaxis_title="Time",yaxis_title="Temperature (°C)")

        return fig


