import os
from groq import Groq
from dotenv import load_dotenv
import subprocess
from STT import STT
load_dotenv()
from TTS import speak
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



def generate_bash_command(request,cwd,os_name):
    messages = [
        {
    "role": "system",
    "content": f'''You are a Bash Command Generator for {os_name}.You should generated commands for {os_name}. Provide only the required bash command in response to each user request.

Guidelines:

Respond with only the bash command in the exact format needed, without additional text or assumptions. 
Interpret all paths as relative to the current working directory  and do not start commands from ~ or any assumed root directory unless explicitly requested.
If the request is unrelated to file system tasks, respond with exactly: "I only generate bash commands for file system tasks."
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
            give you are in s in y in x
            Enchance it appropriate for a text to speech. 
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


while(True):

    speech_recog.record_audio("audio_sample.wav", duration=7)
    command  = speech_recog.process_audio_with_whisper("audio_sample.wav")
    print(command)
    if command is None or "end" in command:
        break
     
    response = ReadSolution(command,pipeline(command))
    print( "Response : ",response)
    speak(response)