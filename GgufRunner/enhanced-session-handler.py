import os
import json
import time
import datetime
import hashlib
from typing import Optional, Dict, Any, List
import streamlit as st

class SessionHandler:
    """Class to handle chat session saving and loading with enhanced stability."""
    
    def __init__(self, sessions_dir: str = "sessions"):
        self.sessions_dir = sessions_dir
        self.max_sessions = 50  # Limit total number of saved sessions
        self.max_session_size_mb = 10  # Maximum session file size
        
        # Create the sessions directory with proper permissions
        try:
            os.makedirs(self.sessions_dir, exist_ok=True)
            # Set restrictive permissions if possible
            try:
                os.chmod(self.sessions_dir, 0o700)  # Read, write, execute for owner only
            except Exception:
                pass  # Ignore permission setting errors
        except Exception as e:
            st.error(f"Critical error creating sessions directory: {e}")
            raise
    
    def _validate_session_data(self, session_data: Dict[str, Any]) -> bool:
        """
        Validate the integrity of session data before saving.
        
        Args:
            session_data: Session data to validate
            
        Returns:
            bool: Whether the session data is valid
        """
        try:
            # Check for critical components
            required_keys = ['messages', 'timestamp']
            for key in required_keys:
                if key not in session_data:
                    st.warning(f"Missing critical session data: {key}")
                    return False
            
            # Validate messages
            if not isinstance(session_data['messages'], list):
                st.warning("Invalid messages format")
                return False
            
            # Limit message count
            session_data['messages'] = session_data['messages'][:500]
            
            return True
        except Exception as e:
            st.error(f"Session data validation error: {e}")
            return False
    
    def _manage_session_count(self):
        """
        Manage the number of saved sessions, removing oldest if exceeding limit.
        """
        try:
            sessions = self.get_available_sessions()
            
            # If we're over the max session count, remove oldest sessions
            if len(sessions) >= self.max_sessions:
                # Sort sessions by timestamp (oldest first)
                sessions.sort(key=lambda x: x['timestamp'])
                
                # Remove excess sessions
                for session in sessions[:-self.max_sessions + 1]:
                    try:
                        os.unlink(session['file_path'])
                    except Exception as e:
                        st.warning(f"Could not remove old session: {e}")
        except Exception as e:
            st.error(f"Error managing session count: {e}")
    
    def save_session(self, name: Optional[str] = None) -> str:
        """
        Save the current chat session to a file with enhanced stability.
        
        Args:
            name: Optional custom name for the session
            
        Returns:
            str: Path to the saved session file
        """
        # Sanitize filename more aggressively
        if not name:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"Session_{timestamp}"
        
        # More robust filename sanitization
        name = "".join(c for c in name if c.isalnum() or c in ['_', '-', '.'])[:50]
        
        if not name.endswith(".json"):
            name = f"{name}.json"
        
        # Create session data
        session_data = {
            "timestamp": time.time(),
            "formatted_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model_path": st.session_state.get("current_model_path", ""),
            "model_params": st.session_state.get("current_model_params", {}),
            "messages": st.session_state.get("messages", []),
            "roleplay_mode": st.session_state.get("roleplay_mode", False),
            "selected_persona": st.session_state.get("selected_persona", "helpful_assistant"),
            # Save generation parameters
            "generation_params": {
                "temperature": st.session_state.get("temperature", 0.7),
                "max_tokens": st.session_state.get("max_tokens", 512),
                "top_p": st.session_state.get("top_p", 0.95),
                "top_k": st.session_state.get("top_k", 40),
                "repeat_penalty": st.session_state.get("repeat_penalty", 1.1),
                "frequency_penalty": st.session_state.get("frequency_penalty", 0.0),
                "presence_penalty": st.session_state.get("presence_penalty", 0.0),
            },
            # Save theme settings
            "theme_settings": {
                "primary_color": st.session_state.get("primary_color", "#2A9D8F"),
                "assistant_color": st.session_state.get("assistant_color", "#E9ECEF"),
                "user_color": st.session_state.get("user_color", "#F0F7FF"),
            },
            # Save user presets
            "user_presets": st.session_state.get("user_presets", {}),
            "metadata": {
                "name": name,
                "session_id": hashlib.md5(
                    f"{time.time()}{name}".encode()
                ).hexdigest()
            }
        }
        
        # Validate session data
        if not self._validate_session_data(session_data):
            st.error("Session data failed validation")
            return ""
        
        # Manage session count
        self._manage_session_count()
        
        # Save to file
        file_path = os.path.join(self.sessions_dir, name)
        
        # Temporary file for atomic write
        temp_path = file_path + '.tmp'
        
        try:
            with open(temp_path, "w") as f:
                json.dump(session_data, f, indent=2)
            
            # Atomic rename
            os.replace(temp_path, file_path)
        except Exception as e:
            st.error(f"Error saving session: {e}")
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            return ""
        
        return file_path
    
    def load_session(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Load a chat session from a file with enhanced error handling.
        
        Args:
            file_path: Path to the session file to load
            
        Returns:
            Dict: The loaded session data
        """
        if not os.path.exists(file_path):
            st.error(f"Session file not found: {file_path}")
            return None
        
        try:
            # Check file size before loading
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > self.max_session_size_mb:
                st.error(f"Session file too large: {file_size_mb:.2f} MB")
                return None
            
            with open(file_path, "r") as f:
                # Use safe loading to prevent potential code execution
                session_data = json.load(f)
            
            # Validate loaded data
            if not self._validate_session_data(session_data):
                st.error("Loaded session data is invalid")
                return None
            
            return session_data
        
        except json.JSONDecodeError:
            st.error(f"Corrupted session file: {file_path}")
            return None
        except Exception as e:
            st.error(f"Error loading session: {str(e)}")
            return None
    
    # Existing methods remain the same: apply_session, get_available_sessions, 
    # _generate_preview, delete_session (from the original implementation)
    
    def apply_session(self, session_data: Dict[str, Any]) -> bool:
        """
        Apply a loaded session to the current Streamlit session state.
        
        Args:
            session_data: The session data to apply
            
        Returns:
            bool: Whether the session was applied successfully
        """
        # Existing implementation from the original code
        if not session_data:
            return False
        
        try:
            # Existing session application logic
            # ... [rest of the existing apply_session method remains unchanged]
            
            return True
        except Exception as e:
            st.error(f"Error applying session: {str(e)}")
            return False
    
    # [All other existing methods from the original implementation remain the same]
