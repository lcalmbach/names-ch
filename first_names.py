import streamlit as st 
import pandas as pd
import streamlit_wordcloud as wordcloud
import altair as alt
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import validators


NAME_FILE = './data/100129.csv'
WIKI_URL_BASE = 'https://de.wikipedia.org/wiki/'
min_year = 0
max_year = 0

@st.experimental_memo()
def read_data():
    df = pd.read_csv(NAME_FILE,sep=';')
    df = df[['Jahr','Vorname','Geschlecht','Anzahl']]
    df = df.dropna()
    df = df.rename(columns={'Jahr':'year', 'Vorname': 'text','Geschlecht':'gender','Anzahl':'value'})
    return df

def filter_data(df, filter_exp):
    df_filtered = df.query(filter_exp)
    return df_filtered

def verify_url(url):
    return validators.url(url)

def rank_data(df, threshold):
    df_ranked = df
    df_ranked['rank'] = df['value'].rank(ascending=False)
    df_ranked = df_ranked.query('rank <= @threshold')
    return df_ranked

def create_word_list(df):
    names = []
    for index, row in df.iterrows():
        names.append({ 'text': row['text'], 'value': row['value'], 'rank': row['rank'] })
    
    return wordcloud.visualize(names, 
        tooltip_data_fields={'text':'Vorname', 'value':'Anzahl', 'rank':'Rang'}, 
        per_word_coloring=False)

def get_min_max_years(df):
    min_year = df['year'].min()
    max_year = df['year'].max()
    return min_year, max_year


def show_wordcloud(df):
    def show_link(name):            
        url = WIKI_URL_BASE + name
        if verify_url((url)):
            st.markdown(f"Mehr über den Vornamen {name} erfahren auf [Wikipedia]({url})", unsafe_allow_html=True)

    with st.expander('Anleitung'):
        st.write("""Wähle das gewünschte Jahr und die Zahl der angezeigten Vornamen in der Grafik aus. Bei > 300 Namen dauert der Prozess ziemlich 
lange. Diese Grafik stellt die Verbreitung der häufigsten Vornamen der Einwohner im Kanton Basel-Stadt als Wordcloud dar. Häufige Namen 
erscheinen in Grossbuchstaben und im Zentrum der Grafik. Wenn du auf einen Vornamen klickst, so erscheint unterhalb der Grafik ein Link auf die entsprechende 
Wikipedia Seite mit mehr Informationen zum Vornamen.""")
    years = range(min_year, max_year+1)
    jahr = st.sidebar.selectbox('Jahr', options = years, index = len(years)-1)
    threshold = st.sidebar.number_input('Limite für Anzahl angezeigte Namen', min_value=1,max_value=1000, value=200)
    if threshold > 200:
        st.info('Diese Abfrage dauert etwas länger, habe etwas Geduld...')
    st.markdown('### Vornamen Männer')
    filter_exp = f"year == {jahr} & gender == 'M' & text != 'Übrige' & text"
    df_m = filter_data(df, filter_exp).sort_values(by='value',ascending=[False])
    df_ranked_m = rank_data(df_m, threshold)
    wc = create_word_list(df_ranked_m)
    try:
        show_link(wc['clicked']['text'])
    except:
        pass
    filter_exp = f"year == {jahr} & gender == 'W' & text != 'Übrige'"
    df_m = filter_data(df,filter_exp).sort_values(by='value',ascending=[False])
    df_ranked_f = rank_data(df_m, threshold)
    st.markdown('### Vornamen Frauen')
    wc = create_word_list(df_ranked_f)
    try:
        show_link(wc['clicked']['text'])
    except:
        pass
    

def show_timeseries(df):
    def get_timeseries(df, title):
        chart = alt.Chart(df, title = title).mark_line().encode(
            x=alt.X('year:Q', axis=alt.Axis(title='Jahr',format='N')),
            y=alt.Y('value:Q', axis=alt.Axis(title='Anzahl')),
            color = alt.Color('text:N', legend=alt.Legend(title="Vornamen")),
            tooltip=['year','text','value']
        ).properties(width=800,height=400)
        return chart
            
    with st.expander('Anleitung'):
        st.write('Wähle das Geschlecht sowie die Vornamen, deren Häufigkeit als Zeitreihe dargestellt werden sollen' )
    gender = st.sidebar.selectbox('Geschlecht', options = ['Weiblich', 'Männlich'])
    filter_exp = f"gender == '{gender[0]}' & text != 'Übrige'"
    df = filter_data(df,filter_exp).sort_values(by='text')
    lst_names = df['text'].unique()
    names = st.sidebar.multiselect('Vornamen',lst_names,[lst_names[0],lst_names[1],lst_names[2]])
    filter_exp = f"text.isin({names})"
    df = filter_data(df,filter_exp).sort_values(by='text')
    st.altair_chart(get_timeseries(df, f'Vornamen {gender}'))
    

def show_table(df):
    def aggregate_df(df):
        df_agg = df.groupby(df['text']).value.agg(['min','max','mean']).reset_index()      
        return df_agg

    with st.expander('Anleitung'):
        st.write('Wähle Geschlecht und Namen aus, die du auswerten möchtest' )
    gender = st.sidebar.selectbox('Geschlecht', options = ['Weiblich', 'Männlich'])
    filter_exp = f"gender == '{gender[0]}' & text != 'Übrige'"
    df = filter_data(df,filter_exp).sort_values(by='text')
    lst_names = df['text'].unique()
    names = st.sidebar.multiselect('Vornamen',lst_names,[lst_names[0],lst_names[1],lst_names[2]])
    filter_exp = f"text.isin({names})"
    df = filter_data(df,filter_exp).sort_values(by='text')

    st.markdown("### Häufigkeit der ausgewählten Vornamen")
    df_agg = aggregate_df(df)
    df_agg.columns=['Vorname','Min','Max', 'Durchschnitt']
    AgGrid(df_agg)

    st.markdown("### Ausgewählte Vornamen nach Jahr")
    df = df[['year','text','value']].sort_values(by=['text','year'])
    df.columns=['Jahr','Vorname','Anzahl']
    AgGrid(df)
    

def show_menu():
    global min_year
    global max_year

    df = read_data()#.copy()
    min_year, max_year = get_min_max_years(df)
    menu_action = st.sidebar.selectbox("Darstellung",['Wordcloud','Zeitreihe', 'Tabelle'])
    if menu_action == 'Wordcloud':
        show_wordcloud(df)
    elif menu_action == 'Zeitreihe':
        show_timeseries(df)
    elif menu_action == 'Tabelle':
        show_table(df)

