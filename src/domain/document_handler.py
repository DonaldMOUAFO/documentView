import re
import json
import streamlit as st
from io import StringIO
from PyPDF2 import PdfReader
from src.interface.streamlit_app import error_message, inform_message
from langchain_text_splitters import RecursiveCharacterTextSplitter, TokenTextSplitter
from src.infrastructure import config

def load_txt(file_path=config.CORPUS_FILE_PATH):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def clean_text(text):
    # collapses multiple consecutive newlines into a single newline
    text = re.sub(r'\n+', '\n', text)  

    # strip out page markers
    text = re.sub(r'Page \d+', '', text)

    # remove HTML tags and special characters, keep basic punctuation
    text = re.sub(r'<.*?>', '', text)  

    # remove non-alphanumeric characters except basic punctuation
    text = re.sub(r'[^\w\s.,!?()-]', '', text)

    # replace tabs with spaces and collapse multiple spaces into one
    text = text.replace("\t", " ")

    # collapse multiple spaces into a single space    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text 

def chunk_text(text, chunk_size=500, overlap=80):
    # Split text into chunks of max_length characters 
    return [text[i:i+chunk_size] for i in range(0, len(text.split()), chunk_size - overlap)]

def chunk_text_recursive(raw_text, meta_data=None):
    """Recursively chunk text using a character-based splitter.
    
    Args: 
      raw_text (list of dict): The input text to be chunked. Each dict should have a 
        "text" key containing the text of each page and a "page" key indicating the page number.
        If the raw_test originate from a txt file, the page key will be set to 1 that is len(raw_text) = 1.
      chunk_size (int): The maximum size of each chunk (default: 400 characters).
      overlap (int): The number of overlapping characters between chunks (default: 80 characters).
    Returns:
      list of dict: A list of chunked text segments.
    """
    test = []
    doc_data = {}

    for page in raw_text:
        text = page["text"]
        page_num = page["page"]
        
        text = clean_text(text)
        chunked_text = recursive_chunk(text)

        for chunk_text in chunked_text:
            test.append(chunk_text)

            doc_data[len(test)] = {     #{"id": f"p{idx:02d}"
                "text": chunk_text,
                "metadata": {
                    "page": page_num,
                    "id": len(test),
                    "source": meta_data.get("source", "unknown") if meta_data else "unknown",
                    "size": meta_data.get("size", "unknown") if meta_data else "unknown",
                    "type": meta_data.get("type", "unknown") if meta_data else "unknown",
                    "title": meta_data.get("title", "unknown") if meta_data else "unknown",
                    "author": meta_data.get("author", "unknown") if meta_data else "unknown",
                    "creator": meta_data.get("creator", "unknown") if meta_data else "unknown",
                    "producer": meta_data.get("producer", "unknown") if meta_data else "unknown",
                    "modification_date": meta_data.get("modification_date", "unknown") if meta_data else "unknown",
                    "creation_date": meta_data.get("creation_date", "unknown") if meta_data else "unknown",
                }
            }
    return test, doc_data

def save_corpus(doc_data, corpus_file_path=config.CORPUS_FILE_PATH):
    json.dump(
        doc_data, 
        open(corpus_file_path, "w", encoding="utf-8"), 
        indent=2
    )
    inform_message(
        f"Corpus successfully saved at:\n{corpus_file_path}..."
    )

def load_corpus(corpus_file_path=config.CORPUS_FILE_PATH):
    with open(corpus_file_path, "r", encoding="utf-8") as f:
        corpus = json.load(f)
    
    chunked_text = []
    for _, value in corpus.items():
        chunked_text.append(value["text"])

    return chunked_text, corpus

def recursive_chunk(text):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400, chunk_overlap=80,
        length_function=len,
        is_separator_regex=True,
    )
    chunked_text = text_splitter.split_text(text)

    return chunked_text

def tokentextsplitter_chunk(text):
    text_splitter = TokenTextSplitter(chunk_size=100, chunk_overlap=20)
    chunked_text = text_splitter.split_text(text)
    return chunked_text

def load_document(uploaded_file):
    
    file_type = uploaded_file.type

    if file_type == "text/plain" :

        # To convert to a string based IObject and read the text content
        stringio = StringIO(
            uploaded_file.getvalue().decode("utf-8")
        )   

        string_data = [{
            "text" : stringio.read(), # To read file as string
            "page" : 1
        }]  

        meta_data = {
            "source": uploaded_file.name,
            "size": uploaded_file.size,
            "type": uploaded_file.type,
            "title": None,
            "author": None,
            "creator": None,
            "producer": None,
            "modification_date": None,
            "creation_date": None,
        }
        return string_data, meta_data

    elif file_type == "application/pdf" :
        # TO DO :
        # Implement pdf handelling with PyMuPDF or PyMuPDFF4LLM
        text = []
        try :
            pdf = PdfReader(uploaded_file)
            
            # Document-level metadata
            doc_meta = pdf.metadata or {}
            st.write(f"Document Metadata: {doc_meta}")

            for i, page in enumerate(pdf.pages) :
                single_page_text = page.extract_text() or ""
                text.append({
                    "text": clean_text(single_page_text),
                    "page": i + 1, 
                })
            
        except Exception as e :
            doc_meta = None
            st.error(f"The following Error occured when handelling Pdf!\nError : {e}")
            st.markdown(
                """
                <div style="
                    padding:20px;
                    border-radius:12px;
                    background:#f9fafc;
                    border:1px solid #e6e6e6;
                ">
                <h3 style="margin-top:0;">📄 Not possible to handle the uploaded document due to aforementioned error!</h3>
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
        if doc_meta is not None :
            meta_data = {
                "source": uploaded_file.name,
                "size": uploaded_file.size,
                "type": uploaded_file.type,
                "title": doc_meta.get("/Title", ""),
                "author": doc_meta.get("/Author", ""),
                "creator": doc_meta.get("/Creator", ""),
                "producer": doc_meta.get("/Producer", ""),
                "modification_date": doc_meta.get("/ModDate", ""),
                "creation_date": doc_meta.get("/CreationDate", ""),
            }
        return text, meta_data        
    else:
        st.error("Unsupported file type. Please upload a TXT or PDF.")
        return ""
    
# class DocumentHandler:

#     def __init__(self, uploaded_file) -> None:
#         self.uploaded_file = uploaded_file
#         self.file_type = uploaded_file.type

#     def __clean_text(self, text):
#         # collapses multiple consecutive newlines into a single newline
#         text = re.sub(r'\n+', '\n', text)  

#         # strip out page markers
#         text = re.sub(r'Page \d+', '', text)

#         # remove HTML tags and special characters, keep basic punctuation
#         text = re.sub(r'<.*?>', '', text)  

#         # remove non-alphanumeric characters except basic punctuation
#         text = re.sub(r'[^\w\s.,!?()-]', '', text)

#         # replace tabs with spaces and collapse multiple spaces into one
#         text = text.replace("\t", " ")

#         # collapse multiple spaces into a single space    text = re.sub(r' +', ' ', text)
#         text = re.sub(r'\s+', ' ', text)
#         return text

#     def txt_meta_data(self):
        
#         return {
#             "source": self.uploaded_file.name,
#             "size": self.uploaded_file.size,
#             "type": self.uploaded_file.type,
#             "title": None,
#             "author": None,
#             "creator": None,
#             "producer": None,
#             "modification_date": None,
#             "creation_date": None,
#         }
    
#     def pdf_meta_data(self, pdf):
       
#         doc_meta = pdf.metadata or {}
#         meta_data = {
#             "source": self.uploaded_file.name,
#             "size": self.uploaded_file.size,
#             "type": self.uploaded_file.type,
#             "title": doc_meta.get("/Title", ""),
#             "author": doc_meta.get("/Author", ""),
#             "creator": doc_meta.get("/Creator", ""),
#             "producer": doc_meta.get("/Producer", ""),
#             "modification_date": doc_meta.get("/ModDate", ""),
#             "creation_date": doc_meta.get("/CreationDate", ""),
#         }
        
#         return meta_data

#     def load_document(self):

#         text = []

#         if self.file_type == "text/plain" :

#             # To convert to a string based IObject and read the text content
#             stringio = StringIO(
#                 self.uploaded_file.getvalue().decode("utf-8")
#             )   

#             text.append({
#                 "text" : self.__clean_text(stringio.read()), # To read file as string
#                 "page" : 1
#             })  

#         elif self.file_type == "application/pdf" :

#             try :
#                 pdf = PdfReader(self.uploaded_file)
                
#                 for i, page in enumerate(pdf.pages) :
#                     single_page_text = page.extract_text() or ""

#                     if len(single_page_text.strip()) == 0 :
#                         #Page {i+1} contains no extractable text and will be skipped.")
#                         continue
#                     text.append({
#                         "text": self.__clean_text(single_page_text),
#                         "page": i + 1, 
#                     })
#             except Exception as e :
#                 message = "Not possible to handle the uploaded document due to aforementioned error!"
#                 error_message(e, f"{message}")
                    
#         return text
    
#     def chunk_text_recursive(self, text_data_dict, doc_meta):
#         """Recursively chunk text using a character-based splitter.
        
#         Args: 
#         raw_text (list of dict): The input text to be chunked. Each dict should have a 
#             "text" key containing the text of each page and a "page" key indicating the page number.
#             If the raw_test originate from a txt file, the page key will be set to 1 that is len(raw_text) = 1.
#         chunk_size (int): The maximum size of each chunk (default: 400 characters).
#         overlap (int): The number of overlapping characters between chunks (default: 80 characters).
#         Returns:
#         list of dict: A list of chunked text segments.
#         """
#         test = []
#         doc_data = {}

#         for page in raw_text:
#             text = page["text"]
#             page_num = page["page"]
            
#             text = clean_text(text)
#             chunked_text = recursive_chunk(text)

#             for chunk_text in chunked_text:
#                 test.append(chunk_text)

#                 doc_data[len(test)] = {     #{"id": f"p{idx:02d}"
#                     "text": chunk_text,
#                     "metadata": {
#                         "page": page_num,
#                         "id": len(test),
#                         "source": meta_data.get("source", "unknown") if meta_data else "unknown",
#                         "size": meta_data.get("size", "unknown") if meta_data else "unknown",
#                         "type": meta_data.get("type", "unknown") if meta_data else "unknown",
#                         "title": meta_data.get("title", "unknown") if meta_data else "unknown",
#                         "author": meta_data.get("author", "unknown") if meta_data else "unknown",
#                         "creator": meta_data.get("creator", "unknown") if meta_data else "unknown",
#                         "producer": meta_data.get("producer", "unknown") if meta_data else "unknown",
#                         "modification_date": meta_data.get("modification_date", "unknown") if meta_data else "unknown",
#                         "creation_date": meta_data.get("creation_date", "unknown") if meta_data else "unknown",
#                     }
#                 }
#         return test, doc_data

#     def save_corpus(self, doc_meta, corpus_file_path=corpus_file_path):
#         pass

#     def fit(self):
#         text_data_dict, doc_meta = load_document(uploaded_file)  

#         # chunked_text is a list of dist. with "text" and "metadata" keys. 
#         # text is a string containing a single chunk.
#         # Metadata is a dict including the following keys which each value is a string
#         # (source, page, chunk_id, type, title, author, creator, producer, modification_date, creation_date).
#         chunked_text, doc_meta = chunk_text_recursive(text_data_dict, doc_meta)
#         save_corpus(doc_meta, corpus_file_path=corpus_file_path)
