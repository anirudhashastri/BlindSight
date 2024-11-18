import os
from groq import Groq
from dotenv import load_dotenv
import subprocess
from STT import STT
from TTS import speak
from documentreader import doc_main
import re

load_dotenv()


speech_recog = STT()

client = Groq(
   api_key=os.environ["GROQ_API_KEY"],
)

# feed what type of system it is

os_name = os.name

print(os_name)

if os_name=='nt':
    os_name = 'Windows'

else:
    os_name = 'Unix/Linux'



# Intent recognition using LLM
def recognize_intent_with_llm(command):
    prompt = [
    {
        "role": "system",
        "content": f'''
Identify the intent of the command and respond with one of these labels:
Bash command execution, Document Operation.

CRUD operations such as Read and Update are categorized as Document Operation. File-level actions such as Create, Delete or Rename are categorized as Bash command execution.

Examples:

1. Command: Open my txt file Money. Response: Document Operation  
2. Command: Change my directory. Response: Bash command execution  
3. Command: Create a new document called report. Response: Bash command execution  
4. Command: Delete the file named draft.txt. Response: Bash command execution  
5. Command: Open the document project.docx. Response: Document Operation  
6. Command: List all files in my directory. Response: Bash command execution  
7. Command: Show me the file notes.txt. Response: Document Operation  
8. Command: Rename the file budget to budget2024. Response: Bash command execution  
9. Command: Access the file chapter1.docx. Response: Document Operation  
10. Command: Create a text file called tasks. Response: Bash command execution  
11. Command: Load the file presentation.pptx. Response: Document Operation  
12. Command: Move the file report.docx to the archive folder. Response: Bash command execution  
13. Command: Edit the file named checklist.txt. Response: Document Operation  
14. Command: Copy the file agenda.txt to my desktop. Response: Bash command execution  
15. Command: View the file application.docx. Response: Document Operation  
16. Command: Create a new text file logs.txt. Response: Bash command execution  
17. Command: Open the file user_manual.docx. Response: Document Operation  
18. Command: Delete the document named old_notes.txt. Response: Bash command execution  
19. Command: Display the contents of the file tasks.txt. Response: Document Operation  
20. Command: Create a folder named backup. Response: Bash command execution 

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
        "content": "Open my txt file Money"
    },
    {
        "role": "assistant",
        "content": "Document Operation"
    },
    {
        "role": "user",
        "content": "Change my directory"
    },
    {
        "role": "assistant",
        "content": "Bash command execution"
    },
    {
        "role": "user",
        "content": "Create a new document called report"
    },
    {
        "role": "assistant",
        "content": "Bash command execution"
    },
    {
        "role": "user",
        "content": "Delete the file named draft.txt"
    },
    {
        "role": "assistant",
        "content": "Bash command execution"
    },
    {
        "role": "user",
        "content": "Open the document project.docx"
    },
    {
        "role": "assistant",
        "content": "Document Operation"
    },
    {
        "role": "user",
        "content": "List all files in my directory"
    },
    {
        "role": "assistant",
        "content": "Bash command execution"
    },
    {
        "role": "user",
        "content": "Show me the file notes.txt"
    },
    {
        "role": "assistant",
        "content": "Document Operation"
    },
    {
        "role": "user",
        "content": "Rename the file budget to budget2024"
    },
    {
        "role": "assistant",
        "content": "Bash command execution"
    },
    {
        "role": "user",
        "content": "Access the file chapter1.docx"
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
    
  
    response = client.chat.completions.create(
        messages=prompt,
        model="llama3-70b-8192"
    )
    
    # Extract and return the bash command
    bash_command = response.choices[0].message.content
    return bash_command

def generate_bash_command(request,cwd,os_name):
    messages = [
        {
    "role": "system",
    "content": f'''You are a Bash Command Generator for {os_name}.You should generated commands for {os_name}. Provide only the required bash command in response to each user request.

Guidelines:

Respond with only the bash command in the exact format needed, without additional text or assumptions.
Interpret all paths as relative to the current working directory and do not start commands from ~ or any assumed root directory unless explicitly requested.
If the request is unrelated to file system tasks, respond with exactly: "I only generate bash commands for file system tasks."
For create-related commands, ensure the bash command is in lowercase and that any file names created are also in lowercase..
'''
},  # Always include the system prompt first
        {"role": "user", "content": request}  # Then the user request
    ]
    
    # Call the model with just the system and latest user message
    response = client.chat.completions.create(
        messages=messages,
        model="llama3-70b-8192"
    )
    
    # Extract and return the bash command
    bash_command = response.choices[0].message.content
    return bash_command


def execute_command(command):
    try:
        # Check if the command is a 'cd' command
        if command.startswith("cd "):
            # Extract the directory path after 'cd' and strip any surrounding whitespace
            path = command[3:].strip()
            os.chdir(path)
            return f"Changed directory to {os.getcwd()}"
        
        elif command.startswith("find "):
            result = subprocess.run(command, shell=True,capture_output=True, text=True)
            return result.stdout.strip()

        # For other commands, use subprocess
        else:
            result = subprocess.run(command, shell=True, check = True,capture_output=True, text=True)
            # print(result)
            
            return result.stdout.strip()

    except Exception as e:
        
        return (e)
    

    # error handler functions
def generate_missing_file(error_message):
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
    
    response = client.chat.completions.create(
        messages=messages,
        model="llama3-70b-8192"
    )
    
    missing_item = response.choices[0].message.content.strip()
    return missing_item


 # TO-DO : 
def generate_find_command(missing_item):
    # Return the 'find' command as a string to locate the missing item
    # TODO: Add for windows commad 
    # based on input comand catgerize as file or folder and genrate 
    # regex for optimised search 
    # TODO: Maybe call a pwd and use currect directory as paramter ( if we can find a way to localize what we are 
    # search in the sense of direcroy and a septrate threaded process we can further optimize the search)
    return f"find / -name '{missing_item}' -maxdepth 5 2>/dev/null"


def explainError(error_message):
    messages = [

        {
            "role": "system",
            "content": '''Given a python Exception , explain as if you are the file system. Keep it clear, CONCISE.
            DO NOT ASSUME ANYTHING OR CHANGE THE ERROR. ONLY EXPLAIN THE ERROR VERY SHORTLY and OBJECTIVELY. 
'''
        },
        {"role": "user", "content": error_message}
    ]
    
    response = client.chat.completions.create(
        messages=messages,
        model="llama3-70b-8192"
    )
    
    explainedError = response.choices[0].message.content.strip()
    return explainedError


def pipeline(request):
    cwd = os.getcwd()
    
    try:
        # Generate and execute the primary bash command
        bash_command = generate_bash_command(request, cwd,os_name)
        
        result = execute_command(bash_command)
        

        if isinstance(result, BaseException):
            raise result
        
        return result
    
    

    except Exception as e:
        # Fallback: Identify the missing item and generate a 'find' command
        print(explainError(str(e)))
    
        # print(e.__name__)
        if FileNotFoundError:
        
                    # Identify the missing file or folder from the error message
                    missing_item = generate_missing_file(str(e))
                    print(f"Searching {missing_item} in the file system")
                    
                    if missing_item:
                        # Generate the 'find' command and execute it
                        find_command = generate_find_command(missing_item)
                        
                        return execute_command(find_command)
                    else:
                        return "Could not determine missing item from error message."
                    
        else :
            
            print(explainError(e))


def ReadSolution(question,result):
    messages = [

        {
            "role": "system",
            "content": '''You are given bash command and its response. Make it suitable for reading. For example if the bash command is ls and the response 
            is a list of contents of a directory, you should reply it as Here are the files, File1.txt, file2.pdf. For path related responses - if the response is x/y/s you should 
            give you are in s in y in x. If it a list command, identify the folders and files and arrange them accordingly.
            Enchance it appropriate for a text to speech.DO NOT GIVE ANYTHING EXTRA, IF COMMAND DOES NOT MAKE SENSE, GIVE ERROR SAYING 'SORRY, GIVE DOCUMENT COMMANDS ONLY.'. 
'''
        },
        {"role": "user", "content": question + "Ans :\n" + result}
    ]
    
    response = client.chat.completions.create(
        messages=messages,
        model="llama3-70b-8192"
    )
    
    explainedError = response.choices[0].message.content.strip()
    return explainedError

speak("I can now start assisting you!")


terminate_regex = r"^(?i)(end|quit|stop)"
while(True):

    speech_recog.record_audio("audio_sample.wav", duration=7)
    command  = speech_recog.process_audio_with_whisper("audio_sample.wav")
    print(command)
    
    if re.match(terminate_regex, command):

        break

    intent = recognize_intent_with_llm(command)
    if intent == "Document Operation":
        doc_main(command,speech_recog=speech_recog)
        speak("you are now back in you OS")
    else:
        response = ReadSolution(command,pipeline(command))
        print( "Response : ",response)
        speak(response)