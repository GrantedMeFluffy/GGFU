import os
import time
import threading
from typing import Optional, Dict, Any, List, Tuple, Generator
import gc
import numpy as np
import streamlit as st
from llama_cpp import Llama

class ModelManager:
    """Enhanced class to handle GGUF model loading, unloading, and inference."""
    
    def __init__(self):
        self.model = None
        self.lock = threading.Lock()
        self.default_params = {
            "n_ctx": 2048,  # Increased default context window
            "n_batch": 512,  # Optimized batch size
            "n_threads": os.cpu_count(),  # Use all available CPU threads
            "n_gpu_layers": 0,  # GPU layer support
            "verbose": False
        }

    def load_model(self, model_path: str, parameters: Dict[str, Any] = None) -> bool:
        """
        Improved GGUF model loading with enhanced error handling and validation.
        
        Args:
            model_path: Path to the GGUF model file
            parameters: Dictionary of model parameters
            
        Returns:
            bool: Whether the model was loaded successfully
        """
        # Validate model file
        if not os.path.exists(model_path):
            st.error(f"Model file not found: {model_path}")
            return False
        
        if not model_path.lower().endswith('.gguf'):
            st.error(f"Invalid file type. Please use a .gguf model file: {model_path}")
            return False
        
        # Check file size and warn if too large
        file_size = os.path.getsize(model_path)
        if file_size > 20 * 1024 * 1024 * 1024:  # 20 GB threshold
            st.warning(f"Large model file detected ({file_size / (1024*1024*1024):.2f} GB). Loading may take some time.")
        
        # Merge default and provided parameters
        load_params = self.default_params.copy()
        if parameters:
            load_params.update(parameters)
        
        # Free any existing model to prevent memory leaks
        self.unload_model()
        
        try:
            # Enhanced loading with progress and timing
            start_time = time.time()
            
            # Show loading progress
            with st.spinner(f"Loading model from {os.path.basename(model_path)}..."):
                self.model = Llama(
                    model_path=model_path,
                    **load_params
                )
            
            # Calculate and log loading metrics
            load_time = time.time() - start_time
            model_size = file_size / (1024 * 1024)  # Convert to MB
            
            # Store model metadata in session state
            st.session_state.update({
                "current_model_path": model_path,
                "current_model_params": load_params,
                "model_loaded": True,
                "model_load_time": load_time,
                "model_file_size_mb": model_size
            })
            
            # Log successful model load
            st.success(f"Model loaded successfully in {load_time:.2f} seconds ({model_size:.2f} MB)")
            
            return True
        
        except Exception as e:
            # Comprehensive error handling
            error_details = str(e)
            st.error(f"Model loading failed: {error_details}")
            
            # Additional diagnostics
            if "insufficient memory" in error_details.lower():
                st.warning("Possible memory issue. Try reducing context size or GPU layers.")
            
            return False
    
    def unload_model(self) -> None:
        """Unload the current model and free memory."""
        with self.lock:
            if self.model is not None:
                del self.model
                self.model = None
                # Force garbage collection
                gc.collect()
                # Clear memory caches if possible
                try:
                    import torch
                    if hasattr(torch, 'cuda') and torch.cuda.is_available():
                        torch.cuda.empty_cache()
                except ImportError:
                    # Torch is not available, skip this step
                    pass
                st.session_state["model_loaded"] = False
                st.session_state["current_model_path"] = None
                st.session_state["current_model_params"] = None
    
    def generate_response(self, prompt: str, 
                          generation_params: Dict[str, Any] = None,
                          stream: bool = True):
        """
        Generate a response from the model for the given prompt.
        
        Args:
            prompt: The input prompt for the model
            generation_params: Dictionary of generation parameters
            stream: Whether to stream the response
            
        Returns:
            str: The generated response
        """
        if self.model is None:
            st.error("No model is loaded. Please load a model first.")
            return ""
        
        # Default generation parameters
        default_gen_params = {
            "max_tokens": 256,  # Reduced max tokens
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.05,
            "top_k": 40,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "stop": ["User:", "USER:", "<|user|>", "<|im_end|>"],
        }
        
        # Update with provided parameters
        if generation_params:
            default_gen_params.update(generation_params)
        
        with self.lock:
            try:
                if stream:
                    # For streaming output
                    response_text = ""
                    for token in self.model(
                        prompt,
                        stream=True,
                        **default_gen_params
                    ):
                        # Check if generation should be stopped
                        if st.session_state.get("generation_stopped", False):
                            break
                            
                        response_text += token["choices"][0]["text"]
                        # Yield the token for real-time display
                        yield response_text
                else:
                    # For non-streaming output
                    response = self.model(
                        prompt,
                        stream=False,
                        **default_gen_params
                    )
                    return response["choices"][0]["text"]
            except Exception as e:
                error_msg = f"Error generating response: {str(e)}"
                st.error(error_msg)
                return error_msg

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the currently loaded model.
        
        Returns:
            Dict: Dictionary containing model information
        """
        if self.model is None:
            return {"status": "No model loaded"}
        
        # Basic model info
        model_info = {
            "model_path": st.session_state.get("current_model_path", "Unknown"),
            "parameters": st.session_state.get("current_model_params", {}),
            "load_time": st.session_state.get("model_load_time", 0),
            "file_size_mb": st.session_state.get("model_file_size_mb", 0),
            "status": "Loaded"
        }
        
        return model_info

    def upload_model(self, uploaded_file, custom_name: Optional[str] = None) -> Optional[str]:
        """
        Upload a model file to the models directory.
        
        Args:
            uploaded_file: The uploaded file object
            custom_name: Optional custom name for the model file
            
        Returns:
            str: Path to the saved model file
        """
        if uploaded_file is None:
            return None
            
        # Create models directory if it doesn't exist
        os.makedirs("models", exist_ok=True)
        
        # Use custom name if provided, otherwise use the original filename
        if custom_name:
            filename = f"{custom_name}.gguf" if not custom_name.endswith(".gguf") else custom_name
        else:
            filename = uploaded_file.name
            
        # Sanitize filename for Windows compatibility
        filename = filename.replace(":", "_").replace("?", "_").replace("*", "_").replace('"', "_").replace("<", "_").replace(">", "_").replace("|", "_")
        
        # Save the file
        save_path = os.path.join("models", filename)
        
        # Show progress
        progress_text = "Uploading model file..."
        progress_bar = st.progress(0)
        
        with open(save_path, "wb") as f:
            # Get file size
            file_size = len(uploaded_file.getvalue())
            chunk_size = 1024 * 1024  # 1MB chunks
            
            # Read and write in chunks to show progress
            bytes_remaining = file_size
            data = uploaded_file.getvalue()
            i = 0
            while bytes_remaining > 0:
                chunk = min(chunk_size, bytes_remaining)
                f.write(data[i:i+chunk])
                i += chunk
                bytes_remaining -= chunk
                # Update progress
                progress = (file_size - bytes_remaining) / file_size
                progress_bar.progress(progress)
                time.sleep(0.01)  # Small delay to show progress
        
        # Complete progress
        progress_bar.progress(1.0)
        
        return save_path

    def get_available_models(self) -> List[str]:
        """
        Get a list of available model files in the models directory.
        
        Returns:
            List[str]: List of model file paths
        """
        # Create models directory if it doesn't exist
        os.makedirs("models", exist_ok=True)
        
        # Get all .gguf files in the models directory
        model_files = [
            os.path.join("models", f) for f in os.listdir("models") 
            if f.endswith(".gguf")
        ]
        
        return model_files
