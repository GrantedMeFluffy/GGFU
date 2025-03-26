import tkinter as tk
from tkinter import ttk, scrolledtext
from llama_cpp import Llama
import json
import os
from datetime import datetime

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GGUF Chat")

        # Settings Frame
        self.settings_frame = ttk.LabelFrame(root, text="Model Settings")
        self.settings_frame.pack(padx=10, pady=5, fill='x')

        # Temperature setting
        temp_frame = ttk.Frame(self.settings_frame)
        temp_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(temp_frame, text="Temperature:").pack(side='left')
        self.temperature = ttk.Scale(temp_frame, from_=0.0, to=2.0, orient='horizontal')
        self.temperature.set(0.7)
        self.temperature.pack(side='left', expand=True, fill='x', padx=5)

        # Max tokens setting
        tokens_frame = ttk.Frame(self.settings_frame)
        tokens_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(tokens_frame, text="Max Tokens:").pack(side='left')
        self.max_tokens = ttk.Scale(tokens_frame, from_=64, to=2048, orient='horizontal')
        self.max_tokens.set(512)
        self.max_tokens.pack(side='left', expand=True, fill='x', padx=5)

        # Roleplay Frame
        self.roleplay_frame = ttk.LabelFrame(root, text="Roleplay Mode")
        self.roleplay_frame.pack(padx=10, pady=5, fill='x')

        # Roleplay Enable/Disable
        self.roleplay_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.roleplay_frame, text="Enable Roleplay", variable=self.roleplay_var).pack(padx=5, pady=2)

        # Persona Selection
        self.personas = {
            "helpful_assistant": "Helpful Assistant",
            "pirate": "Pirate",
            "shakespeare": "Shakespeare",
            "detective": "Detective",
            "sci_fi_robot": "Sci-Fi Robot",
            "medieval_scholar": "Medieval Scholar",
            "cosmic_entity": "Cosmic Entity"
        }
        self.persona_var = tk.StringVar(value="helpful_assistant")
        persona_combo = ttk.Combobox(self.roleplay_frame, textvariable=self.persona_var, values=list(self.personas.values()))
        persona_combo.pack(padx=5, pady=2, fill='x')

        # Chat display
        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20)
        self.chat_display.pack(padx=10, pady=10, expand=True, fill='both')

        # Input area
        self.input_frame = ttk.Frame(root)
        self.input_frame.pack(padx=10, pady=(0,10), fill='x')

        self.message_entry = ttk.Entry(self.input_frame)
        self.message_entry.pack(side='left', expand=True, fill='x', padx=(0,10))

        self.send_button = ttk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side='right')

        # Session controls
        self.session_frame = ttk.Frame(root)
        self.session_frame.pack(padx=10, pady=5, fill='x')

        ttk.Button(self.session_frame, text="Save Session", command=self.save_session).pack(side='left', padx=5)
        ttk.Button(self.session_frame, text="Load Session", command=self.load_session).pack(side='left', padx=5)

        #Eject and Stop Buttons
        self.eject_button = ttk.Button(self.session_frame, text="Eject Model", command=self.eject_model)
        self.eject_button.pack(side='left', padx=5)
        self.stop_button = ttk.Button(self.session_frame, text="Stop Chat", command=self.stop_chat)
        self.stop_button.pack(side='left', padx=5)


        # Bind Enter key to send
        self.message_entry.bind('<Return>', lambda e: self.send_message())

        # Model Selection Frame
        self.model_frame = ttk.LabelFrame(root, text="Model Selection")
        self.model_frame.pack(padx=10, pady=5, fill='x')
        
        # Add button to select model file
        self.select_model_button = ttk.Button(self.model_frame, text="Select GGUF Model", command=self.select_model)
        self.select_model_button.pack(padx=5, pady=2)
        
        self.model = None
        self.eject_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.chat_display.insert(tk.END, "Please select a GGUF model file to begin.\n\n")

    def save_session(self):
        # Create sessions directory if it doesn't exist
        os.makedirs("sessions", exist_ok=True)

        # Get chat content
        chat_content = self.chat_display.get("1.0", tk.END)

        # Create session data
        session_data = {
            "chat_content": chat_content,
            "temperature": self.temperature.get(),
            "max_tokens": self.max_tokens.get(),
            "roleplay_enabled": self.roleplay_var.get(),
            "selected_persona": self.persona_var.get()
        }

        # Save to file
        filename = f"sessions/chat_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(session_data, f)

        self.chat_display.insert(tk.END, f"\nSession saved to {filename}\n\n")
        self.chat_display.see(tk.END)

    def load_session(self):
        if not os.path.exists("sessions"):
            self.chat_display.insert(tk.END, "\nNo saved sessions found.\n\n")
            return

        files = [f for f in os.listdir("sessions") if f.endswith('.json')]
        if not files:
            self.chat_display.insert(tk.END, "\nNo saved sessions found.\n\n")
            return

        # Create a new window for session selection
        select_window = tk.Toplevel(self.root)
        select_window.title("Select Session")
        select_window.geometry("300x400")

        # Create listbox
        listbox = tk.Listbox(select_window)
        listbox.pack(padx=10, pady=10, fill='both', expand=True)

        # Add files to listbox
        for file in files:
            listbox.insert(tk.END, file)

        def load_selected():
            selection = listbox.curselection()
            if selection:
                filename = files[selection[0]]
                with open(f"sessions/{filename}", 'r') as f:
                    session_data = json.load(f)

                # Clear current chat
                self.chat_display.delete("1.0", tk.END)

                # Load chat content
                self.chat_display.insert(tk.END, session_data["chat_content"])

                # Load settings
                self.temperature.set(session_data["temperature"])
                self.max_tokens.set(session_data["max_tokens"])
                self.roleplay_var.set(session_data["roleplay_enabled"])
                self.persona_var.set(session_data["selected_persona"])

                select_window.destroy()
                self.chat_display.insert(tk.END, f"\nSession loaded from {filename}\n\n")
                self.chat_display.see(tk.END)

        # Add load button
        ttk.Button(select_window, text="Load Selected Session", command=load_selected).pack(pady=10)

    def send_message(self):
        message = self.message_entry.get().strip()
        if not message:
            return

        # Clear input
        self.message_entry.delete(0, tk.END)

        # Display user message
        self.chat_display.insert(tk.END, f"You: {message}\n")

        if self.model:
            # Get AI response with settings
            response = self.model.create_completion(
                message,
                temperature=self.temperature.get(),
                max_tokens=int(self.max_tokens.get())
            )
            ai_message = response['choices'][0]['text'].strip()

            # Display AI response
            self.chat_display.insert(tk.END, f"\nAI: {ai_message}\n\n")
        else:
            self.chat_display.insert(tk.END, "\nError: Model not loaded\n\n")

        # Scroll to bottom
        self.chat_display.see(tk.END)

    def eject_model(self):
        self.model = None
        self.chat_display.insert(tk.END, "\nModel ejected.\n\n")
        self.eject_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def stop_chat(self):
        self.chat_display.insert(tk.END, "\nChat stopped.\n\n")
        self.stop_button.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def select_model(self):
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Select GGUF Model",
            filetypes=[("GGUF files", "*.gguf"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.model = Llama(filename)
                self.chat_display.insert(tk.END, f"Model loaded: {filename}\n\n")
                self.eject_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.NORMAL)
            except Exception as e:
                self.chat_display.insert(tk.END, f"Error loading model: {str(e)}\n\n")
                self.model = None
                self.eject_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.DISABLED)
            self.chat_display.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()