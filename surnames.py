import streamlit as st 
import pandas as pd
import streamlit_wordcloud as wordcloud
import altair as alt
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import validators


NAME_FILE = './data/100127.csv'
WIKI_URL_BASE = 'https://de.wikipedia.org/wiki/'
min_year = 0
max_year = 0

@st.experimental_memo()
def read_data():
    df = pd.read_csv(NAME_FILE,sep=';')
    df = df[['Jahr','Nachname','Anzahl']]
    df = df.dropna()
    df = df.rename(columns={'Jahr':'year', 'Nachname': 'text','Anzahl':'value'})
    df = df.query("text != 'übrige'")
    return df


def get_record(df, name: str, year: int):
    """
    Finds rank of name and then return a dataframe where 3 names above and 170 below are shown, so the name is viisalbe in the wordcloud
    """
    filter_exp = "text == @name & year == @year"
    df_last_occurrence = df.query(filter_exp)
    return df_last_occurrence


def filter_data(df, filter_exp):
    df_filtered = df.query(filter_exp)
    return df_filtered

def verify_url(url):
    return validators.url(url)


def rank_data(df):
    df_ranked = df
    df_ranked['rank'] = df.groupby('year')["value"].rank("max",ascending=False)
    return df_ranked

def create_word_list(df):
    names = []
    for index, row in df.iterrows():
        names.append({ 'text': row['text'], 'value': row['value'], 'rank': row['rank'] })
    
    return wordcloud.visualize(names, 
        tooltip_data_fields={'text':'Nachname', 'value':'Anzahl', 'rank':'Rang'}, 
        per_word_coloring=False)

def get_min_max_years(df):
    min_year = df['year'].min()
    max_year = df['year'].max()
    return min_year, max_year


def show_wordcloud(df):
    def show_link(name):            
        url = WIKI_URL_BASE + name
        if verify_url((url)):
            st.markdown(f"Mehr über den Nachnamen {name} erfahren auf [Wikipedia]({url})", unsafe_allow_html=True)

    with st.expander('Anleitung'):
        st.write("""Wähle das gewünschte Jahr und die Zahl der angezeigten Nachnamen in der Grafik aus. Bei > 300 Namen dauert der Prozess ziemlich 
lange. Diese Grafik stellt die Verbreitung der häufigsten Nachnamen der Einwohner im Kanton Basel-Stadt als Wordcloud dar. Häufige Namen 
erscheinen in Grossbuchstaben und im Zentrum der Grafik. Wenn du auf einen Nachnamen klickst, so erscheint unterhalb der Grafik ein Link auf die entsprechende 
Wikipedia Seite mit mehr Informationen zum Nachnamen.""")
    years = range(min_year, max_year+1)
    jahr = st.sidebar.selectbox('Jahr', options = years, index = len(years)-1)
    threshold = st.sidebar.number_input('Limite für Anzahl angezeigte Namen', min_value=1,max_value=1000, value=200)
    if threshold > 200:
        st.info('Diese Abfrage dauert etwas länger, habe etwas Geduld...')
    st.markdown('### Nachnamen')
    filter_exp = f"year == {jahr}"
    df = filter_data(df, filter_exp).sort_values(by='value',ascending=[False])
    df_ranked = rank_data(df)
    df_ranked = df_ranked.query('rank <= @threshold')
    wc = create_word_list(df_ranked)
    try:
        show_link(wc['clicked']['text'])
    except:
        pass
    

def get_timeseries(df, settings):
    if 'color' in settings:
        chart = alt.Chart(df, title = settings['title']).mark_line().encode(
            x=alt.X('year:Q', axis=alt.Axis(title='Jahr',format='N')),
            y=settings['y'],
            color = alt.Color('text:N', legend=alt.Legend(title="Nachname")),
            tooltip=['year','text','value','rank']
        ).properties(width=settings['width'],height=settings['height'])
    else:
        chart = alt.Chart(df, title = settings['title']).mark_line().encode(
            x=alt.X('year:Q', axis=alt.Axis(title='Jahr',format='N')),
            y=settings['y'],
            tooltip=['year','text','value','rank']
        ).properties(width=settings['width'],height=settings['height'])

    return chart


def show_timeseries(df):
    with st.expander('Anleitung'):
        st.write('Wähle die Nachnamen, deren Häufigkeit als Zeitreihe dargestellt werden sollen' )
    df = rank_data(df).sort_values(by='text')
    lst_names = df['text'].unique()
    names = st.sidebar.multiselect('Nachnamen',lst_names,[lst_names[0],lst_names[1],lst_names[2]])
    filter_exp = f"text.isin({names})"
    df = filter_data(df,filter_exp).sort_values(by='text')
    settings = {'width':700, 'height':300}
    settings['y'] = alt.Y('value:Q', axis=alt.Axis(title='Anzahl'))
    settings['title'] =  f'Anzahl der Nachnamen'
    settings['color'] = 'text'
    st.altair_chart(get_timeseries(df, settings))

    settings['y'] = alt.Y('rank:Q', axis=alt.Axis(title='Rang'))
    settings['title'] =  f'Rang der Nachnamen'
    st.altair_chart(get_timeseries(df, settings))
    

def show_table(df):
    def aggregate_df(df):
        df_agg = df.groupby(df['text']).value.agg(['min','max','mean']).reset_index()      
        return df_agg

    with st.expander('Anleitung'):
        st.write('Wähle Namen aus, die du auswerten möchtest' )
    filter_exp = f"text != 'übrige'"
    df = filter_data(df,filter_exp).sort_values(by='text')
    lst_names = df['text'].unique()
    names = st.sidebar.multiselect('Nachnamen',lst_names,[lst_names[0],lst_names[1],lst_names[2]])
    filter_exp = f"text.isin({names})"
    df = filter_data(df,filter_exp).sort_values(by='text')

    st.markdown("### Häufigkeit der ausgewählten Nachnamen")
    df_agg = aggregate_df(df)
    df_agg.columns=['Nachname','Min','Max', 'Durchschnitt']
    AgGrid(df_agg)

    st.markdown("### Ausgewählte Nachnamen nach Jahr")
    df = df[['year','text','value']].sort_values(by=['text','year'])
    df.columns=['Jahr','Nachname','Anzahl']
    AgGrid(df)
    
def show_analysis(df):
    def get_description(df,name):
        df_name = df.query('text == @name').sort_values('rank')
        # min max mean over years where name has occured
        df_agg_value = df_name.groupby(df_name['text']).value.agg(['min','max','mean', 'count']).reset_index()                 
        # first and last year for name occurrence
        df_agg_year = df_name.groupby(df_name['text']).year.agg(['min','max'])
        last_year = df_agg_year.iloc[0]['max']
        df_year = df.query('year == @last_year').sort_values('rank').copy().reset_index()
        record = get_record(df_year, name, last_year)
        rank = record.iloc[0]['rank']
        rank_start = int(df_name.iloc[-1]['rank'])
        max_rank = df.query('year == @last_year')['rank'].max()
        index = (record.index).astype(int)

        if index > 0:
            name_before = df_year.iloc[index - 1].iloc[0]['text']
        if index < len(df_year) -1:
            name_after = df_year.iloc[index + 1].iloc[0]['text']
        
        first_year_count = df[ (df['year'] == df_agg_year.iloc[0]['min']) & (df['text'] == name) ].iloc[0]['value']
        diff_tot = record.iloc[0]['value'] - first_year_count 
        text = f"Im Jahr {last_year} gab es {record.iloc[0]['value']} Personen mit dem Nachnamen {name}, dieser steht damit auf Rang {int(rank)}"
        if rank == 1:
            text += f", dies ist somit der beliebteste Nachname in Basel-Stadt"
        elif (rank > 1) & (rank < max_rank):
            text += f" hinter {name_before} und vor {name_after}"
        else:
            text += f", er gehört damit zu den eher selteneren Namen in Basel-Stadt"
        
        if diff_tot > 0:
            text += f". Seit dem ersten Auftreten im Jahr {df_agg_year.iloc[0]['min']} ist die Anzahl Personen mit diesem Nachnamen um {diff_tot} gestiegen."  
        elif diff_tot < 0:
            text += f". Seit dem ersten Auftreten im Jahr {df_agg_year.iloc[0]['min']} ist Anzahl Personen mit diesem Nachnamen um {diff_tot} gesunken."
        else: 
            text += f". Die Zahl der Personen mit diesem Nachnamen ist wieder identisch mit derjenigen von {df_agg_year.iloc[0]['min']}."

        text += f" Damals hatte {name} den Rang {rank_start}.  Weitere Informationen zum Nachnamen {name} findest du auf [Wikipedia]({WIKI_URL_BASE}{name})."

        return text

    def get_record(df, name: str, year: int):
        """
        Finds rank of name and then return a dataframe where 3 names above and 170 below are shown, so the name is viisalbe in the wordcloud
        """
        filter_exp = "text == @name & year == @year"
        df_last_occurrence = df.query(filter_exp)
        return df_last_occurrence


    def prepare_timeseries_df(df_gender, name):
        df_years = df_gender.query('text == @name')
        return df_years

    df_ranked = rank_data(df).sort_values('text')
    lst_names = list(df_ranked['text'].unique())
    name = st.sidebar.selectbox('Vornamen', lst_names)
    
    ts_df = prepare_timeseries_df(df_ranked, name)
    last_year = ts_df['year'].max()
    with st.expander('Anleitung'):
        st.write("""Wähle Geschlecht und einen Vornamen aus, über den du mehr erfahren möchtest. Die Zeitreihe der Anzahl und Rang des Namens seit Beginn der Datenreihe in 1979 vermittelt einen Eindruck, wie viele Personen 
über die Jahre diesen Namen trugen.""" )
    st.markdown(f"### Beliebtheit des Vornamens *{name}* in Basel-Stadt im Jahr {last_year}")
    
    col1, col2 = st.columns(2)
    settings = {'width':400, 'height':250}
    with col1:
        settings['y'] = alt.Y('value:Q', axis=alt.Axis(title='Anzahl'))
        settings['title'] =  f'Anzahl {name}'
        chart = get_timeseries(ts_df, settings)
        st.altair_chart(chart)
    
    with col2:
        settings['y'] = alt.Y('rank:Q', axis=alt.Axis(title='Rang'))
        settings['title'] =  f'Rang von {name}'
        chart = get_timeseries(ts_df, settings)
        st.altair_chart(chart)
    
    st.markdown(get_description(df_ranked,name))

def show_menu():
    global min_year
    global max_year

    df = read_data()
    min_year, max_year = get_min_max_years(df)
    menu_action = st.sidebar.selectbox("Darstellung",['Wort-Wolke','Zeitreihe', 'Analyse','Tabelle'])
    if menu_action == 'Wort-Wolke':
        show_wordcloud(df)
    elif menu_action == 'Zeitreihe':
        show_timeseries(df)
    elif menu_action == 'Analyse':
        show_analysis(df)
    elif menu_action == 'Tabelle':
        show_table(df)

