from altair.vegalite.v4.schema.core import Align
import streamlit as st 
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import first_names
import surnames
import newborns
import requests

__version__ = '0.1.0'
__author__ = 'Lukas Calmbach'
__author_email__ = 'lcalmbach@gmail.com'
VERSION_DATE = '2022-05-11'
my_name = 'Namen Explorer Basel-Stadt'
my_kuerzel = "NEx"
SOURCE_URL = 'https://data.bs.ch/pages/home/'
GIT_REPO = 'https://github.com/lcalmbach/names-ch'
APP_INFO = f"""<div style="background-color:powderblue; padding: 10px;border-radius: 15px;">
    <small>App created by <a href="mailto:{__author_email__}">{__author__}</a><br>
    version: {__version__} ({VERSION_DATE})<br>
    source: <a href="{SOURCE_URL}">Datenportal Basel-Stadt</a>
    <br><a href="{GIT_REPO}">git-repo</a>
    """

@st.experimental_memo()
def get_lottie():
    ok=True
    r=''
    try:
        r = requests.get('https://assets5.lottiefiles.com/packages/lf20_co3tq7q4.json').json()
    except:
        ok = False
    return r,ok
    
    
def main():
    st.set_page_config(
        page_title=my_name,
        layout="wide")
    
    lottie_search_names,ok = get_lottie()
    if ok:
        with st.sidebar:
            st_lottie(lottie_search_names,height=80, loop=False)
    else:
        pass
    
    menu_options = ['Vornamen','Nachnamen', 'Neugeborene']
    with st.sidebar:
        st.markdown(f"## 👫🏽 {my_name}")
        menu_action = option_menu(None, menu_options, 
            icons=['person', 'person-plus', "person-x"], 
            menu_icon="cast", default_index=0)

    if menu_action == menu_options[0]:
        first_names.show_menu()
    elif menu_action == menu_options[1]:
        surnames.show_menu()
    elif menu_action == menu_options[2]:
        newborns.show_menu()
    
    st.sidebar.markdown(APP_INFO, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
