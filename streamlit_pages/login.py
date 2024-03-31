from streamlit_pages import preferences
import streamlit as st
import pandas as pd
def main():
        
    st.title('App Login')

    api_key = st.text_input("Enter your API key", type="password")
    email = st.text_input("Enter your email")
    app_password = st.text_input("Enter your app password", type="password")

    if api_key and email and app_password:
        st.success('Access granted. Welcome to the app!')
        # Rest of the app goes here

        st.write("You can now use the app.")
        
        df = pd.DataFrame({
        'first column': [1, 2, 3, 4],
        'second column': [10, 20, 30, 40]
        
            })
        st.write(df)
        preferences.main()
    else:
        st.warning('Please enter all the required information to access the app.')
