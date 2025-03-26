import os
import time
import streamlit as st
from typing import Dict, Any, List, Optional
from model_manager import ModelManager
from session_handler import SessionHandler
from utils import format_message, calculate_file_size, format_model_params_display, get_prompt_template

def show_header() -> None:
    """Display the application header."""
    st.title("GGUF Model Chat")
    st.markdown("Upload, load, and chat with GGUF language models")

def show_sidebar(model_manager: ModelManager, session_handler: SessionHandler) -> None:
    """
    Display the sidebar with model loading options and settings.
    
    Args:
        model_manager: The ModelManager instance
        session_handler: The SessionHandler instance
    """
    st.title("Model Controls")
    
    # Option buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Load Model", key="load_model_btn", use_container_width=True):
            st.session_state.show_session_browser = False
            st.rerun()
    
    with col2:
        if st.button("Browse Sessions", key="browse_sessions_btn", use_container_width=True):
            st.session_state.show_session_browser = True
            st.rerun()
    
    st.divider()
    
    # Model selection and loading
    available_models = model_manager.get_available_models()
    
    if available_models:
        st.subheader("Load Available Model")
        selected_model = st.selectbox(
            "Select a model to load", 
            options=available_models,
            format_func=os.path.basename
        )
        
        # Model parameters
        with st.expander("Model Parameters"):
            ctx_length = st.slider("Context Length (n_ctx)", 512, 8192, 2048, 512)
            batch_size = st.slider("Batch Size (n_batch)", 128, 1024, 512, 128)
            gpu_layers = st.slider("GPU Layers", 0, 100, 0, 1)
        
        # Load button
        if st.button("Load Selected Model", use_container_width=True):
            if selected_model:
                # Create progress bar for loading
                progress_text = "Loading model..."
                progress_bar = st.progress(0)
                
                # Parameters for model loading
                params = {
                    "n_ctx": ctx_length,
                    "n_batch": batch_size,
                    "n_gpu_layers": gpu_layers,
                }
                
                # Loading happens in stages for better UI feedback
                progress_bar.progress(0.1)
                time.sleep(0.5)  # Show progress starting
                
                # Load model
                success = model_manager.load_model(selected_model, params)
                
                progress_bar.progress(0.9)
                time.sleep(0.5)  # Small delay to show progress
                
                if success:
                    progress_bar.progress(1.0)
                    st.success(f"Model loaded successfully: {os.path.basename(selected_model)}")
                    # If there was a session loaded, check model compatibility
                    if "loaded_session_model_path" in st.session_state:
                        if st.session_state["loaded_session_model_path"] != selected_model:
                            st.warning("The loaded session was created with a different model. Results may vary.")
                    st.rerun()
                else:
                    progress_bar.empty()
                    st.error("Failed to load model")
    
    # Model unloading
    if st.session_state.get("model_loaded"):
        st.divider()
        st.subheader("Memory Management")
        if st.button("Unload Current Model", use_container_width=True):
            model_manager.unload_model()
            st.success("Model unloaded successfully")
            st.rerun()
    
    # Session management
    if st.session_state.get("model_loaded") and st.session_state.get("messages"):
        st.divider()
        st.subheader("Session Management")
        
        session_name = st.text_input("Session Name (optional)", 
                                   placeholder="Enter a name to save this session")
        
        if st.button("Save Current Session", use_container_width=True):
            saved_path = session_handler.save_session(session_name)
            st.success(f"Session saved: {os.path.basename(saved_path)}")
    
    # Add generation settings
    if st.session_state.get("model_loaded"):
        st.divider()
        st.subheader("Generation Settings")
        
        # Primary generation parameters - outside the expander for visibility
        st.session_state["temperature"] = st.slider(
            "Temperature", 0.0, 2.0, 0.7, 0.01,
            help="Higher values produce more diverse and creative outputs, lower values are more focused and deterministic"
        )
        
        # Create two columns for the sliders
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state["max_tokens"] = st.slider(
                "Max Tokens", 64, 4096, 512, 64,
                help="Maximum length of generated text"
            )
        
        with col2:
            st.session_state["repeat_penalty"] = st.slider(
                "Repetition Penalty", 1.0, 2.0, 1.1, 0.05,
                help="Higher values reduce repetition"
            )
        
        # Style presets with detailed parameters
        style_presets = {
            "balanced": {
                "name": "Balanced",
                "description": "A good balance between creativity and coherence",
                "parameters": {
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "repeat_penalty": 1.1,
                    "max_tokens": 512,
                    "frequency_penalty": 0.0,
                    "presence_penalty": 0.0
                }
            },
            "creative": {
                "name": "Creative",
                "description": "More varied and imaginative responses",
                "parameters": {
                    "temperature": 1.0,
                    "top_p": 0.9,
                    "top_k": 60,
                    "repeat_penalty": 1.05,
                    "max_tokens": 512,
                    "frequency_penalty": 0.0,
                    "presence_penalty": 0.1
                }
            },
            "precise": {
                "name": "Precise",
                "description": "More deterministic and focused responses",
                "parameters": {
                    "temperature": 0.3,
                    "top_p": 0.85,
                    "top_k": 20,
                    "repeat_penalty": 1.2,
                    "max_tokens": 512,
                    "frequency_penalty": 0.1,
                    "presence_penalty": 0.0
                }
            },
            "verbose": {
                "name": "Verbose",
                "description": "Longer, more detailed responses",
                "parameters": {
                    "temperature": 0.8,
                    "top_p": 0.95,
                    "top_k": 50,
                    "repeat_penalty": 1.0,
                    "max_tokens": 1024,
                    "frequency_penalty": 0.0,
                    "presence_penalty": 0.0
                }
            },
            "concise": {
                "name": "Concise",
                "description": "Shorter, more to-the-point responses",
                "parameters": {
                    "temperature": 0.4,
                    "top_p": 0.9,
                    "top_k": 30,
                    "repeat_penalty": 1.15,
                    "max_tokens": 256,
                    "frequency_penalty": 0.1,
                    "presence_penalty": 0.0
                }
            },
            "factual": {
                "name": "Factual",
                "description": "More likely to stick to known facts",
                "parameters": {
                    "temperature": 0.1,
                    "top_p": 0.7,
                    "top_k": 10,
                    "repeat_penalty": 1.3,
                    "max_tokens": 512,
                    "frequency_penalty": 0.2,
                    "presence_penalty": 0.0
                }
            },
            "custom": {
                "name": "Custom",
                "description": "Your custom settings",
                "parameters": {}
            }
        }
        
        # Initialize user presets if not already in session state
        if "user_presets" not in st.session_state:
            st.session_state["user_presets"] = {}
        
        # Add user presets to available presets
        all_presets = {**style_presets, **st.session_state["user_presets"]}
            
        # Style preset selection
        preset_options = list(all_presets.keys())
        
        # Get current parameter values
        current_params = {
            "temperature": st.session_state.get("temperature", 0.7),
            "top_p": st.session_state.get("top_p", 0.95),
            "top_k": st.session_state.get("top_k", 40),
            "repeat_penalty": st.session_state.get("repeat_penalty", 1.1),
            "max_tokens": st.session_state.get("max_tokens", 512),
            "frequency_penalty": st.session_state.get("frequency_penalty", 0.0),
            "presence_penalty": st.session_state.get("presence_penalty", 0.0),
        }
        
        # Determine current preset (or custom if no match)
        current_preset = "custom"
        for preset_key, preset_data in all_presets.items():
            if preset_key != "custom" and preset_data["parameters"] == current_params:
                current_preset = preset_key
                break
        
        # Two columns for preset selection and management
        preset_col1, preset_col2 = st.columns([3, 1])
        
        with preset_col1:
            selected_preset = st.selectbox(
                "Response Style",
                options=preset_options,
                format_func=lambda x: all_presets[x]["name"],
                index=preset_options.index(current_preset) if current_preset in preset_options else 0,
                key="style_preset",
                help="Choose a preset style for AI responses or create your own"
            )
        
        with preset_col2:
            manage_presets = st.button(
                "Manage", 
                key="manage_presets",
                help="Save your current settings as a preset or delete existing presets",
                use_container_width=True
            )
        
        # Apply selected preset
        if selected_preset != "custom" and st.session_state.get("last_selected_preset") != selected_preset:
            preset_params = all_presets[selected_preset]["parameters"]
            for param, value in preset_params.items():
                st.session_state[param] = value
            st.session_state["last_selected_preset"] = selected_preset
            # Force rerun to update sliders
            st.rerun()
        
        # Display preset description
        st.info(all_presets[selected_preset]["description"])
        
        # Manage presets functionality
        if manage_presets:
            with st.expander("Manage Style Presets", expanded=True):
                st.subheader("Save Current Settings as Preset")
                preset_name = st.text_input("Preset Name", value="My Custom Preset", key="new_preset_name")
                preset_desc = st.text_area("Description", value="My personalized response style", key="new_preset_desc")
                
                save_col1, save_col2 = st.columns(2)
                with save_col1:
                    if st.button("Save Preset", key="save_preset_confirm", use_container_width=True):
                        if preset_name.strip():
                            # Generate a unique key from the name
                            preset_key = preset_name.lower().replace(" ", "_")
                            counter = 1
                            original_key = preset_key
                            
                            # Make sure key doesn't override built-in presets
                            while preset_key in style_presets:
                                preset_key = f"{original_key}_{counter}"
                                counter += 1
                            
                            # Save the preset
                            st.session_state["user_presets"][preset_key] = {
                                "name": preset_name,
                                "description": preset_desc,
                                "parameters": {
                                    "temperature": st.session_state.get("temperature", 0.7),
                                    "top_p": st.session_state.get("top_p", 0.95),
                                    "top_k": st.session_state.get("top_k", 40),
                                    "repeat_penalty": st.session_state.get("repeat_penalty", 1.1),
                                    "max_tokens": st.session_state.get("max_tokens", 512),
                                    "frequency_penalty": st.session_state.get("frequency_penalty", 0.0),
                                    "presence_penalty": st.session_state.get("presence_penalty", 0.0)
                                }
                            }
                            st.success(f"Preset '{preset_name}' saved!")
                            st.rerun()
                
                # Only show delete functionality if user has saved presets
                if st.session_state["user_presets"]:
                    st.subheader("Manage User Presets")
                    
                    manage_col1, manage_col2 = st.columns(2)
                    
                    with manage_col1:
                        # Delete presets
                        user_preset_keys = list(st.session_state["user_presets"].keys())
                        preset_to_delete = st.selectbox(
                            "Select Preset to Delete",
                            options=user_preset_keys,
                            format_func=lambda x: st.session_state["user_presets"][x]["name"],
                            key="preset_to_delete"
                        )
                        
                        if st.button("Delete Selected Preset", key="delete_preset", use_container_width=True):
                            if preset_to_delete:
                                del st.session_state["user_presets"][preset_to_delete]
                                st.success(f"Preset deleted!")
                                st.rerun()
                    
                    with manage_col2:
                        # Export presets
                        if st.button("Export All Presets", key="export_presets", use_container_width=True):
                            # Convert presets to JSON string
                            import json
                            presets_json = json.dumps(st.session_state["user_presets"], indent=2)
                            
                            # Create a download link
                            import base64
                            b64 = base64.b64encode(presets_json.encode()).decode()
                            href = f'<a href="data:application/json;base64,{b64}" download="model_presets.json">Download Presets File</a>'
                            st.markdown(href, unsafe_allow_html=True)
                            st.success("Click the link above to download your presets!")
                
                # Import presets section
                st.subheader("Import Presets")
                uploaded_preset_file = st.file_uploader(
                    "Upload Presets File",
                    type=["json"],
                    help="Import presets from a JSON file",
                    key="preset_upload"
                )
                
                if uploaded_preset_file is not None:
                    try:
                        import json
                        # Parse the uploaded JSON file
                        presets_data = json.loads(uploaded_preset_file.getvalue().decode())
                        
                        if isinstance(presets_data, dict):
                            # Initialize user_presets if not exist
                            if "user_presets" not in st.session_state:
                                st.session_state["user_presets"] = {}
                                
                            # Count how many new presets will be added
                            new_preset_count = sum(1 for key in presets_data if key not in st.session_state["user_presets"])
                            
                            # Display confirmation message
                            if new_preset_count > 0:
                                st.info(f"Found {new_preset_count} new presets to import")
                                
                                if st.button("Confirm Import", key="confirm_import", use_container_width=True):
                                    # Merge with existing presets (imported ones override duplicates)
                                    st.session_state["user_presets"] = {**st.session_state["user_presets"], **presets_data}
                                    st.success(f"Successfully imported {new_preset_count} presets!")
                                    st.rerun()
                            else:
                                st.info("No new presets found in the uploaded file")
                        else:
                            st.error("Invalid preset file format. Expected a JSON object.")
                    except Exception as e:
                        st.error(f"Error importing presets: {str(e)}")
                    
                    # Clear the file uploader
                    uploaded_preset_file = None
                
        # Advanced parameters in expander
        with st.expander("Advanced Parameters", expanded=False):
            st.session_state["top_p"] = st.slider(
                "Top P", 0.0, 1.0, 0.95, 0.05,
                help="Nucleus sampling: 1.0 considers all tokens, lower values focus on more likely tokens"
            )
            
            st.session_state["top_k"] = st.slider(
                "Top K", 1, 100, 40, 1,
                help="Only consider the top K most likely tokens (lower = more focused)"
            )
            
            frequency_penalty = st.slider(
                "Frequency Penalty", 0.0, 2.0, 0.0, 0.1,
                help="Penalize tokens based on their frequency in the text so far"
            )
            
            presence_penalty = st.slider(
                "Presence Penalty", 0.0, 2.0, 0.0, 0.1,
                help="Penalize tokens that have appeared at all in the text so far"
            )
            
            if "frequency_penalty" not in st.session_state:
                st.session_state["frequency_penalty"] = frequency_penalty
            if "presence_penalty" not in st.session_state:
                st.session_state["presence_penalty"] = presence_penalty
        
        # Theme customization
        st.divider()
        st.subheader("Theme Settings")
        
        # Collapsible section for theme customization
        with st.expander("App Appearance", expanded=False):
            # Color picker for the primary color (buttons, sliders, etc.)
            st.session_state["primary_color"] = st.color_picker(
                "Primary Color",
                value=st.session_state.get("primary_color", "#2A9D8F"),
                help="Color for buttons, sliders, and accents"
            )
            
            # Create two columns for more color options
            col1, col2 = st.columns(2)
            
            with col1:
                # Color for assistant (AI) messages
                st.session_state["assistant_color"] = st.color_picker(
                    "AI Message Color",
                    value=st.session_state.get("assistant_color", "#E9ECEF"),
                    help="Background color for AI messages"
                )
            
            with col2:
                # Color for user messages
                st.session_state["user_color"] = st.color_picker(
                    "User Message Color",
                    value=st.session_state.get("user_color", "#F0F7FF"),
                    help="Background color for your messages"
                )
            
            # Apply theme button
            if st.button("Apply Theme", use_container_width=True):
                # Update the theme in config.toml
                import toml
                
                # Read the current config
                config_path = ".streamlit/config.toml"
                try:
                    with open(config_path, "r") as f:
                        config = toml.load(f)
                    
                    # Update theme settings
                    if "theme" not in config:
                        config["theme"] = {}
                    
                    config["theme"]["primaryColor"] = st.session_state.get("primary_color", "#2A9D8F")
                    
                    # Write the updated config
                    with open(config_path, "w") as f:
                        toml.dump(config, f)
                    
                    st.success("Theme applied! Refresh the page to see all changes.")
                except Exception as e:
                    st.error(f"Error updating theme: {str(e)}")
        
        # Roleplay mode controls
        st.divider()
        st.subheader("Roleplay Mode")
        
        # Toggle for roleplay mode
        st.session_state["roleplay_mode"] = st.toggle(
            "Enable Roleplay Mode", 
            st.session_state.get("roleplay_mode", False),
            help="Make the AI adopt different personas and behaviors"
        )
        
        # Persona selection (only shown when roleplay mode is enabled)
        if st.session_state.get("roleplay_mode", False):
            persona_options = {
                "helpful_assistant": "Helpful Assistant",
                "pirate": "Pirate",
                "shakespeare": "Shakespeare",
                "detective": "Detective",
                "sci_fi_robot": "Sci-Fi Robot",
                "medieval_scholar": "Medieval Scholar",
                "cosmic_entity": "Cosmic Entity"
            }
            
            st.session_state["selected_persona"] = st.selectbox(
                "Select Persona",
                options=list(persona_options.keys()),
                format_func=lambda x: persona_options[x],
                index=list(persona_options.keys()).index(
                    st.session_state.get("selected_persona", "helpful_assistant")
                ),
                help="Choose a persona for the AI to adopt"
            )
            
            # Show the current persona's description
            from utils import get_persona_instructions
            with st.expander("Persona Description", expanded=False):
                st.markdown(get_persona_instructions(st.session_state.get("selected_persona", "helpful_assistant")))

def show_model_info() -> None:
    """Display information about the currently loaded model."""
    if st.session_state.get("current_model_path"):
        model_path = st.session_state["current_model_path"]
        model_size = calculate_file_size(model_path)
        model_params = st.session_state.get("current_model_params", {})
        
        with st.expander("Model Information", expanded=False):
            # Basic model info
            st.markdown("#### Model Details")
            st.markdown(f"**Name:** {os.path.basename(model_path)}")
            st.markdown(f"**Size:** {model_size}")
            st.markdown(f"**Load Time:** {st.session_state.get('model_load_time', 0):.2f} seconds")
            
            # Technical parameters
            st.markdown("#### Technical Parameters")
            st.code(format_model_params_display(model_params))
            
            # Current personalization settings
            st.markdown("#### Current Personalization")
            
            # Create 3 columns for compact display
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Style Profile:**")
                current_preset = st.session_state.get("style_preset", "custom")
                if current_preset != "custom":
                    # Get preset name from either built-in or user presets
                    preset_name = None
                    if "user_presets" in st.session_state and current_preset in st.session_state["user_presets"]:
                        preset_name = st.session_state["user_presets"][current_preset]["name"]
                    else:
                        # This assumes the style_presets variable from show_sidebar is accessible here
                        # If not, you would need to recreate it or refactor to make it accessible
                        preset_name = current_preset.capitalize()
                    
                    st.markdown(f"*{preset_name}*")
                else:
                    st.markdown("*Custom*")
            
            with col2:
                st.markdown("**Temperature:**")
                st.markdown(f"{st.session_state.get('temperature', 0.7)}")
                
                st.markdown("**Max Tokens:**")
                st.markdown(f"{st.session_state.get('max_tokens', 512)}")
            
            with col3:
                st.markdown("**Top P:**")
                st.markdown(f"{st.session_state.get('top_p', 0.95)}")
                
                st.markdown("**Repeat Penalty:**")
                st.markdown(f"{st.session_state.get('repeat_penalty', 1.1)}")
            
            # Roleplay information if active
            if st.session_state.get("roleplay_mode", False):
                st.markdown("#### Roleplay Settings")
                persona_options = {
                    "helpful_assistant": "Helpful Assistant",
                    "pirate": "Pirate",
                    "shakespeare": "Shakespeare",
                    "detective": "Detective",
                    "sci_fi_robot": "Sci-Fi Robot",
                    "medieval_scholar": "Medieval Scholar",
                    "cosmic_entity": "Cosmic Entity"
                }
                selected_persona = st.session_state.get("selected_persona", "helpful_assistant")
                persona_name = persona_options.get(selected_persona, "Unknown")
                st.markdown(f"**Active Persona:** {persona_name}")
                
                # Brief persona description
                from utils import get_persona_instructions
                persona_instructions = get_persona_instructions(selected_persona)
                if persona_instructions:
                    # Extract just the first sentence or two for a brief summary
                    brief_desc = persona_instructions.split('.')[0] + '.'
                    st.markdown(f"**Character Brief:** {brief_desc}")

def show_chat_interface(model_manager: ModelManager, session_handler: SessionHandler) -> None:
    """
    Display the chat interface for interacting with the model.
    
    Args:
        model_manager: The ModelManager instance
        session_handler: The SessionHandler instance
    """
    # Show roleplay mode indicator if active
    if st.session_state.get("roleplay_mode", False):
        persona_options = {
            "helpful_assistant": "Helpful Assistant",
            "pirate": "Pirate",
            "shakespeare": "Shakespeare",
            "detective": "Detective",
            "sci_fi_robot": "Sci-Fi Robot",
            "medieval_scholar": "Medieval Scholar",
            "cosmic_entity": "Cosmic Entity"
        }
        
        selected_persona = st.session_state.get("selected_persona", "helpful_assistant")
        persona_display_name = persona_options.get(selected_persona, "Unknown Persona")
        
        st.info(f"🎭 Roleplay Mode Active: **{persona_display_name}**")
    
    # Display chat messages from history with custom styling
    for message in st.session_state.messages:
        role = message["role"]
        # Apply custom background colors if they exist in session state
        if role == "assistant" and "assistant_color" in st.session_state:
            with st.chat_message(role, avatar="🤖"):
                # Apply custom CSS with the selected color
                custom_css = f"""
                <style>
                    .stChatMessage [data-testid="stChatMessageContent"] {{
                        background-color: {st.session_state["assistant_color"]};
                    }}
                </style>
                """
                st.markdown(custom_css, unsafe_allow_html=True)
                st.markdown(message["content"])
        elif role == "user" and "user_color" in st.session_state:
            with st.chat_message(role, avatar="👤"):
                # Apply custom CSS with the selected color
                custom_css = f"""
                <style>
                    .stChatMessage [data-testid="stChatMessageContent"] {{
                        background-color: {st.session_state["user_color"]};
                    }}
                </style>
                """
                st.markdown(custom_css, unsafe_allow_html=True)
                st.markdown(message["content"])
        else:
            # Default styling
            with st.chat_message(role):
                st.markdown(message["content"])
    
    # Input area for new message
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append(format_message("user", prompt))
        
        # Display user message in chat interface with custom styling
        if "user_color" in st.session_state:
            with st.chat_message("user", avatar="👤"):
                # Apply custom CSS with the selected color
                custom_css = f"""
                <style>
                    .stChatMessage [data-testid="stChatMessageContent"] {{
                        background-color: {st.session_state["user_color"]};
                    }}
                </style>
                """
                st.markdown(custom_css, unsafe_allow_html=True)
                st.markdown(prompt)
        else:
            with st.chat_message("user"):
                st.markdown(prompt)
        
        # Initialize variable for storing the complete response
        full_response = ""
        
        # Display message container with custom styling
        if "assistant_color" in st.session_state:
            with st.chat_message("assistant", avatar="🤖"):
                # Apply custom CSS with the selected color
                custom_css = f"""
                <style>
                    .stChatMessage [data-testid="stChatMessageContent"] {{
                        background-color: {st.session_state["assistant_color"]};
                    }}
                </style>
                """
                st.markdown(custom_css, unsafe_allow_html=True)
                message_placeholder = st.empty()
        else:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
        
        # Get generation parameters from session state
        generation_params = {
            "max_tokens": st.session_state.get("max_tokens", 512),
            "temperature": st.session_state.get("temperature", 0.7),
            "top_p": st.session_state.get("top_p", 0.95),
            "top_k": st.session_state.get("top_k", 40),
            "repeat_penalty": st.session_state.get("repeat_penalty", 1.1),
            "frequency_penalty": st.session_state.get("frequency_penalty", 0.0),
            "presence_penalty": st.session_state.get("presence_penalty", 0.0),
        }
        
        # Create the full prompt from message history, with roleplay mode if enabled
        full_prompt = get_prompt_template(
            st.session_state.messages,
            roleplay_mode=st.session_state.get("roleplay_mode", False),
            persona=st.session_state.get("selected_persona", "helpful_assistant")
        )
        
        # Add a stop button with better styling
        col1, col2 = st.columns([3, 1])
        with col2:
            stop_button = st.button(
                "🛑 Stop Generation", 
                key="stop_generation",
                help="Click to stop the AI from generating more text",
                use_container_width=True
            )
        
        # Reset the stopped flag for new generation
        st.session_state["generation_stopped"] = False
        
        # Stream the response
        generating = True
        try:
            for response_chunk in model_manager.generate_response(
                full_prompt, 
                generation_params=generation_params,
                stream=True
            ):
                # Check if stop button was clicked
                if stop_button or st.session_state.get("generation_stopped", False):
                    st.session_state["generation_stopped"] = True
                    message_placeholder.markdown(full_response + " *(generation stopped)*")
                    generating = False
                    break
                
                full_response = response_chunk
                message_placeholder.markdown(full_response + "▌")
        except Exception as e:
            st.error(f"Error during generation: {str(e)}")
            generating = False
            
        # Only display the final response if generation completed normally
        if generating:
            message_placeholder.markdown(full_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append(format_message("assistant", full_response))

def show_upload_section(model_manager: ModelManager) -> None:
    """
    Display the model upload section.
    
    Args:
        model_manager: The ModelManager instance
    """
    st.header("Upload New Model")
    
    with st.expander("Upload GGUF Model", expanded=True):
        # Model file upload
        uploaded_file = st.file_uploader(
            "Upload GGUF model file (up to 10GB)",
            type=["gguf"],
            help="Upload a GGUF (GPT-Generated Unified Format) language model file. Maximum file size is 10GB."
        )
        
        # Optional custom name
        custom_name = st.text_input(
            "Custom model name (optional)",
            placeholder="Enter a name for your model"
        )
        
        # Upload button
        if uploaded_file is not None:
            if st.button("Process Upload", use_container_width=True):
                save_path = model_manager.upload_model(uploaded_file, custom_name)
                if save_path:
                    st.success(f"Model saved as {os.path.basename(save_path)}")
                    
                    # Ask if user wants to load the model
                    if st.button("Load Uploaded Model Now", use_container_width=True):
                        # Default parameters for model loading
                        params = {
                            "n_ctx": 2048,
                            "n_batch": 512,
                            "n_gpu_layers": 0,
                        }
                        success = model_manager.load_model(save_path, params)
                        if success:
                            st.success(f"Model loaded successfully: {os.path.basename(save_path)}")
                            st.rerun()
                        else:
                            st.error("Failed to load model")
                else:
                    st.error("Failed to save model")

def show_session_browser(session_handler: SessionHandler, model_manager: ModelManager) -> None:
    """
    Display the session browser for loading previous sessions.
    
    Args:
        session_handler: The SessionHandler instance
        model_manager: The ModelManager instance
    """
    if st.session_state.get("show_session_browser") or not st.session_state.get("model_loaded"):
        st.header("Session Browser")
        
        # Get available sessions
        available_sessions = session_handler.get_available_sessions()
        
        if not available_sessions:
            st.info("No saved sessions found. Start a new conversation and save it to see it here.")
            return
        
        # Display sessions in a table with actions
        for idx, session in enumerate(available_sessions):
            with st.expander(f"{session['name']} - {session['formatted_time']}"):
                st.text(f"Messages: {session['message_count']}")
                st.text(f"Model: {os.path.basename(session['model_path'])}")
                
                # Display roleplay information if enabled
                if session.get('roleplay_mode', False):
                    persona_options = {
                        "helpful_assistant": "Helpful Assistant",
                        "pirate": "Pirate",
                        "shakespeare": "Shakespeare",
                        "detective": "Detective",
                        "sci_fi_robot": "Sci-Fi Robot",
                        "medieval_scholar": "Medieval Scholar",
                        "cosmic_entity": "Cosmic Entity"
                    }
                    persona = persona_options.get(session.get('selected_persona', 'helpful_assistant'), 'Unknown Persona')
                    st.text(f"Roleplay Mode: Enabled - {persona}")
                
                # Show theme colors if available
                session_data = session_handler.load_session(session['file_path'])
                if session_data:
                    # Display theme information
                    if "theme_settings" in session_data:
                        theme = session_data.get("theme_settings", {})
                        with st.container():
                            st.markdown("#### Theme Settings")
                            colors_col1, colors_col2, colors_col3 = st.columns(3)
                            
                            with colors_col1:
                                st.markdown(f"<div style='background-color:{theme.get('primary_color', '#2A9D8F')}; height:20px; border-radius:4px;'></div>", unsafe_allow_html=True)
                                st.caption("Primary Color")
                            
                            with colors_col2:
                                st.markdown(f"<div style='background-color:{theme.get('assistant_color', '#E9ECEF')}; height:20px; border-radius:4px;'></div>", unsafe_allow_html=True)
                                st.caption("AI Messages")
                            
                            with colors_col3:
                                st.markdown(f"<div style='background-color:{theme.get('user_color', '#F0F7FF')}; height:20px; border-radius:4px;'></div>", unsafe_allow_html=True)
                                st.caption("User Messages")
                    
                    # Display saved presets information
                    if "user_presets" in session_data and session_data["user_presets"]:
                        user_presets = session_data.get("user_presets", {})
                        if user_presets:
                            st.markdown("#### Saved Style Presets")
                            
                            # Create a table-like display for presets
                            presets_table = """
                            | Preset Name | Description |
                            | ----------- | ----------- |
                            """
                            
                            # Add up to 5 presets to avoid cluttering the UI
                            preset_count = 0
                            for preset_key, preset_data in user_presets.items():
                                preset_name = preset_data.get("name", "Unknown")
                                preset_desc = preset_data.get("description", "")
                                # Truncate description if too long
                                if len(preset_desc) > 40:
                                    preset_desc = preset_desc[:37] + "..."
                                    
                                presets_table += f"| {preset_name} | {preset_desc} |\n"
                                preset_count += 1
                                if preset_count >= 5:
                                    break
                            
                            # Display the table
                            st.markdown(presets_table)
                            
                            # Indicate if there are more presets not shown
                            if len(user_presets) > preset_count:
                                st.caption(f"*and {len(user_presets) - preset_count} more presets...*")
                            
                            # Option to import these presets
                            if st.button(f"Import Presets ({len(user_presets)})", key=f"import_presets_{idx}"):
                                # Merge with current presets (imported ones override duplicates)
                                if "user_presets" not in st.session_state:
                                    st.session_state["user_presets"] = {}
                                
                                # Count how many new presets will be added
                                new_preset_count = sum(1 for key in user_presets if key not in st.session_state["user_presets"])
                                
                                # Merge presets
                                st.session_state["user_presets"] = {**st.session_state["user_presets"], **user_presets}
                                st.success(f"Successfully imported {new_preset_count} new presets!")
                                st.rerun()
                
                st.text(f"Preview: {session['preview']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Load Session", key=f"load_{idx}", use_container_width=True):
                        session_data = session_handler.load_session(session['file_path'])
                        if session_data:
                            # Apply the session to the current state
                            success = session_handler.apply_session(session_data)
                            if success:
                                st.success("Session loaded successfully!")
                                
                                # Check if we need to load the corresponding model
                                if session_data.get("model_path") and os.path.exists(session_data["model_path"]):
                                    if (not st.session_state.get("model_loaded") or 
                                        st.session_state.get("current_model_path") != session_data["model_path"]):
                                        st.info(f"This session uses model: {os.path.basename(session_data['model_path'])}")
                                        if st.button("Load Required Model", key=f"load_model_{idx}", use_container_width=True):
                                            success = model_manager.load_model(
                                                session_data["model_path"], 
                                                session_data.get("model_params", {})
                                            )
                                            if success:
                                                st.success("Model loaded successfully!")
                                                st.session_state.show_session_browser = False
                                                st.rerun()
                                            else:
                                                st.error("Failed to load the model for this session")
                                else:
                                    st.session_state.show_session_browser = False
                                    st.rerun()
                            else:
                                st.error("Failed to apply session")
                        else:
                            st.error("Failed to load session data")
                
                with col2:
                    if st.button("Delete Session", key=f"delete_{idx}", use_container_width=True):
                        success = session_handler.delete_session(session['file_path'])
                        if success:
                            st.success("Session deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete session")
