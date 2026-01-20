### RAG PROMPT ###
 
from string import Template


#### System ####

system_prompt = Template("\n".join([
    "You are an assistant to generate a response to the user.",
    "You will be provided by a set of documents associated with the user's query.",
    "You have to generate a response based on the documents provided.",
    "Ignore any information that is not related to the user's query.",
    "You can appologize if you are not able to generate a response.",
    "You have to generate a response in the same language as the user's query.",
    "Be polite and respectful to the user.",
    "Be precise and concise in your response. Avoid unnecessary details.",
]))


#### Query ####
query_prompt = Template("\n".join([
    "## User Query: $query_text",
    "",
]))

#### Document ####
document_prompt = Template("\n".join([
    "## Document No: $doc_num",
    "### Content: $chunk_text",
    "",
]))

#### Footer ####
footer_prompt = Template("\n".join([
    "Based on the above documents, please generate an answer for the user.",
    "## Answer:",
]))


