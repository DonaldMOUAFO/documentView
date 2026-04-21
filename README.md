# documentView
The documentView API enables semantic search and question answering over documents using a Retrieval-Augmented Generation (RAG) pipeline. It retrieves the most relevant document segments from a vector database and combines them with a language model to produce precise, context-aware answers, improving accuracy and reducing hallucinations.


# 1. Quit start
python src/application/main.py -d data/corpus/test.txt

### Output ####
```
===============================================================================================================================
System : You are a concise assistant. Rely ONLY on the provided context, but you MAY synthesize an answer by combining or paraphrasing the facts present. If the context truly lacks sufficient evidence, say you do not know instead of guessing.
Context:
Kyoto University and UNESCO. Among severe landslides, about 2800 died in Cholima in Honduras in 1973 and almost 1200 in northern Italy in 1963. The Louvain University database on which the figures

the population of European Jews, which exploded from 30,000 people in the 13th century to something like 9 million just prior to World War II, Behar says. The Nazis and their allies killed 6 million

officer of the UN University. A report released at the time of the meeting says some cultural sites are at risk from landslides, including the Valley of the Kings where Egypts Pharaohs are buried,

record set in May 1969 by the returning Apollo 10 command module. As its heat-shield fried away, a comet-like plume formed in its wake, looking like a torch that was visible in parts of the western

Kings where Egypts Pharaohs are buried, the Inca mountain fortress of Machu Picchu in Peru and Chinas Huaqing Palace dating from the Tang dynasty. Special attention should be given to cultural and

User Question: What happened in Cholima and when
Answer: According to the provided context, about 2800 people died in Cholima, Honduras, due to severe landslides in 1973.
==================================================================================================================
```

This RAG demontration was implemented using `nltk_data/corpora/abc/science.txt` from NLTK python package.