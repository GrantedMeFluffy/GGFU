# GGUF Model Chat Application

A Streamlit-based application for uploading, loading, and chatting with GGUF language models, with memory management and session persistence features.

## Features

- **Model Management**: Upload, load, and unload GGUF models (up to 10GB)
- **Chat Interface**: Interact with loaded models through a user-friendly chat interface
- **Session Persistence**: Save and load chat sessions for later continuation
- **Memory Management**: Efficiently manage model loading/unloading to control memory usage
- **Roleplay Mode**: Make the AI adopt different personas with 7 built-in character options
- **Windows Compatibility**: Fully compatible with Windows, macOS, and Linux
- **Parameter Controls**: Adjust generation parameters like temperature, max tokens, etc.

## Supported Personas (Roleplay Mode)

- **Helpful Assistant**: Standard helpful AI assistant
- **Pirate**: Salty sea pirate with nautical language
- **Shakespeare**: Responses in Elizabethan English with poetic flourishes
- **Detective**: Hard-boiled noir detective style
- **Sci-Fi Robot**: Futuristic AI with technical terminology
- **Medieval Scholar**: 12th century philosopher with archaic language
- **Cosmic Entity**: Mysterious entity speaking about cosmic phenomena

## How to Use

1. **Upload a Model**:
   - Use the "Upload New Model" section to upload a GGUF file
   - Optionally provide a custom name for your model

2. **Load a Model**:
   - Select an uploaded model from the sidebar dropdown
   - Adjust model parameters as needed (context length, batch size, GPU layers)
   - Click "Load Selected Model"

3. **Chat with the Model**:
   - Once a model is loaded, use the chat interface to send messages
   - View the model's responses in real-time

4. **Save and Load Sessions**:
   - Save your current chat session using the sidebar option
   - Browse and load previously saved sessions

5. **Roleplay Mode**:
   - Enable roleplay mode in the sidebar
   - Select a persona from the dropdown menu
   - The model will respond in the style of the selected persona

## Technical Details

- Built with Streamlit and llama-cpp-python
- Optimized for efficiency with adjustable parameters
- Saves sessions as JSON files for easy management
- Supports GGUF (GGML Unified Format) models for optimized inference

## Requirements

- Python 3.8+
- Required packages: llama-cpp-python, numpy, streamlit

## Project Structure

- `app.py`: Main Streamlit application
- `model_manager.py`: Handles GGUF model loading and operations
- `session_handler.py`: Manages saving and loading of chat sessions
- `components.py`: UI components for the application interface
- `utils.py`: Utility functions and roleplay persona definitions
- `.streamlit/config.toml`: Streamlit configuration

## Tips for Best Performance

- Larger models require more RAM, so choose models appropriate for your system
- Unload models when not in use to free up memory
- Adjust context length based on your use case (larger context = more memory usage)
- For improved performance on compatible hardware, increase GPU layers