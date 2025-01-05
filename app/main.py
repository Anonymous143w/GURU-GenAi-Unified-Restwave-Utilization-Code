import streamlit as st
from components.chat_interface import GURUInterface

def main():
    if 'interface' not in st.session_state:
        st.session_state.interface = GURUInterface()
    st.session_state.interface.setup_interface()

if __name__ == "__main__":
    main()