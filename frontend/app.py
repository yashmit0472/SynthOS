import customtkinter as ctk
import keyboard
import threading
import requests
import json
import time

# Configuration
API_URL = "http://127.0.0.1:8000/query"
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class NexisApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Nexis")
        self.geometry("600x400")
        self.attributes("-topmost", True)
        self.overrideredirect(True) # Remove windows borders/titlebar
        
        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

        # Hide initially
        self.withdraw()
        self.is_visible = False

        self.setup_ui()
        self.setup_hotkey()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Input area
        self.input_entry = ctk.CTkEntry(
            self, 
            placeholder_text="Ask Nexis...", 
            height=50, 
            font=("Segoe UI", 20),
            border_width=0,
            corner_radius=8
        )
        self.input_entry.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.input_entry.bind("<Return>", self.handle_query)
        self.input_entry.bind("<Escape>", lambda e: self.hide_window())

        # Output area
        self.output_textbox = ctk.CTkTextbox(
            self, 
            font=("Segoe UI", 14),
            wrap="word",
            corner_radius=8
        )
        self.output_textbox.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.output_textbox.configure(state="disabled")

    def setup_hotkey(self):
        # We run the hotkey listener in a separate thread so it doesn't block the GUI
        def listen_hotkey():
            keyboard.add_hotkey('ctrl+space', self.toggle_window)
            keyboard.wait()
            
        thread = threading.Thread(target=listen_hotkey, daemon=True)
        thread.start()

    def toggle_window(self):
        if self.is_visible:
            self.hide_window()
        else:
            self.show_window()

    def show_window(self):
        self.deiconify()
        self.lift()
        self.focus_force()
        self.input_entry.focus()
        self.is_visible = True

    def hide_window(self):
        self.withdraw()
        self.is_visible = False
        self.input_entry.delete(0, 'end')

    def append_output(self, text):
        self.output_textbox.configure(state="normal")
        self.output_textbox.insert("end", text + "\n\n")
        self.output_textbox.see("end")
        self.output_textbox.configure(state="disabled")

    def clear_output(self):
        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.configure(state="disabled")

    def handle_query(self, event=None):
        query = self.input_entry.get().strip()
        if not query:
            return

        self.clear_output()
        self.append_output(f"Thinking about: '{query}'...")
        
        # Run API call in a thread to keep GUI responsive
        threading.Thread(target=self.api_call, args=(query,), daemon=True).start()

    def api_call(self, query):
        try:
            start = time.time()
            response = requests.post(API_URL, json={"question": query}, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            self.clear_output()
            
            mode = data.get("mode", "UNKNOWN")
            self.append_output(f"[Mode: {mode}] ({time.time()-start:.1f}s)")
            
            if mode == "FILE_SEARCH":
                results = data.get("results", [])
                if not results:
                    self.append_output("No matching files found.")
                else:
                    for i, r in enumerate(results[:1]):
                        self.append_output(f"{i+1}. {r.get('filename')}\nPath: {r.get('path')}\nSnippet: {r.get('snippet')}")
            
            else:
                answer = data.get("final_answer", json.dumps(data, indent=2))
                self.append_output(answer)
                
                if mode == "DECISION":
                    conf = data.get("confidence_score")
                    self.append_output(f"\nConfidence: {conf}")
                    
        except requests.exceptions.ConnectionError:
            self.clear_output()
            self.append_output("Error: Could not connect to backend. Is uvicorn running?")
        except Exception as e:
            self.clear_output()
            self.append_output(f"Error: {e}")

if __name__ == "__main__":
    app = NexisApp()
    app.mainloop()
