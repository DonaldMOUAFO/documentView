import streamlit as st

def app_header():
    
    st.set_page_config(
        page_title="DocumentView", 
        page_icon="# :blue[:material/local_library:]", 
        layout="wide"
    )
    with st.container():
        col1, col2 = st.columns([3, 5])
        with col1:
            st.markdown("<div style='margin-bottom:-175px;'></div>", unsafe_allow_html=True)
            st.markdown("# :blue[:material/local_library:]DocumentView") 
      
        with col2:
            pass 

def app_header_side(text):
   
    st.set_page_config(
        page_title="DocumentView", 
        page_icon="# :blue[:material/local_library:]", 
        layout="wide"
    )
    with st.container():
        st.markdown("<div style='margin-bottom:0px;'></div>", unsafe_allow_html=True)
        st.markdown("# :blue[:material/local_library:]DocumentView") 
        st.markdown(f"{text}") 
            
def inform_message(message : str):
    with st.container():
        st.markdown(
            f"""
            <div style=" border-radius: 12px; padding: 30px;
                background-color: #f5f7fa;
                text-align: center; border: 1px solid #e0e0e0;
            ">
                <h1 style="font-size: 18; color: #4CAF50">{message}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )