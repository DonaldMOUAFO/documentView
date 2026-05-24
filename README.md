# documentView
The documentView API enables semantic search and question answering over documents using a Retrieval-Augmented Generation (RAG) pipeline. 
The purpose of RAG is to specialize an Large Language Model on a particular dataset corpus without complex retraining effort.

To summarized, A RAG process consistes of four steps :
- Load the document a extract the corpus
The first step consistes of extracting the textual content of the doccument from it original medium (either Pdf, web page, or .txt doc). 

- Chunked the document into a serie of chunks 
This step consistes of dividing the entire document into a number of smaller chunks

- Embeddings and indexing
This step consiste of converting each document chunk into a vector (embedings) using a LLM. Then indexing the embeddings to associated each with appropriate index which enables also to uniquely identify the corresponding chunk. Then ensemble of chunked document, embeddings and indexes correspond to the vector database of the corpus text.

- Retreival and generation
The last step consiste of retreiving information from the document through retreival and generation process. This means, when a user as question, the question is converted to a vector using the same LLM that was used to generate embeddings of the corpus text. The question's embadding is then use to conduct similarity search to vector database, the top k most similar chunk are the retreived. Finaly both the question and the top k chunked are used to build the prompt to send to the LLM for LLM to generate the final answer that is send back to the user.

# 1. Quit start

Working with DocumentView is very simple. After installation, one simply upload a document and start questionning it. for the moment both `Pdf` and `txt` are supported.

The installation procedure of `DocumentView` is the following:
- clone the repository 
```
  git clone https://github.com/DonaldMOUAFO/documentView.git
```
- Navigate to the documentView/
```
  cd documentView/
```
- Create a virtual environement 
```
  conda create -m my/env/name
```
- Install requirements.txt
```
  pip install -r requirement.txt
```
- Install documentView
```
  pip install -e .
```

After installation, the app can be run as follow.
```
  streamlit run interface/app.py 

```

The following image is an illustration of the User Interface of DocumentView.
<p align="center"> 
  <img src="data/images/Screen_capture_of_DocumentView-UI.png" width="900"> 
  One can see typical discussion with the uploaded document
</p>

### Output ####
============================================================================================================================================================================
System : You are a concise assistant. Rely ONLY on the provided context, but you MAY synthesize an answer by combining or paraphrasing the facts present. If the context truly lacks sufficient evidence, say you do not know instead of guessing.
Context:
Kyoto University and UNESCO. Among severe landslides, about 2800 died in Cholima in Honduras in 1973 and almost 1200 in northern Italy in 1963. The Louvain University database on which the figures

the population of European Jews, which exploded from 30,000 people in the 13th century to something like 9 million just prior to World War II, Behar says. The Nazis and their allies killed 6 million

officer of the UN University. A report released at the time of the meeting says some cultural sites are at risk from landslides, including the Valley of the Kings where Egypts Pharaohs are buried,

Kings where Egypts Pharaohs are buried, the Inca mountain fortress of Machu Picchu in Peru and Chinas Huaqing Palace dating from the Tang dynasty. Special attention should be given to cultural and

when the ancestral Eve of all living humans lived in Africa, about 180,000 years ago. Now they have found four ancestral Jewish mothers. I think there was some kind of genetic pool that was in the

User Question: What happened in Cholima and when ?
Answer: According to the provided context, approximately 2800 people died in Cholima, Honduras due to severe landslides in 1973.
===========================================================================================================================================================================
```
This RAG demontration was implemented using `nltk_data/corpora/abc/science.txt` from NLTK python package.