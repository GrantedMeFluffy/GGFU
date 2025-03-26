import sys
import logging
from llama_cpp import Llama

# Configure logging for more detailed output
logging.basicConfig(level=logging.DEBUG)

def load_model(model_path):
    try:
        print(f"Attempting to load model from: {model_path}")
        
        # Expanded model loading parameters
        model = Llama(
            model_path=model_path, 
            n_ctx=4096,           # Increased context window
            n_batch=1024,         # Increased batch size
            n_gpu_layers=-1,      # Use all GPU layers if available
            verbose=True          # Detailed loading information
        )
        
        print("Model loaded successfully!")
        
        # More robust inference test
        test_prompts = [
            "Hello, how are you?",
            "Can you introduce yourself?",
            "What is your primary function?"
        ]
        
        for prompt in test_prompts:
            print(f"\nTesting prompt: {prompt}")
            try:
                output = model(prompt, max_tokens=100)
                print("Model output:")
                print(output)
            except Exception as inference_error:
                print(f"Inference error: {inference_error}")
        
        return model
    
    except Exception as e:
        print(f"Error loading model: {e}")
        print(f"Error type: {type(e)}")
        print(f"Detailed error info: {sys.exc_info()}")
        return None

# Replace with your actual model path
MODEL_PATH = r"C:\Users\blanc\OneDrive\Desktop\Coding-AI\Copies of AI models and Sets\New folder\MN-12B-Celeste-V1.9-Q4_K_S.gguf"

if __name__ == "__main__":
    model = load_model(MODEL_PATH)
