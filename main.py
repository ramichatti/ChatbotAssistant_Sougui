"""
Sougui DWH Chatbot - Main Entry Point
A desktop chatbot application using Ollama LLM to query SQL Server database
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ui.chatbot_ui import ChatbotUI

def main():
    print("Starting Sougui DWH Chatbot...")
    print("Ollama Model: llama3.1:latest")
    print("Database: Sougui_DWH")
    print()
    
    try:
        app = ChatbotUI()
        print("UI initialized successfully!")
        print("Opening window...")
        app.run()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
