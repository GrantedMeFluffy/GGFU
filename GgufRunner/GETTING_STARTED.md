# Getting Started with GGUF Model Chat

This guide will help you get up and running with the GGUF Model Chat application.

## Prerequisites

- Python 3.8 or higher
- Basic knowledge of language models (LLMs)
- A GGUF model file (or you can download one later)

## Installation

1. Clone this repository or fork it on Replit
2. Install the required dependencies:
   ```
   pip install llama-cpp-python numpy streamlit
   ```
3. Start the application:
   ```
   streamlit run app.py
   ```

## First Steps

### 1. Obtaining a GGUF Model

If you don't already have a GGUF model, you can download one from:
- [Hugging Face](https://huggingface.co/models?search=gguf)
- [TheBloke's GGUF models](https://huggingface.co/TheBloke)

Popular models include:
- Llama 2
- Mistral
- Phi
- Gemma

Look for files with the `.gguf` extension. Start with smaller models (1-3B parameters) if you have limited RAM.

### 2. Uploading Your Model

1. In the application, go to the "Upload New Model" section
2. Click "Browse files" and select your GGUF model file
3. Optionally, enter a custom name for your model
4. Click "Process Upload"
5. After uploading, click "Load Uploaded Model Now"

### 3. Starting a Chat

Once your model is loaded:
1. Type a message in the chat input box at the bottom of the screen
2. Press Enter to send your message
3. Wait for the model to generate a response

### 4. Adjusting Settings

In the sidebar, you can adjust various settings:
- **Model Parameters**: Context length, batch size, GPU layers
- **Generation Settings**: Temperature, max tokens, top-p, etc.
- **Roleplay Mode**: Enable/disable different AI personas

### 5. Saving Your Session

To save your chat session:
1. In the sidebar, enter an optional name for your session
2. Click "Save Current Session"
3. Your session will be saved and can be loaded later

## Troubleshooting

### Common Issues

- **Out of Memory Error**: Try using a smaller model or reducing the context length
- **Slow Response Time**: Adjust batch size or reduce max tokens for generation
- **Model Won't Load**: Check that your file is a valid GGUF format

### Need Help?

Refer to the README.md file for more detailed information, or open an issue on GitHub.