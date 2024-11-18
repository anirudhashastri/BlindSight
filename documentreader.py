from docx import Document
from groq import Groq
import os
from dotenv import load_dotenv
import pyttsx3
from pynput import keyboard
import threading
import sys
import re
# Load environment variables
load_dotenv()

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Global flag for speech interruption
speaking = False
summary_regex = r"(?i)(summary|summarize)"
exit_regex = r"^(?i)(exit|close document)"

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
            "content": '''Given a document and a specified operation, apply the operation to the document and return only the entire updated text. Do not include any explanations or extra information.
            If it is only a blank audio for command. Just return the original document. If unable to perform said operation, respond only with "Operation failed". Do not include any explanations or extra information.
            '''
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
            "content": '''
Extract the filename with its extension from the given command. If a full file path is provided, return the entire file path including the extension. 
            Respond with only the result, no additional text or explanation. Examples:

    Command: Open my text file food. Response: food.txt
    Command: Open file sunrise dot txt. Response: sunrise.txt
    Command: I need to access the document report. Response: report.docx
    Command: Can you retrieve my file project dot t x t? Response: project.txt
    Command: Load the file notes dot t x t. Response: notes.txt
    Command: Read the file homework. Response: homework.txt
    Command: Show me the file proposal dot d o c x. Response: proposal.docx  
    Command: Open the agenda file in documents under home. Response: /home/user/documents/agenda.txt
    Command: Fetch the file summary dot t x t. Response: summary.txt
    Command: Open file book docs. Resposne: book.docx
    Command: Acces the doc file reading. Response: reading.docx
    Command: Access the file reading dot text. Response: reading.txt
    Command: Open docs book. Response: book.docs
    Command: Access the file reference dot d o c x. Response: reference.docx   
    Command: Get the document instructions dot d o c x. Response: instructions.docx
    Command: Retrieve my text file story dot t x t. Response: story.txt
    Command: Open my document thesis dot d o c x. Response: thesis.docx
    Command: Access the file drafts dot t x t. Response: drafts.tx'''
    },
    {
        "role": "user",
        "content": "Open file book docs"
    },
    {
        "role": "assistant",
        "content": "book.docx"
    },
    {
        "role": "user",
        "content": "Access the doc file reading"
    },
    {
        "role": "assistant",
        "content": "reading.docx"
    },
    {
        "role": "user",
        "content": "Access the file reading dot text"
    },
    {
        "role": "assistant",
        "content": "reading.txt"
    },
    {
        "role": "user",
        "content": "Open docs book"
    },
    {
        "role": "assistant",
        "content": "book.docs"
    },
        {
        "role": "user",
        "content": "Open my text file food"
    },
    {
        "role": "assistant",
        "content": "food.txt"
    },
    {
        "role": "user",
        "content": "Open file sunrise dot txt"
    },
    {
        "role": "assistant",
        "content": "sunrise.txt"
    },
    {
        "role": "user",
        "content": "I need to access the document report"
    },
    {
        "role": "assistant",
        "content": "report.docx"
    },
    {
        "role": "user",
        "content": "Can you retrieve my file project dot t x t?"
    },
    {
        "role": "assistant",
        "content": "project.txt"
    },
    {
        "role": "user",
        "content": "Load the file notes dot t x t"
    },
    {
        "role": "assistant",
        "content": "notes.txt"
    },
    {
        "role": "user",
        "content": "Read the file homework"
    },
    {
        "role": "assistant",
        "content": "homework.txt"
    },
    {
        "role": "user",
        "content": "Show me the file proposal dot d o c x"
    },
    {
        "role": "assistant",
        "content": "proposal.docx"
    },
    {
        "role": "user",
        "content": "Open the agenda file in documents under home"
    },
    {
        "role": "assistant",
        "content": "/home/user/documents/agenda.txt"
    },
    {
        "role": "user",
        "content": "Fetch the file summary dot t x t"
    },
    {
        "role": "assistant",
        "content": "summary.txt"
    },
    {
        "role": "user",
        "content": "Access the file reference dot d o c x"
    },
    {
        "role": "assistant",
        "content": "reference.docx"
    },
    {
        "role": "user",
        "content": "Get the document instructions dot d o c x"
    },
    {
        "role": "assistant",
        "content": "instructions.docx"
    },
    {
        "role": "user",
        "content": "Retrieve my text file story dot t x t"
    },
    {
        "role": "assistant",
        "content": "story.txt"
    },
    {
        "role": "user",
        "content": "Open my document thesis dot d o c x"
    },
    {
        "role": "assistant",
        "content": "thesis.docx"
    },
    {
        "role": "user",
        "content": "Access the file drafts dot t x t"
    },
    {
        "role": "assistant",
        "content": "drafts.txt"
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
            document_content = read_docx(filename=filename.lower())
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

        if re.match(exit_regex, command, re.IGNORECASE):
            return

        # Perform operation
        elif 'read' in command.lower():
            speak(document_content)
        else:
            updated_content = doc_operations(document_content, command)
            if "Operation failed" in updated_content:
                speak("Operation failed.")
            elif re.search(summary_regex, command, re.IGNORECASE):
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