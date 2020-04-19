import urllib.request  # instead of urllib2 like in Python 2.7
import json
import pandas as pd
from datetime import date, datetime, time, timedelta
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


#
# Exercise using json data sources, pandas data manipulation, web page access and matplotlib to
# show corona virus data.
#
# Author: Sergio Ruiz Sandoval
# Date  : 04/10/2020
#

class CoronaInfo():

    def __init__(self, root):
        # Parent window
        self.root = root

        # Object window
        self.w_corona = Toplevel(self.root)
        self.w_corona.focus()
        self.w_corona.title("Corona virus Info")
        self.w_corona.geometry("1100x800")
        self.w_corona.resizable(False, False)
        self.w_corona.config(background="white")

        # Variable instances
        self.url_data = "https://pomber.github.io/covid19/timeseries.json"
        self.sel_country = StringVar()  # Selected country
        self.initial_country = 'US'

        # Data frames
        self.df_confirmed_all = None  # All Confirmed cases
        self.df_confirmed_sel = None  # Confirmed cases for selected country
        self.df_last_day = None  # Latest data by country (last day)

        # Widgets
        self.figTrend = None
        self.ax_cases = None
        self.canvas_line_chart = None
        self.figTop10 = None
        self.ax_top10 = None
        self.canvas_bar_chart = None

        # Lambda, gets all country columns based on country selection and column name
        self.country_value = lambda column: self.df_last_day.loc[self.df_last_day["country"] == self.sel_country.get()][column].values[0]

        # Lambda, gets a particular column (attribute) for the selected country (formatted)
        self.country_attr = lambda column: "{0:,.0f}".format(self.country_value(column)).rjust(40, ".")

        # Get the information
        self.show_corona_info()

    # Shows corona virus info for selected country
    def show_cv_country_info(self):
        ttk.Label(self.w_corona, text="Confirmed cases." + self.country_attr("confirmed")).grid(row=2, column=0, sticky="nw", padx=25)
        ttk.Label(self.w_corona, text="Increase........" + self.country_attr("conf_inc")).grid(row=3, column=0, sticky="nw", padx=25)
        ttk.Label(self.w_corona, text=" ").grid(row=4, column=0, padx=25)
        ttk.Label(self.w_corona, text="Recovered cases." + self.country_attr("recovered")).grid(row=5, column=0, sticky="nw", padx=25)
        ttk.Label(self.w_corona, text="Number of deaths" + self.country_attr("deaths")).grid(row=6, column=0, sticky="nw", padx=25)

    # Refresh trend chart based on the  country selection
    def update_trend_chart(self, event):
        # Clear previous axes
        self.ax_cases.cla()
        self.ax_cases.set_title('Confirmed cases by date (' + self.sel_country.get() + ")")
        self.ax_cases.set_xlabel("Month/day")

        # Update data frame with the selected country
        self.df_confirmed_sel = self.df_confirmed_all.loc[self.df_confirmed_all['country'] == self.sel_country.get()]

        # Plot the new data
        self.df_confirmed_sel.plot(kind='line', legend=True, ax=self.ax_cases, x='mm_dd', color='r', marker='o', fontsize=10, grid=True)
        self.canvas_line_chart.draw()

        # Show country info
        self.show_cv_country_info()

    # Shows corona virus info, it gets the information from a website
    def show_corona_info(self):

        # Open the URL and read the data
        web_url = urllib.request.urlopen(self.url_data)

        # Check if the page is available
        if web_url.getcode() == 200:
            # Use the json module to load the string data into a dictionary
            data = web_url.read()
            orig_corona_dict = json.loads(data)
        else:
            messagebox.showinfo(title="Receive an error from server", message="Cannot retrieve results " + str(web_url.getcode()))
            return

        # Create a new dictionary layout (country, date, confirmed, deaths, recovered)
        new_corona_dict = {}
        local_count = 0
        for e in orig_corona_dict:
            for d in orig_corona_dict[e]:
                year = d["date"].split("-")[0]
                month = d["date"].split("-")[1].rjust(2, "0")
                day = d["date"].split("-")[2].rjust(2, "0")
                new_corona_dict[local_count] = {"country": e,
                                                "date": year + "-" + month + "-" + day,
                                                "mm_dd": month + "-" + day,
                                                "confirmed": d["confirmed"],
                                                "deaths": d["deaths"],
                                                "recovered": d["recovered"]}
                local_count += 1

        # Convert dict to data frame
        df_corona = pd.DataFrame.from_dict(new_corona_dict, orient="index")

        # Add percentage of deaths
        df_corona['pct_deaths'] = df_corona['confirmed'] / df_corona['deaths']

        # Increase from previous date (confirmed)
        df_corona['conf_inc'] = df_corona['confirmed'] - df_corona['confirmed'].shift(1)
        df_corona['conf_pct_inc'] = df_corona['conf_inc'] / df_corona['confirmed'].shift(1)

        # Get a separate df for all confirmed cases
        self.df_confirmed_all = df_corona[["country", "mm_dd", "confirmed"]]

        # Get latest date data per  country
        df_group_by_country = df_corona.groupby(['country']).max()
        self.df_last_day = df_group_by_country.reset_index()  # Information by country

        # Get the latest update date
        latest_upd = df_corona['date'].max()

        # Get the list of countries
        countries = df_corona.groupby(['country'])['country'].max().values.tolist()

        # Get Top 10 infected countries
        df_top = df_group_by_country.nlargest(10, 'confirmed').drop(columns=["date", "deaths", "recovered",
                                                                             'conf_inc', 'conf_pct_inc'])

        # Current trend for US
        self.df_confirmed_sel = self.df_confirmed_all.loc[self.df_confirmed_all['country'] == self.initial_country]

        # Show title
        ttk.Label(self.w_corona, text="COVID-19 Worldwide Data", style='Header.TLabel').grid(row=0, column=0, columnspan=5, pady=25)

        # Show source URL
        ttk.Label(self.w_corona, text="Source: " + self.url_data).grid(row=8, column=3, columnspan=2)

        # Latest update info
        ttk.Label(self.w_corona, text="Latest update: " + str(latest_upd)).grid(row=8, column=0, columnspan=2)

        # Build the combo box
        ttk.Label(self.w_corona, text="Please select a country: ", anchor="w").grid(row=2, column=3, padx=25)
        combo_country = ttk.Combobox(self.w_corona, textvariable=self.sel_country, state='readonly', width=25)
        combo_country.grid(row=2, column=4, sticky="w", padx=25)
        combo_country.config(values=countries)
        self.sel_country.set(self.initial_country)
        combo_country.bind("<<ComboboxSelected>>", self.update_trend_chart)

        # Show selected country info
        self.show_cv_country_info()

        # Build confirmed cases canvas
        self.figTrend = plt.Figure(figsize=(5, 5), dpi=100)
        self.ax_cases = self.figTrend.add_subplot(111)
        self.canvas_line_chart = FigureCanvasTkAgg(self.figTrend, self.w_corona)
        self.canvas_line_chart.get_tk_widget().grid(row=7, column=0, columnspan=2, sticky="nsew", padx=25)

        # Show confirmed cases line chart
        self.df_confirmed_sel.plot(kind='line', legend=True, ax=self.ax_cases, x='mm_dd', color='r', marker='o', fontsize=10, grid=True)
        self.ax_cases.set_title('Confirmed cases by date (' + self.sel_country.get() + ")")
        self.ax_cases.set_xlabel("Month/day")

        # Build Top 10 infected countries canvas
        self.figTop10 = plt.Figure(figsize=(5, 5), dpi=100)
        self.ax_top10 = self.figTop10.add_subplot(111)
        self.canvas_bar_chart = FigureCanvasTkAgg(self.figTop10, self.w_corona)
        self.canvas_bar_chart.get_tk_widget().grid(row=7, column=3, columnspan=2, sticky="nsew", padx=25)

        # Show Top 10 infected countries bar chart
        df_top.plot(kind='bar', legend=False, ax=self.ax_top10, rot=25, bottom=3, fontsize=8, grid=True)
        self.ax_top10.set_title('Infected countries (Top 10)')
        self.ax_top10.set_xlabel("")
