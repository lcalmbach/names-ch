import streamlit as st 
import first_names
import surnames

__version__ = '0.0.7'
__author__ = 'Lukas Calmbach'
__author_email__ = 'lcalmbach@gmail.com'
VERSION_DATE = '2021-9-28'
my_name = 'Namen Explorer'
my_kuerzel = "NEx"
GIT_REPO = 'https://github.com/lcalmbach/names-ch'
APP_INFO = f"""<div style="background-color:powderblue; padding: 10px;border-radius: 15px;">
    <small>App created by <a href="mailto:{__author_email__}">{__author__}</a><br>
    version: {__version__} ({VERSION_DATE})<br>
    <a href="{GIT_REPO}">git-repo</a>
    """

def main():
    st.set_page_config(
        page_title=my_name,
        layout="wide")
    st.sidebar.markdown(f"## 👫🏽 {my_name}")
    menu_action = st.sidebar.selectbox('Menu',['Vornamen','Nachnamen'])
    if menu_action == 'Vornamen':
        first_names.show_menu()
    elif menu_action == 'Nachnamen':
        surnames.show_menu()
    st.sidebar.markdown(APP_INFO,unsafe_allow_html=True)

if __name__ == '__main__':
    main()
