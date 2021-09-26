# names-ch
## Introduction
names-ch is built on the opendata dataset [Vornamen der baselstädtischen Bevölkerung](https://data.bs.ch/explore/dataset/100129) and displays first names filtered by year since 1979 as a wordcloud chart or as time series. I plan the integration of names from other cantons if similar datasets are available.

## Programming and Framworks
delphi-bs is written in Python and uses the frameworks Streamlit and Altair. The wordcloud is generated using the stramlit compontent [streamlit-wordcloud](https://github.com/rezaho/streamlit-wordcloud). The app can be opened [here](https://names-ch.herokuapp.com/)

## Installation
In order to install the app on your machine.
1. Clone this repo
1. Create a virtual env, e.g. on Windows:
    ```
    > python -m venv .venv
    ```
1. Activate the virtual env:
    ```
    > env\scripts\activate
    ```
1. Install the dependencies 
    ```
    > pip intall -r requirements.txt
    ```
1. Start the app
    ```
    > streamlit run app.py
    ```
1. The app should open in your browser on http://localhost:8501/
