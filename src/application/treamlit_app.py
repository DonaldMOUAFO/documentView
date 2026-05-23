import streamlit as st
from os import path
from src.infrastructure import config, prompt_engineering
from src.interface.streamlit_app import app_header, app_header_side
from src.domain.document_handler import chunk_text_recursive, load_corpus, load_document, save_corpus
from src.domain.embeddings import load_model, compute_embeddings, load_embeddings, save_embeddings
from src.domain.vector_search import build_hnsw_index, load_index, save_index
import warnings

app_header()
st.markdown(
    "#### :blue[:material/local_library:]*Questionne your document ...*<br> ", 
    unsafe_allow_html=True,
    text_alignment="right"
)

with st.sidebar:
    app_header_side(
        "The easiest way to ask question to your document..."
    )

    Llm_model_used = st.chat_input(
        f"Precise the Llm model to use.\nDefault : {config.EMBEDINGS_MODEL_NAME}"
    )

    uploaded_file = st.file_uploader(
        label = "Upload the document to interact with",
        type = ["txt", "pdf"],
        accept_multiple_files = False ,
    )

    if uploaded_file is not None :
        st.markdown(
            """
            <div style="text-align: left; padding: 1px 3px;">
                <h1 style="font-size: 18px; color: #4CAF50">
                    📄  Document uploaded successfully... 
                    <p style="style="text-align: center; font-size: 13px; color: gray;">
                        As any question to your document.
                    </p>
                </h1>
                
            </div>
            """,
            unsafe_allow_html=True
        )
        
question = st.chat_input("As any question to your document ...")

while question :

    if uploaded_file is None : 
        with st.container():
           st.markdown(
                """
                <div style=" border-radius: 12px; padding: 30px;
                    background-color: #f5f7fa;
                    text-align: center; border: 1px solid #e0e0e0;
                ">
                    <h1 style="font-size: 42px; color: #4CAF50">📄  Upload a document to start interacting</h1>
                    <p style="font-size: 18px; color: gray;">
                        Upload a PDF or text file and start asking questions instantly.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
    else  :
        embs_file_path = config.prepare_file_path(
            uploaded_file.name, "emb"
        )
        # To save the chunked text and the metadata in the corpus directory.
        corpus_file_path = config.prepare_file_path(
            uploaded_file.name, "corpus"
        )

        model = load_model(config.EMBEDINGS_MODEL_NAME)

        if path.isfile(embs_file_path) :
            embeddings = load_embeddings(
                emb_file_path = embs_file_path
            )
            chunked_text, doc_meta = load_corpus(
                corpus_file_path=corpus_file_path
            )
        else :
            if path.isfile(corpus_file_path) :
                chunked_text, doc_meta = load_corpus(
                    corpus_file_path=corpus_file_path
                )
                
            else :
                # Read file as string and extract the text content and the metadata as a dict.
                text_data_dict, doc_meta = load_document(uploaded_file)  

                # chunked_text is a list of dist. with "text" and "metadata" keys. 
                # text is a string containing a single chunk.
                # Metadata is a dict including the following keys which each value is a string
                # (source, page, chunk_id, type, title, author, creator, producer, modification_date, creation_date).
                chunked_text, doc_meta = chunk_text_recursive(text_data_dict, doc_meta)
                save_corpus(doc_meta, corpus_file_path=corpus_file_path)

                embeddings = compute_embeddings(chunks=chunked_text, model=model)
                save_embeddings(embeddings, embs_file_path)

        st.session_state.chunked_text = chunked_text
        st.session_state.doc_meta = doc_meta

        if embeddings is None:
            uploaded_file = None
            question = None
            continue

        if "index" not in st.session_state :
            index_file_path = config.prepare_file_path(
                uploaded_file.name, "index"
            )
            
            if path.isfile(index_file_path) :
                index = load_index(index_path=index_file_path)
            else :
                index = build_hnsw_index(embeddings=embeddings)
                save_index(index, index_file_path)
            
            st.session_state.index = index

        if "messages" not in st.session_state :
            st.session_state.messages = []
        else :
            for msg in st.session_state.messages :
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
            
        st.session_state.messages.append(
            {"role":"user", "content":question}
        )
        with st.chat_message("user"):
            st.write(question)
        q_emb = compute_embeddings(chunks=question, model=model)

        top_k_search = st.session_state.index.search(
            q_emb.reshape(1, -1), 
            k=config.DEFAULT_TOP_K
        )

        top_k_search_text = [
            st.session_state.chunked_text[i] for i in top_k_search[1][0]
        ]

        prompt = prompt_engineering.build_prompt(
            [r for r in top_k_search_text], question, allow_synthesis=False
        )
        
        with st.sidebar:
            prompt_html = prompt_engineering.handle_html_content(prompt)
            st.markdown(prompt_html, unsafe_allow_html=True)

        prompt = prompt_engineering.history_aware_prompt(
            prompt, st.session_state.messages, question
        )

        answer = prompt_engineering.generation_chat_response(
            model="llama3", prompt=prompt
        )

        st.session_state.messages.append(
            {"role":"assistant", "content": answer } 
        )
        with st.chat_message("assistant"):
            st.write( answer )

        question = None 

else : 
    question = "What happened in Cholima and when ?"

warnings.filterwarnings("ignore")
