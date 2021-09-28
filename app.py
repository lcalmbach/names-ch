from altair.vegalite.v4.schema.core import Align
import streamlit as st 
from streamlit_lottie import st_lottie
import first_names
import surnames
import requests

__version__ = '0.0.7'
__author__ = 'Lukas Calmbach'
__author_email__ = 'lcalmbach@gmail.com'
VERSION_DATE = '2021-9-28'
my_name = 'Namen Explorer'
my_kuerzel = "NEx"
SOURCE_URL = 'https://data.bs.ch/explore/dataset/100129'
GIT_REPO = 'https://github.com/lcalmbach/names-ch'
APP_INFO = f"""<div style="background-color:powderblue; padding: 10px;border-radius: 15px;">
    <small>App created by <a href="mailto:{__author_email__}">{__author__}</a><br>
    version: {__version__} ({VERSION_DATE})<br>
    source:<a href="{SOURCE_URL}">Statistisches Amt Basel-Stadt</a><br>
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
        st_lottie(lottie_search_names,height=80, loop=False)
    else:
        st.write(123)
    st.sidebar.markdown(f"## 👫🏽 {my_name}")
    menu_action = st.sidebar.selectbox('Menu',['Vornamen','Nachnamen'])
    if menu_action == 'Vornamen':
        first_names.show_menu()
    elif menu_action == 'Nachnamen':
        surnames.show_menu()
    st.sidebar.markdown(APP_INFO,unsafe_allow_html=True)

if __name__ == '__main__':
    main()
