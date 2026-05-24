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
    note = "✅ Successful information note ..."
    with st.container():
        st.markdown(
            f"""
            <div style=" border-radius: 6px; padding: 4px;
                background-color: #f5f7fa;
                text-align: left; border: 1px solid #e0e0e0;
            ">
                <h1 style="font-size: 18px; color: #4CAF50">{note}</h1>
                <h1 style="font-size: 12px; color: ##afac4c">{message}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )
    # Empty line for better spacing and readability in case of multiple wigets.
    st.markdown(f" ")

def error_message(e, message : str):

    with st.container():
        note = "❌ Faillure information note ..."
        st.error(f"The following Error occured when handelling Pdf!\nError : {e}")
        st.markdown(
            f"""
            <div style="
                padding:20px;
                border-radius:12px;
                background:#f9fafc;
                border:1px solid #e6e6e6;
            ">
            <h1 style="font-size: 14px; color: #4CAF50">{note}</h1>
            <h3 style="margin-top:0;">📄 {message}</h3>
            <ul>
                <li style="color:red"><b>Supported formats:</b> PDF (.pdf) or text files (.txt)</li>
                <li style="color:red"><b>Readable content:</b> Ensure the document contains selectable text</li>
                <li><b>Clear structure:</b> Headings and paragraphs improve answers</li>
                <li><b>Relevant content:</b> Upload meaningful information</li>
                <li><b>Reasonable size:</b> Large files may take longer</li>
            </ul>
            <p style="color:#555;"><i>💡 Tip: Better structure = better answers</i></p>
            </div>
            """,
            unsafe_allow_html=True
        )