from docx import Document
from groq import Groq
import os
from dotenv import load_dotenv
import pyttsx3
from pynput import keyboard
import threading
import sys

# Load environment variables
load_dotenv()

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Global flag for speech interruption
speaking = False

def on_press(key):
    global speaking
    speaking = False
    return False  # Stop listener

def speak(text):
    global speaking
    speaking = True
    
    # Create a thread for the keyboard listener
    def keyboard_listener():
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
    
    # Create and start the keyboard listener thread
    listener_thread = threading.Thread(target=keyboard_listener)
    listener_thread.daemon = True
    listener_thread.start()
    
    # Split text into sentences or chunks for more responsive interruption
    chunks = text.split('.')
    
    for chunk in chunks:
        if not speaking:
            engine.stop()
            break
        
        if chunk.strip():  # Only speak non-empty chunks
            engine.say(chunk.strip())
            engine.runAndWait()
            
        if not speaking:
            engine.stop()
            break

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def read_docx(filename):
    try:
        if filename.endswith(".docx"):
            return Document(filename)
        elif filename.endswith(".txt"):
            with open(filename, "r+") as file:
                return file.read()
    except Exception as e:
        print("Error reading file.",e)

def write_docx(file_path, content):
    """Writes content to a .docx file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")
        raise FileNotFoundError

def doc_operations(document, command):
    """Processes the document content with Groq API."""
    prompt = [
        {
            "role": "system",
            "content": '''Given a document and a specified operation, apply the operation to the document and return only the updated text. Do not include any explanations or extra information.
            If it is only a blank audio for command. Just return the original document. Do the same for read document command.'''
        },
        {"role": "user", "content": f"{document}\n\nOperation:\n{command}"}
    ]

    try:
        response = client.chat.completions.create(
            messages=prompt,
            model="llama3-70b-8192"
        )
        
        result = response.choices[0].message.content.strip()
        return result
    
    except Exception as e:
        print(f"Error during API call: {e}")
        return None

def doc_reading(command):
    prompt = [
        {
            "role": "system",
            "content": '''Extract the filename with its extension from the given command. If a full file path is provided, return the entire file path including the extension. Respond with only the result, no additional text or explanation.
            Eg: Command: Open my text file food. response: food.txt
            open file sunrize dot txt. Response: sunrize.txt
            Open my document money. response : money.docx'''
        },
        {"role": "user", "content": command}
    ]

    try:
        response = client.chat.completions.create(
            messages=prompt,
            model="llama3-70b-8192"
        )
        
        result = response.choices[0].message.content.strip()
        return result
    
    except Exception as e:
        print(f"Error during API call: {e}")
        return None

def doc_main(command, speech_recog):
    speak("You are now in document editor mode. Say Exit in the end to close the document after all your changes.")
    filename = doc_reading(command)
    print(f"Filename is {filename}\n")

    while True:
        try:
            document_content = read_docx(filename=filename)
            if document_content is None:
                speak("There is no content to read. What would you like to do?")
            else:
                speak("Document is now open, what would you like to do")
        except:
                speak("Error reading file")
                return
        

        speech_recog.record_audio("audio_sample.wav", duration=7)
        command = speech_recog.process_audio_with_whisper("audio_sample.wav")
        print(command)

        if "exit" in command.lower() or "close document" in command.lower():
            return

        # Perform operation
        elif 'read' in command.lower():
            speak(document_content)
        else:
            updated_content = doc_operations(document_content, command)
        if updated_content is None:
            speak("Operation failed.")
        elif "summary" in command.lower() or "summarize" in command.lower():
            speak(updated_content)
        elif updated_content != None:
            write_docx(filename, updated_content)
            speak(f"File '{filename}' has been updated.")

if __name__ == "__main__":
    file_path = "test/text.txt"  # Update to the actual path
    command = "Change sun to moon"

    # Read document
    document_content = read_docx(file_path)
    speak(document_content)