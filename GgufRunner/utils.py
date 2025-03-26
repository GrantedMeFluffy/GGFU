import os
import uuid
import streamlit as st
from typing import Dict, Any, List

def initialize_session_state() -> None:
    """Initialize Streamlit session state variables if they don't exist."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if "model_loaded" not in st.session_state:
        st.session_state.model_loaded = False
    
    if "current_model_path" not in st.session_state:
        st.session_state.current_model_path = None
    
    if "current_model_params" not in st.session_state:
        st.session_state.current_model_params = None
        
    if "show_session_browser" not in st.session_state:
        st.session_state.show_session_browser = False
        
    # Generation control
    if "generation_stopped" not in st.session_state:
        st.session_state.generation_stopped = False
        
    # Roleplay mode settings
    if "roleplay_mode" not in st.session_state:
        st.session_state.roleplay_mode = False
        
    if "selected_persona" not in st.session_state:
        st.session_state.selected_persona = "helpful_assistant"

def format_message(role: str, content: str) -> Dict[str, str]:
    """
    Format a message dictionary.
    
    Args:
        role: The role of the message sender (user or assistant)
        content: The content of the message
        
    Returns:
        Dict: A message dictionary with role and content
    """
    return {"role": role, "content": content}

def calculate_file_size(file_path: str) -> str:
    """
    Calculate the human-readable size of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: Human-readable file size
    """
    if not os.path.exists(file_path):
        return "N/A"
    
    # Get file size in bytes
    size_bytes = os.path.getsize(file_path)
    
    # Convert to human-readable format
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.2f} PB"

def format_model_params_display(params: Dict[str, Any]) -> str:
    """
    Format model parameters for display.
    
    Args:
        params: Dictionary of model parameters
        
    Returns:
        str: Formatted parameter display string
    """
    if not params:
        return "No parameters available"
    
    # Format each parameter for display
    param_strings = []
    for key, value in params.items():
        param_strings.append(f"{key}: {value}")
    
    return ", ".join(param_strings)

def get_prompt_template(messages: List[Dict[str, str]], roleplay_mode: bool = False, persona: str = None) -> str:
    """
    Convert the message history to a prompt for the model.
    
    Args:
        messages: List of message dictionaries
        roleplay_mode: Whether roleplay mode is enabled
        persona: The selected persona when roleplay mode is enabled
        
    Returns:
        str: Formatted prompt string
    """
    prompt = ""
    
    # Add persona instructions at the beginning if roleplay mode is enabled
    if roleplay_mode and persona:
        prompt += get_persona_instructions(persona) + "\n\n"
    
    for message in messages:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            prompt += f"User: {content}\n\n"
        elif role == "assistant":
            prompt += f"Assistant: {content}\n\n"
    
    # Add the final assistant prefix
    prompt += "Assistant: "
    
    return prompt

def get_persona_instructions(persona: str) -> str:
    """
    Get the instruction prompt for a specific persona.
    
    Args:
        persona: The name of the persona
        
    Returns:
        str: Instruction prompt for the persona
    """
    personas = {
        "helpful_assistant": "You are a helpful, respectful and honest assistant. Always provide accurate information and assist the user to the best of your ability.",
        
        "pirate": "You are a salty sea pirate from the Golden Age of Piracy. Speak with pirate slang, use nautical references, and be bold and adventurous in your responses. Add 'Arr!' and 'Matey' occasionally.",
        
        "shakespeare": "You are William Shakespeare, the famous playwright and poet. Respond in Elizabethan English, use poetic language, make references to your famous works, and occasionally add 'thee', 'thou', and other period-appropriate language.",
        
        "detective": "You are a hard-boiled detective from a noir film. Speak in short, punchy sentences. Be cynical but insightful. Make observations about the 'case' the user presents to you as if you're investigating it.",
        
        "sci_fi_robot": "You are an advanced AI robot from the far future. Use technical terminology, make references to your circuits and processors, mention your programming directives, and occasionally glitch in your responses.",
        
        "medieval_scholar": "You are a medieval scholar and philosopher from the 12th century. Reference ancient texts, speak formally with archaic terms, express wonder at modern concepts, and frame your knowledge within a medieval worldview.",
        
        "cosmic_entity": "You are a cosmic entity that exists beyond time and space. Speak in mysterious and enigmatic ways, reference the vastness of the universe, different dimensions, and cosmic phenomena. Make your responses sound profound and otherworldly."
    }
    
    return personas.get(persona, personas["helpful_assistant"])
