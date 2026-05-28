from setuptools import setup, find_packages

setup(
    name        = "documentview",
    url         = "https://github.com/DonaldMOUAFO/documentView.git",
    author      = "Donald MOUAFO, donald.l.mouafo@gmail.com",
    description = """documentView API enables semantic search and question answering over documents 
        using a Retrieval-Augmented Generation (RAG).""",
    version ='1.0.0',
    packages = find_packages()  
)