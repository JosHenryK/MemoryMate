from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import LLM_CONFIG

def create_chains():
    """Create LLM processing chains.
    
    Returns a dictionary containing two processing chains:
    - 'key_points': A processing chain that identifies key points in a conversation.
    - 'summary': A processing chain that creates a summary of a conversation.
    """
    llm = ChatGoogleGenerativeAI(**LLM_CONFIG)
    
    key_points_prompt = ChatPromptTemplate.from_template(
        "Identify {num_points} key points: {conversation}"
    )
    
    summary_prompt = ChatPromptTemplate.from_template(
        "Create summary: {conversation}"
    )
    
    return {
        "key_points": key_points_prompt | llm | StrOutputParser(),
        "summary": summary_prompt | llm | StrOutputParser()
    }

if __name__ == "__main__":
    # Test chain creation
    chains = create_chains()
    print("Chains created:", chains.keys())