import os
import sqlite3
import pyttsx3
import ollama
import speech_recognition as sr
from fuzzywuzzy import process
from docreader import edit_document


# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Database Initialization and File Indexing
class FileIndexer:
    def __init__(self, db_name="file_index.db"):
        self.db_name = db_name
        self.initialize_database()

    def initialize_database(self):
        """Creates a database to index system files."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY, name TEXT, path TEXT)''')
        conn.commit()
        conn.close()

    def index_files(self):
        """Indexes all files in the system."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        for root, dirs, files in os.walk("C:\\"):  # Change path as needed
            for file in files:
                cursor.execute("INSERT INTO files (name, path) VALUES (?, ?)", (file, os.path.join(root, file)))
        conn.commit()
        conn.close()

# Microphone Handling
class MicrophoneHandler:
    def list_microphones(self):
        """Lists all available microphones."""
        mic_list = sr.Microphone.list_microphone_names()
        print("Available microphones:")
        for i, microphone_name in enumerate(mic_list):
            print(f"{i}: {microphone_name}")
        return mic_list

    def select_microphone(self):
        """Prompts the user to select a microphone by index."""
        mic_list = self.list_microphones()
        try:
            mic_index = int(input("Enter the microphone index you want to use: "))
            if mic_index >= 0 and mic_index < len(mic_list):
                return mic_index
            else:
                print("Invalid index, using the default microphone.")
                return None
        except ValueError:
            print("Invalid input, using the default microphone.")
            return None

# Speech Handling Functions
def speak(text):
    """Converts text to speech."""
    engine.say(text)
    engine.runAndWait()

def listen(mic_index=None):
    """Listens to the user's voice input using the selected microphone."""
    recognizer = sr.Recognizer()
    mic = sr.Microphone(device_index=mic_index) if mic_index is not None else sr.Microphone()
    with mic as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.")
        except sr.RequestError:
            speak("Sorry, there was a network error.")
    return ""

# LLM Interface
def interact_with_ollama(prompt):
    """Sends the user prompt to Ollama and receives a CLI command."""
    try:
        stream = ollama.chat(
            model='llama3.1:8b',
            messages=[{'role': 'user', 'content': prompt}],
            stream=True
        )
        response = ""
        for chunk in stream:
            response += chunk['message']['content']
        print("Response from interact with Ollama:", response.strip())
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Sorry, something went wrong."
    

# Intent Classification
def get_intent(command):
    """Determines intent of user command."""
    prompt = f"Classify this command as one of the following: 'changedirectory', 'list', or 'search'. Reply with only one word from this list, without any extra text, punctuation, or phrases, based on the command given after the colon:'{command}'"
    # print the intent
    response = interact_with_ollama(prompt)

    return response.strip().lower()

# Command Execution Functions
def change_directory(command):
    """Executes a 'change directory' command."""
    directory = interact_with_ollama(command)
    print("Directory to change to:", directory)
    try:
        os.chdir(directory)
        current_dir = os.getcwd()
        speak(f"Changed directory to {current_dir}")
        return current_dir
    except Exception as e:
        speak(f"Error changing directory: {e}")
        return f"Error: {e}"

def list_files():
    """Lists files in the current directory."""
    try:
        files = os.listdir()
        result = "\n".join(files) if files else "No files found in this directory."
        speak(f"Files in current directory are: {result}")
        return result
    except PermissionError:
        speak("Permission denied. Unable to list the contents of this directory.")
        return "Error: Permission denied."

def search_files(query):
    """Searches indexed files using a query."""
    conn = sqlite3.connect("file_index.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, path FROM files")
    files = cursor.fetchall()
    conn.close()

    search_term = " ".join(query.split()[1:])
    matched_files = process.extract(search_term, [file[0] for file in files], limit=5)
    results = []

    for match in matched_files:
        file_name, path = next((f for f in files if f[0] == match[0]), (None, None))
        if path:
            results.append(f"{file_name} located at {path}")
            speak(f"{file_name} located at {path}")

    return "\n".join(results) if results else "No matching files found."

# Command Routing
def execute_command(command):
    """Routes the command based on intent."""
    intent = get_intent(command)
    print("Intent:", intent)
    if intent == "changedirectory":
        print("I am in the change directory intent")
        # chance directory prompt for llama to take into account we are using os.chdir("") and want what we want to put in the brackets
        command = f"Translate the following request into only the directory path needed for os.chdir, without any extra words, explanations, or punctuation: '{command}'"
        return change_directory(command)
    elif intent == "list":
        # list files prompt for llama to take into account we are using os.listdir() and want what we want to put in the brackets
        command = f"Translate the following request into a command suitable for os.listdir(): '{command}'"
        return list_files()
    elif intent == "search":
        # search files prompt for llama to take into account we are using the search function and want what we want to put in the brackets
        command = f"Translate the following request into a search query: '{command}'"
        return search_files(command)
    elif intent == "read":
        # Handle document reading command
        document_name = command.split("read")[-1].strip()  # Extract document name from command
        file_path = search_files(document_name)  # Search for the document in the indexed files
        
        if file_path:
            return edit_document(file_path)  # Call the document reader function
        else:
            speak("Document not found.")
            return "Document not found."
    else:
        speak("Sorry, I can only execute 'cd', 'ls', or 'search' commands.")
        return "Invalid command"

# Main Pipeline
def main():
    indexer = FileIndexer()
    mic_handler = MicrophoneHandler()
    mic_index = mic_handler.select_microphone()  # Select microphone

    speak("Hello! I am ready to assist you with basic command line tasks. Please tell me what you want to do.")
    
    while True:
        user_command = listen(mic_index)
        if "exit" in user_command:
            speak("Goodbye!")
            break

        result = execute_command(user_command)
        print(result)
        if result:
            speak(result)

if __name__ == "__main__":
    main()




