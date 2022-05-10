import streamlit as st 
import pandas as pd
import streamlit_wordcloud as wordcloud
import altair as alt
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import validators


NAME_FILE = './data/100192.csv'
WIKI_URL_BASE = 'https://de.wikipedia.org/wiki/'
min_year = 0
max_year = 0
gender_dic={'Mädchen': 'W', 'Knaben':'M'}

@st.experimental_memo()
def read_data():
    df = pd.read_csv(NAME_FILE,sep=';')
    df = df[['Jahr','Vorname','Geschlecht','Anzahl']]
    df = df.dropna()
    df = df.rename(columns={'Jahr':'year', 'Vorname': 'text','Geschlecht':'gender','Anzahl':'value'})
    df = df.query("text != 'Übrige'")
    return df

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
        tooltip_data_fields={'text':'Vorname', 'value':'Anzahl', 'rank':'Rang'}, 
        per_word_coloring=False)

def get_genderin_genderax_years(df):
    min_year = df['year'].min()
    max_year = df['year'].max()
    return min_year, max_year


def show_wordcloud(df):
    def show_link(name):            
        url = WIKI_URL_BASE + name
        if verify_url((url)):
            st.markdown(f"Mehr über den Vornamen {name} erfahren auf [Wikipedia]({url})", unsafe_allow_html=True)

    with st.expander('Anleitung'):
        st.markdown("""Wähle das gewünschte Jahr und die Zahl der angezeigten Vornamen in der Grafik aus. Bei > 300 Namen dauert der Prozess ziemlich 
lange. Diese Grafik stellt die Verbreitung der häufigsten Vornamen der Einwohner im Kanton Basel-Stadt als Wordcloud dar. Häufige Namen 
erscheinen in Grossbuchstaben und im Zentrum der Grafik. Wenn du auf einen Vornamen klickst, so erscheint unterhalb der Grafik ein Link auf die entsprechende 
Wikipedia Seite mit mehr Informationen zum Vornamen.""")
    years = range(min_year, max_year+1)
    jahr = st.sidebar.selectbox('Jahr', options = years, index = len(years)-1)
    threshold = st.sidebar.number_input('Limite für Anzahl angezeigte Namen', min_value=1,max_value=1000, value=200)
    if threshold > 200:
        st.info('Diese Abfrage dauert etwas länger, habe etwas Geduld...')
    st.markdown('### Vornamen von Knaben in Basel-Stadt')
    filter_exp = f"year == {jahr} & gender == 'M'"
    df_gender = filter_data(df, filter_exp).sort_values(by='value',ascending=[False])
    df_ranked_gender = rank_data(df_gender)
    df_ranked_gender = df_ranked_gender.query('rank <= @threshold')
    wc = create_word_list(df_ranked_gender)
    try:
        show_link(wc['clicked']['text'])
    except:
        pass

    filter_exp = f"year == {jahr} & gender == 'W'"
    df_gender = filter_data(df,filter_exp).sort_values(by='value',ascending=[False])
    df_ranked_gender = rank_data(df_gender)
    df_ranked_gender = df_ranked_gender.query('rank <= @threshold')
    st.markdown('### Vornamen von Mädchen in Basel-Stadt')
    wc = create_word_list(df_ranked_gender)
    try:
        show_link(wc['clicked']['text'])
    except:
        pass
    

def get_timeseries(df, settings):
    if 'color' in settings:
        chart = alt.Chart(df, title = settings['title']).mark_line(point=True).encode(
            x=alt.X('year:Q', axis=alt.Axis(title='Jahr', format='N')),
            y=settings['y'],
            color = alt.Color('text:N', legend=alt.Legend(title="Vornamen")),
            tooltip=['year','text','value','rank']
        ).properties(width=settings['width'], height=settings['height'])
    else:
        chart = alt.Chart(df, title = settings['title']).mark_line(point=True).encode(
            x=alt.X('year:Q', axis=alt.Axis(title='Jahr', format='N')),
            y=settings['y'],
            tooltip=['year','text','value','rank']
        ).properties(width=settings['width'], height=settings['height'])

    return chart

def show_timeseries(df):    
    with st.expander('Anleitung'):
        st.markdown('Wähle das Geschlecht des Kindes sowie den oder die Vornamen, deren Häufigkeit und Rang als Zeitreihe dargestellt werden sollen' )
    gender = st.sidebar.selectbox('Geschlecht', options = list(gender_dic.keys()))
    sort_by_options= ['nach Rang','Alphabetisch']
    sort_by = st.sidebar.radio('Sortiere Vornamen', sort_by_options)
    filter_exp = f"gender == '{gender_dic[gender]}' & text != 'Übrige'"
    df = filter_data(df,filter_exp).sort_values(by='text')
    df = rank_data(df)
    if sort_by == sort_by_options[0]:
        df = df.sort_values(by='rank')
    else:    
        df = df.sort_values(by='text')
    lst_names = df['text'].unique()
    names = st.sidebar.multiselect('Vornamen', lst_names, lst_names[:3])
    filter_exp = f"text.isin({names})"
    df = filter_data(df,filter_exp)

    settings = {'width':500, 'height':300}
    settings['y'] = alt.Y('value:Q', axis=alt.Axis(title='Anzahl'))
    settings['title'] =  f'Anzahl des Vornamens'
    settings['color'] = 'text'
    chart = get_timeseries(df, settings)
    st.altair_chart(chart)

    settings['y'] = alt.Y('rank:Q', axis=alt.Axis(title='Rang'))
    settings['title'] =  f'Rang des Vornamens'
    chart = get_timeseries(df, settings)
    st.altair_chart(chart)
    

def show_table(df):
    def aggregate_df(df):
        df_agg = df.groupby(df['text']).value.agg(['min','max','mean']).reset_index()      
        return df_agg

    with st.expander('Anleitung'):
        st.markdown('Wähle Geschlecht und Namen aus, die du auswerten möchtest' )
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

def show_ranking(df):
    years_options = list(df['year'].unique())
    years_options = [int(x) for x in years_options]
    years_options.sort(reverse=True)
    sel_year = st.sidebar.selectbox('Jahr', options=years_options)
    cutoff= st.sidebar.slider('Show Top',min_value=10, max_value=100)
    df['year'] = df['year'].astype("int")
    df = df[df['year'] == sel_year]
    boys = df[df['gender'] == 'M']
    boys = rank_data(boys).sort_values('rank')
    boys = boys[:cutoff]
    girls= df[df['gender'] == 'W']
    girls = rank_data(girls).sort_values('rank')
    girls = girls[:cutoff]

    st.markdown(f"### {sel_year}")
    cols = st.columns(2)
    chart_boys = plot_rank(boys)
    chart_girls = plot_rank(girls)
    with cols[0]:
        st.markdown('#### Knaben')
        st.altair_chart(chart_boys)
    with cols[1]:
        st.markdown('#### Mädchen')
        st.altair_chart(chart_girls)


def plot_rank(df):
    df.columns=['Jahr','Name','Geschlecht','Anzahl','Rang']
    
    h=0 if len(df)<16 else (len(df)-15)*6
    chart = alt.Chart(df).mark_bar().encode(
        x="Anzahl:Q",
        y=alt.Y('Name:N', sort='-x'),
        tooltip=['Name', 'Rang']
    ).properties(width=400, height=500 + h)
    return chart


def show_analysis(df):
    def get_description(df,name):
        df_name_ob_rank = df.query('text == @name').sort_values('rank')
        df_name_ob_year = df.query('text == @name').sort_values('year')
        # min max mean over years where name has occured
        df_agg_value = df_name_ob_rank.groupby(df_name_ob_rank['text']).value.agg(['min','max','mean', 'count']).reset_index()                 
        # first and last year for name occurrence
        df_agg_year = df_name_ob_rank.groupby(df_name_ob_rank['text']).year.agg(['min','max'])
        last_year = df_agg_year.iloc[0]['max']
        df_year = df.query('year == @last_year').sort_values('rank').copy().reset_index()
        num_children = len(df_year)
        record = get_record(df_year, name, last_year)
        rank = record.iloc[0]['rank']
        rank_start = int(df_name_ob_year.iloc[0]['rank'])
        max_rank = df.query('year == @last_year')['rank'].max()
        index = (record.index).astype(int)

        if index > 0:
            name_before = df_year.iloc[index - 1].iloc[0]['text']
        if index < len(df_year) -1:
            name_after = df_year.iloc[index + 1].iloc[0]['text']
        
        first_year_count = df[ (df['year'] == df_agg_year.iloc[0]['min']) & (df['text'] == name) ].iloc[0]['value']
        gender_plur = 'Mädchen' if gender == 'Weiblich' else 'Knaben'
        diff_tot = record.iloc[0]['value'] - first_year_count 
        text = f"""Im Jahr {last_year} wurden {num_children} {gender_plur} geboren, und {record.iloc[0]['value']} erhielten den Vornamen 
        {name}. {name} steht damit auf Rang {int(rank)}"""
        
        if rank == 1:
            text += f", dies ist somit der beliebteste {gender_plur}-Vorname in Basel-Stadt!"
        elif (rank > 1) & (rank < max_rank - 50):
            text += f" hinter {name_before} und vor {name_after}"
        else:
            text += f", er gehört damit zu den eher selteneren Vornamen in Basel-Stadt"
        if diff_tot > 0:
            text += f". Seit dem ersten Auftreten im Jahr {df_agg_year.iloc[0]['min']} ist die Anzahl Personen mit diesem Vornamen um {diff_tot} gestiegen."  
        elif diff_tot < 0:
            text += f". Seit dem ersten Auftreten im Jahr {df_agg_year.iloc[0]['min']} ist Anzahl Personen mit diesem Vornamen um {diff_tot} gesunken."
        else: 
            text += f". Die Zahl der Personen mit diesem Vornamen ist wieder identisch mit derjenigen von {df_agg_year.iloc[0]['min']}."
        if diff_tot != 0:
            text += f" Damals hatte {name} den Rang {rank_start}. Informationen zu den Vornamen von Neugeborenen schweizweit findest du unter [bfs.admin.ch](https://www.bfs.admin.ch/bfs/de/home/statistiken/bevoelkerung/geburten-todesfaelle/vornamen-neugeborene.html)."
        text += f""" Weitere Informationen zum Vornamen {name} findest du auf [Wikipedia]({WIKI_URL_BASE}{name}). Hier gehts zum Datensatz auf [Datenportal 
        Basel-Stadt](https://data.bs.ch/explore/dataset/100192)."""

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

    gender = st.sidebar.selectbox('Geschlecht', options = ['Weiblich', 'Männlich'])
    filter_exp = f"gender == '{gender[0]}'"
    df_gender = df.query(filter_exp).sort_values('text')
    df_ranked = rank_data(df_gender)
    lst_names = list(df_ranked['text'].unique())
    name = st.sidebar.selectbox('Vornamen', lst_names)
    
    ts_df = prepare_timeseries_df(df_ranked, name)
    last_year = ts_df['year'].max()
    with st.expander('Anleitung'):
        beginn_datenreihe = df_ranked['year'].min()
        st.markdown(f"""Wähle Geschlecht und einen Vornamen aus, über den du mehr erfahren möchtest. Die Zeitreihe der Anzahl und Rang des Namens seit Beginn der Datenreihe in {beginn_datenreihe} vermittelt einen Eindruck, wie viele Kinder in Basel 
        über die Jahre diesen Vornamen erhielten.""" )
    st.markdown(f"### Beliebtheit des Vornamens *{name}* in Basel-Stadt")
    
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

    df = read_data()#.copy()
    min_year, max_year = get_genderin_genderax_years(df)
    menu_options= ['Wort-Wolke','Zeitreihe', 'Rang-Reihenfolge', 'Analyse','Tabelle']
    menu_action = st.sidebar.selectbox("Darstellung",options=menu_options)
    if menu_action == menu_options[0]:
        show_wordcloud(df)
    elif menu_action == menu_options[1]:
        show_timeseries(df)
    elif menu_action == menu_options[2]:
        show_ranking(df)
    elif menu_action == menu_options[3]:
        show_analysis(df)
    elif menu_action == menu_options[4]:
        show_table(df)

