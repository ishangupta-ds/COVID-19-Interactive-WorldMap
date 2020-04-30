
# packages to store and manipulate data
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# packages for visualizations
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.offline import plot
import plotly.graph_objects as graphO
import pycountry

from flask import Flask, request, Markup, render_template

app = Flask(__name__, template_folder='templates')


def totalcase():

    #date_format(month,day,year)

    now = datetime.now()
    if now.day != 1:
        day = str(now.day-1)
        month = str(now.month)
        if len(day) == 1:
            day = '0' + day
        if len(month) == 1:
            month = '0' + month

        year = str(now.year)
        strrep = month+"-"+day+"-"+year

    else:

        yesterday = datetime.now() - timedelta(days=1)
        day = str(yesterday.day)
        month = str(yesterday.month)
        if len(day) == 1:
            day = '0' + day
        if len(month) == 1:
            month = '0' + month
        year = str(yesterday.year)
        strrep = month+"-"+day+"-"+year

    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv'.format(
        strrep)
    df = pd.read_csv(url, parse_dates=['Last_Update'])
    df.rename(columns={'ObservationDate': 'Date'}, inplace=True)

    # Rename countries so they show up in pycountry
    df["Country_Region"].replace({'US': 'United States'}, inplace=True)

    df['Last_Update'] = df['Last_Update'].apply(
        lambda x: (str(x)).split(" ")[0])

    plt.figure(2, figsize=(14, 14/1.5))
    plt.title("Top Reported Covid-19 Countries")
    df['Country_Region'].value_counts()[:25].plot(kind='bar')

    confirmed = df.groupby('Last_Update').sum()['Confirmed'].reset_index()
    deaths = df.groupby('Last_Update').sum()['Deaths'].reset_index()
    recovered = df.groupby('Last_Update').sum()['Recovered'].reset_index()

    totalCases = graphO.Figure()
    totalCases.add_trace(graphO.Bar(x=confirmed['Last_Update'],
                                    y=confirmed['Confirmed'],
                                    name='Confirmed',
                                    marker_color='cyan'
                                    ))

    totalCases.add_trace(graphO.Bar(x=recovered['Last_Update'],
                                    y=recovered['Recovered'],
                                    name='Recovered',
                                    marker_color='blue'
                                    ))

    totalCases.add_trace(graphO.Bar(x=deaths['Last_Update'],
                                    y=deaths['Deaths'],
                                    name='Deaths',
                                    marker_color='magenta'
                                    ))

    totalCases.update_traces(
        textposition='outside'
    )

    totalCases.update_layout(
        title='Total Reported Covid-19 Cases',
        xaxis_tickfont_size=12,
        yaxis=dict(
            title='Reported Cases',
            titlefont_size=18,
            tickfont_size=12,
        ),
        legend=dict(
            x=1,
            y=1,
        ),
        barmode='stack',
        bargroupgap=0.1
    )

    return totalCases


def mapworld():

    #date_format(month,day,year)

    now = datetime.now()
    if now.day != 1:
        day = str(now.day-1)
        month = str(now.month)
        if len(day) == 1:
            day = '0' + day
        if len(month) == 1:
            month = '0' + month

        year = str(now.year)
        strrep = month+"-"+day+"-"+year

    else:

        yesterday = datetime.now() - timedelta(days=1)
        day = str(yesterday.day)
        month = str(yesterday.month)
        if len(day) == 1:
            day = '0' + day
        if len(month) == 1:
            month = '0' + month
        year = str(yesterday.year)
        strrep = month+"-"+day+"-"+year

    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv'.format(
        strrep)
    df = pd.read_csv(url, parse_dates=['Last_Update'])
    df.rename(columns={'ObservationDate': 'Date'}, inplace=True)

    # Rename countries so they show up in pycountry
    df["Country_Region"].replace({'US': 'United States'}, inplace=True)

    df['Last_Update'] = df['Last_Update'].apply(
        lambda x: (str(x)).split(" ")[0])

    df_map = df.groupby(["Last_Update", "Country_Region"])[['FIPS', 'Last_Update', 'Province_State',
                                                            'Country_Region', 'Confirmed', 'Deaths', 'Recovered']].sum().reset_index()

    confirmed = df_map.groupby(['Last_Update', 'Country_Region']).sum()[
        ['Confirmed']].reset_index()

    latest_date = confirmed['Last_Update'].max()

    map_confirm = confirmed[(confirmed['Last_Update'] == latest_date)][[
        'Country_Region', 'Confirmed']]

    # Getting countries iso for map hover
    countries = {}

    for country in pycountry.countries:
        countries[country.name] = country.alpha_3

    map_confirm["iso_alpha"] = map_confirm["Country_Region"].map(countries.get)

    # Plotly scatter geo guide: https://plot.ly/python/scatter-plots-on-maps/
    plot_map = map_confirm[["iso_alpha", "Confirmed", "Country_Region"]]
    fig = px.scatter_geo(plot_map,
                         locations="iso_alpha",
                         color="Country_Region",
                         hover_name="iso_alpha",
                         size="Confirmed",
                         projection="natural earth", title='Covid-19 Cases')

    return fig


@app.route('/totalcase', methods=['GET'])
def gettotalcase():

    if 'status' in request.args:
        st = request.args['status']

    if st == 'ok':
        response = totalcase()
        graph = response.to_html(full_html=True)
        responsed = render_template('resulttotal.html', div_placeholder=Markup(graph))
        return responsed


@app.route('/worldmap', methods=['GET'])
def getworldmap():

    if 'status' in request.args:
        st = request.args['status']

    if st == 'ok':

        response = mapworld()
        graph = response.to_html(full_html=True)
        responsed = render_template('resultworldmap.html', div_placeholder=Markup(graph))
        print(responsed)
        return responsed


if __name__ == "__main__":
    app.run()

