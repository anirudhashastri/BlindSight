import os
import subprocess
import sys
from dotenv import load_dotenv
from groq import Groq
from STT import STT
from TTS import speak
from documentreader import doc_main
from log_config import setup_logger
import sys
import os
from datetime import datetime
import time



# Create logger for the specific module
logger = setup_logger('pipeline')

# Test logging
logger.info(f"Logging initialized for {__name__}")

# Ensure that your .env file contains the following variables:
# GROQ_API_KEY, WHISPER_MAIN_PATH, WHISPER_MODEL_PATH
load_dotenv()


# Initialize Speech-to-Text (STT) system
try:
    from enhanced_stt import EnhancedSTT  
    speech_recog = EnhancedSTT()
    logger.info("Enhanced Speech-to-Text system initialized.")
except ImportError as e:
    logger.error(f"Failed to import EnhancedSTT class: {e}")
    speak("Speech recognition system is not available.")
    sys.exit(1)
except Exception as e:
    logger.error(f"Error initializing STT system: {e}")
    speak("An error occurred while initializing the speech recognition system.")
    sys.exit(1)



# Initialize Groq client
try:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    client = Groq(api_key=api_key)
    logger.info("Groq client initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    speak("Failed to initialize the language model. Please check your API key and try again.")
    sys.exit(1)

# Determine the operating system name
os_name = os.name
logger.info(f"Operating system detected: {os_name}")


if os_name == 'nt':
    os_name = 'Windows'
else:
    os_name = 'Unix/Linux'

logger.info(f"OS Name set to: {os_name}")

def time_llm_call(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start_time
            logger.info(f"LLM call to {func.__name__} completed in {elapsed:.2f} seconds")
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            logger.error(f"LLM call to {func.__name__} failed after {elapsed:.2f} seconds: {e}")
            raise
    return wrapper

# Intent recognition using LLM
@time_llm_call
def recognize_intent_with_llm(command,max_retries=3):
    """
    Identifies the intent of a given command using the Groq LLM.
    
    Args:
        command (str): The user command to analyze.
    
    Returns:
        str: The identified intent label ("Bash command execution" or "Document Operation").
    """    

    prompt = [
    {
        "role": "system",
        "content": f'''
Identify the intent of the command and respond with one of these labels:
Bash command execution, Document Operation.

CRUD operations such as Read and Update are categorized as Document Operation.
File-level actions such as Delete or Rename are categorized as Bash command execution.

Examples:
- Open my txt file Money: Document Operation
- Read the file report.docx: Document Operation
- Update the content in tasks.txt: Document Operation
- Delete my notes file: Bash command execution
- Rename the document project.pdf: Bash command execution
- Edit the file summary.docx: Document Operation
- Undo changes in tasks.csv: Document Operation
- Remove the file old_data.txt: Bash command execution

Respond only with the intent label and nothing else.
'''
    },
    {
        "role": "user",
        "content": "Open the document report.docx"
    },
    {
        "role": "assistant",
        "content": "Document Operation"
    },
    {
        "role": "user",
        "content": "Delete the file logs.txt"
    },
    {
        "role": "assistant",
        "content": "Bash command execution"
    },
    {
        "role": "user",
        "content": "Edit my tasks file"
    },
    {
        "role": "assistant",
        "content": "Document Operation"
    },
    {
        "role": "user",
        "content": "Remove the file backup.txt"
    },
    {
        "role": "assistant",
        "content": "Bash command execution"
    },
    {
        "role": "user",
        "content": "Undo changes in my notes.txt"
    },
    {
        "role": "assistant",
        "content": "Document Operation"
    },
    # User's input command dynamically added here
    {
        "role": "user",
        "content": command  # Replace 'command' with the actual user input dynamically
    }
]
    

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                messages=prompt,
                model="llama3-70b-8192"
            )
            intent_label = response.choices[0].message.content.strip()
            logger.info(f"Intent recognized: {intent_label}")
            return intent_label
            
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed to recognize intent after {max_retries} attempts: {e}")
                return None
            logger.warning(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(1)  # Wait before retry
  
    # response = client.chat.completions.create(
    #     messages=prompt,
    #     model="llama3-70b-8192"
    # )
    
    # # Extract and return the bash command
    # bash_command = response.choices[0].message.content
    # return bash_command

@time_llm_call
def generate_bash_command(request,cwd,os_name):
    """
    Generates a bash command based on the user request using the Groq LLM.
    
    Args:
        request (str): The user's request for a bash command.
        cwd (str): Current working directory.
        os_name (str): Name of the operating system.
    
    Returns:
        str: The generated bash command.
    """

    system_commands = {
        'Windows': {
            'list': 'dir',
            'delete': 'del',
            'copy': 'copy',
            'move': 'move',
            'mkdir': 'mkdir',
            'rename': 'rename'
        },
        'Unix/Linux': {
            'list': 'ls',
            'delete': 'rm',
            'copy': 'cp',
            'move': 'mv',
            'mkdir': 'mkdir',
            'rename': 'mv'
        }
    }
    messages = [
        {
    "role": "system",
    "content": f'''
    You are a Bash Command Generator for {os_name}.
    You should generate commands for {os_name}. 
    Provide only the required bash command in response to each user request.
    Use these mappings:
    Windows: dir (list), del (delete), copy, move, mkdir, rename
    Unix/Linux/MacOS: ls (list), rm (delete), cp (copy), mv (move/rename), mkdir


Guidelines:

1. Respond with only the bash command in the exact format needed, without additional text or assumptions. 
2. Interpret all paths as relative to the current working directory  and do not start commands from ~ or any assumed root directory unless explicitly requested.
3. If the request is unrelated to file system tasks, respond with exactly: "I only generate bash commands for file system tasks."
'''
},  

        {"role": "user", "content": request}  
    ]
    
    try:
        response = client.chat.completions.create(
            messages=messages,
            model="llama3-70b-8192"
        )
        command = response.choices[0].message.content.strip()
        commands = system_commands['Windows' if os_name == 'Windows' else 'Unix/Linux']
        
        # Replace command if needed based on OS
        for cmd_type, os_cmd in commands.items():
            if cmd_type in command.lower():
                command = command.replace(cmd_type, os_cmd)
        
        return command
    except Exception as e:
        logger.error(f"Command generation error: {e}")
        speak("Error generating command. Please try again.")
        return None

@time_llm_call
def execute_command(command):
    """
    Executes a given bash command and returns its output.
    
    Args:
        command (str): The bash command to execute.
    
    Returns:
        str or Exception: The output of the command or the exception if it fails.
    """    
    try:
        # Check if the command is a 'cd' command
        if command.startswith("cd "):
            # Extract the directory path after 'cd' and strip any surrounding whitespace
            path = command[3:].strip()
            os.chdir(path)
            current_dir = os.getcwd()
            logger.info(f"Changed directory to {current_dir}")
            return f"Changed directory to {current_dir}"
        
        elif command.startswith("find "):
            result = subprocess.run(command, shell=True,capture_output=True, text=True)
            output = result.stdout.strip()
            logger.info(f"Find command output: {output}")
            return result.stdout.strip()

        else:
            # Execute other bash commands
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            output = result.stdout.strip()
            logger.info(f"Bash command output: {output}")
            return output

    except subprocess.CalledProcessError as e:
        error_output = e.stderr.strip() if e.stderr else str(e)
        logger.error(f"Command '{command}' failed with error: {error_output}")
        return e
    except Exception as e:
        logger.error(f"Unexpected error during command execution: {e}")
        return e
    

    # error handler functions
@time_llm_call
def generate_missing_file(error_message):
    """
    Identifies the missing file or directory from an error message using the Groq LLM.
    
    Args:
        error_message (str): The error message containing information about the missing item.
    
    Returns:
        str: The name of the missing file or directory.
    """    
    messages = [
        {
            "role": "system",
            "content": '''You are a Bash Command Assistant specializing in identifying missing files or directories. For each error message provided, identify and return only the name of the file or directory that does not exist.

Guidelines:

1. Respond with only the name of the missing file or directory mentioned in the error message, and nothing else.
2. Do not provide any explanations, paths, or additional information.
3. Assume that the file or directory name is as stated in the error message, without interpreting it as relative or absolute.

Example:

If the error message is: "Exception occurred: [Errno 2] No such file or directory: 'desktop'", respond with: desktop
'''
        },
        {"role": "user", "content": error_message}
    ]
    
    try:
        response = client.chat.completions.create(
            messages=messages,
            model="llama3-70b-8192"
        )
        missing_item = response.choices[0].message.content.strip()
        logger.info(f"Missing item identified: {missing_item}")
        return missing_item
    except Exception as e:
        logger.error(f"Error during missing file identification: {e}")
        speak("I encountered an error while identifying the missing file.")
        return None

@time_llm_call
def generate_find_command(missing_item):
    """
    Generates a 'find' command to locate the missing file or directory.
    
    Args:
        missing_item (str): The name of the missing file or directory.
    
    Returns:
        str: The 'find' command to locate the missing item.
    """
    # TODO: Add Windows command support
    # TODO: Categorize input command as file or folder and generate accordingly
    # TODO: Optimize search using regex
    # TODO: Localize search directory based on current working directory
    
    if os_name == 'Windows':
        find_command = f'dir /s /b *{missing_item}*'
    else:
        find_command = f"find / -name '{missing_item}' -maxdepth 5 2>/dev/null"
    logger.info(f"Find command generated: {find_command}")
    return find_command

@time_llm_call
def explainError(error_message):
    """
    Provides a concise explanation of a Python exception using the Groq LLM.
    
    Args:
        error_message (str): The Python exception message.
    
    Returns:
        str: A brief explanation of the error.
    """    
    messages = [

        {
            "role": "system",
            "content": '''Given a python Exception , explain as if you are the file system. Keep it clear, CONCISE.
            DO NOT ASSUME ANYTHING OR CHANGE THE ERROR. ONLY EXPLAIN THE ERROR VERY SHORTLY and OBJECTIVELY. 
'''
        },
        {"role": "user", "content": error_message}
    ]
    
    try:
        response = client.chat.completions.create(
            messages=messages,
            model="llama3-70b-8192"
        )
        explained_error = response.choices[0].message.content.strip()
        logger.info(f"Error explanation: {explained_error}")
        return explained_error
    except Exception as e:
        logger.error(f"Error during error explanation: {e}")
        speak("I encountered an error while trying to explain the issue.")
        return "An error occurred while processing your request."


def pipeline(request):
    """
    Processes a user request by generating and executing the appropriate bash command.
    
    Args:
        request (str): The user's request.
    
    Returns:
        str: The result of the executed command or an error message.
    """    
    cwd = os.getcwd()
    logger.info(f"Current working directory: {cwd}")
    
    try:
        # Generate and execute the primary bash command
        bash_command = generate_bash_command(request, cwd,os_name)
        if not bash_command:
            logger.error("Bash command generation failed.")
            speak("I couldn't generate a bash command for your request.")
            return "Command generation failed."        
        
        # Execute the generated bash command
        result = execute_command(bash_command)
        
        # If the result is an exception, raise it to be handled in the except block
        if isinstance(result, BaseException):
            raise result
        
        return result
    
    

    except Exception as e:
        # Fallback: Identify the missing item and generate a 'find' command
        explained_error = explainError(str(e))
        # print(explained_error)
        logger.error(f"Error during pipeline execution: {explained_error}")
    

        # Check if the exception is related to a missing file or directory
        if isinstance(e, FileNotFoundError):
            # Identify the missing item from the error message
            missing_item = generate_missing_file(str(e))
            if missing_item:
                logger.info(f"Searching for missing item: {missing_item}")
                speak(f"Searching for the missing item: {missing_item}")
                
                # Generate and execute the 'find' command to locate the missing item
                find_command = generate_find_command(missing_item)
                find_result = execute_command(find_command)
                return find_result if find_result else "Missing item not found."
            else:
                return "Could not determine the missing item from the error message."
        else:
            if explained_error:
                return explained_error
            else:
                return "An unknown error occurred during command execution."


def ReadSolution(question,result):
    """
    Formats the bash command and its response for text-to-speech readability.
    
    Args:
        question (str): The bash command executed.
        result (str): The response/output from the bash command.
    
    Returns:
        str: A formatted explanation suitable for TTS.
    """    
    if isinstance(result, Exception) or "error" in str(result).lower():
        return "I encountered an error while executing your command. Please try rephrasing it."
    
    messages = [

        {
            "role": "system",
            "content": '''
You are given a bash command and its response. Make it suitable for reading. 
For example, if the bash command is 'ls' and the response is a list of contents of a directory, 
you should reply it as "Here are the files: File1.txt, File2.pdf." 
For path-related responses - if the response is 'x/y/s', you should say "You are in 's' in 'y' in 'x'." 
If it's a list command, identify the folders and files and arrange them accordingly.
Enhance it appropriately for text-to-speech. DO NOT GIVE ANYTHING EXTRA. 
IF THE COMMAND DOES NOT MAKE SENSE, RESPOND WITH "SORRY, GIVE DOCUMENT COMMANDS ONLY."
'''
        },
        {"role": "user", "content": question + "Answer :\n" + result}
    ]
    
    try:
        response = client.chat.completions.create(
            messages=messages,
            model="llama3-70b-8192"
        )
        formatted_response = response.choices[0].message.content.strip()

        
        logger.info(f"Formatted response for TTS: {formatted_response}")
        return formatted_response
    except Exception as e:
        logger.error(f"Error during response formatting: {e}")
        speak("I encountered an error while formatting the response.")
        return "I encountered an error while processing your request."

speak("I can now start assisting you! Please press and hold the spacebar to speak your command.", speed=1.5)
logger.info("System is ready to assist the user.")

while(True):

    # Record audio using press-and-hold
    if not speech_recog.record_press_hold("audio_sample.wav"):
        speak("Recording failed. Please try again.")
        continue
        
    command = speech_recog.process_audio_with_whisper("audio_sample.wav")
    logger.info(f"User command received: {command}")
    print(f"Command: {command}")

    # Check for termination commands
    if command is None:
        speak("No command recieved!")
        logger.info("No command recieved")
        continue

    if "exit" in command.lower()  or "quit" in command.lower() or "terminate" in command.lower():
        speak("Exiting the program. Goodbye!")
        logger.info("Exiting the program.")
        break

    # Recognize the intent of the command
    intent = recognize_intent_with_llm(command)
    if intent == "Document Operation":

        # Create a wrapper function to match the expected interface
        def record_audio_wrapper(filename, duration=7):
            return speech_recog.record_press_hold(filename)
            
        # Assign the wrapper function
        speech_recog.record_audio = record_audio_wrapper
        
        # Call doc_main with the modified speech_recog object
        doc_main(command, speech_recog=speech_recog)
        speak("Back to operating system mode.")
    else:
        # Handle bash command executions
        response = ReadSolution(command, pipeline(command))
        print(f"Response: {response}")
        speak(response,speed=1)
        logger.info("Bash command execution completed.")