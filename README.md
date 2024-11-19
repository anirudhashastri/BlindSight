# First High-Fidelity Prototype Development

## **Project Title**
**BlindSight: AI-Powered Voice-Driven File Navigation for the Visually Impaired**

---

## Table of Contents
- [Overview](#overview)
- [Objectives](#Objectives)
- [Prototype Features](#Prototype-Features)
    - [Core Functionalities](#Core-Functionalities)
    - [User Interface Highlights](#User-Interface-Highlights)
- [CLI Features](#CLI-Features)
  - [Task List](#Task-List)
- [Interface Design](#Interface-Design)
- [Screenshots: Video](#Screenshots-Video)
- [Tech Stack](#Tech-Stack)  
- [Feedback Plan](#Feedback-Plan)
    - [Objective](#Objective)
    - [Methods](#Methods)
- [Final Deliverables Checklist](#Final-Deliverables-Checklist)
- [Set up instructions](#Set-up-instructions)
    - [Step 1: Create an Anaconda Environment Optional ](#Step-1-Create-an-Anaconda-Environment-Optional)
    - [step 2: Clone the GitHub Repository](#step-2-Clone-the-GitHub-Repository)
    - [Step 3: Install Required Packages](#Step-3-Install-Required-Packages)
    - [step 4: create a .env file](#step-4-create-a-env-file)
    - [step 5: Set up whisper for speech to text](#step-5-Set-up-whisper-for-speech-to-text)
      - [Mac OS](#Mac-OS)
      - [Windows](#Windows)
    - [Step 6: Obtain a Groq API Key](#Step-6-Obtain-a-Groq-API-Key)
    - [Step 7: Add Groq API key in .env](#Step-7-Add-Groq-API-key-in-env)
- [Running the application](#Running-the-application)
- [Future work](#Future-work)
- [NOTE](#NOTE)



## Overview
This repository contains the first high-fidelity prototype of the BlindSight project. 

BlindSight is our innovative approach to making computer systems more accessible and intuitive for individuals with complete or partial visual impairment. Using just a single key, users can navigate the operating system and perform essential tasks like text-file editing and OS manipulation (e.g., changing directories, listing files, creating folders, etc.). Our mission is to foster inclusivity in the tech space and empower individuals with disabilities by providing them with tools for equal representation in the digital world.

NOTE:The current version of the system is designed specifically for visually impaired users. It is built with the assumption that users can hear and have basic motor skills to interact with the interface by clicking buttons.
---

## Objectives
1. Develop a functional prototype with a **user-friendly interface** that aligns with the core functionality of the project.
2. Demonstrate how design ideas have been translated into an **interactive prototype**.
3. Lay the groundwork for **testing and refining the interface** based on feedback from target users.


![FlowChart](https://github.com/anirudhashastri/BlindSight/blob/2ed29c0bac7b5ed5cf44d75bc0213bc44d152230/images/flowchart.jpg)

---

## Prototype Features
### Core Functionalities
- Voice-Based Navigation:
  - Users can navigate folders, list files, and open or edit documents through voice commands.
- CLI Integration:
  - Real-time updates to file navigation and editing tasks using the Command Line Interface (CLI).
- Document Interaction:
  - Features include reading lines or paragraphs, summarizing text, correcting grammar, and editing documents.

### User Interface Highlights
- Accessibility-Driven Design:
  - Clear, speech-compatible prompts.
  - Audio feedback for every command executed.
  - Capablity to intrupt the Speach to text to update input from user using a single key (Default:Space bar)



---
## CLI Features
- Below are the set of commands that work well in the current system without any immediate issues.There are a few tasks
that are still in devlopment and are not recomended at the current state of the project.
### Task List
- changing directory
- Listing files
- creating directory ( for ease of implementation we have done this for current working directory and not in any file path provided)
- Creating a file (docx, text)
- pwd
- time
- Doc reader:
  - Reading lines
  - Sumarize content
  - Delete lines / paragraphs
  - update and add information 

---

## Interface Design 
The prototype interface has been carefully designed to meet accessibility requirements:
1. Voice Interaction Flow:
   - Supports real-time recognition and execution of commands, with immediate feedback with the capablity of intrupting based on user requirements.
2. Document Viewer:
   - enables the visually diasbled to do the following tasks:
      -  file reading
      -  summarizing
      -  editing functionalities.
3. Error Handling:
   - Clear voice alerts in case of invalid commands or errors.
4. Text to Speach:
    - We have used a text to speach model so that the user get feedback of all the task that thay are doing on the system.

---
## Screenshots: Video
Our project does not have any frontend interface (visual UI) as our whole project is build to help the visually disabled. Our interface is rooted in Text to speach and speach to text therefore we are adding a video link below to show how our system work for you reference. (Click on the image below for video)

[![Watch the video](https://github.com/anirudhashastri/BlindSight/blob/f0b11d0b7f1c4581220d066dc7b0afce8633ebfc/images/thumbnail.png)](https://drive.google.com/file/d/1PtzMPufQGHWVCk3AjRUqQE70H2LEru79/view?usp=sharing)

---
## Tech Stack
- OS Compatiblity:
    - Windows 10/11
    - Mac OS  12/13/14/15
- Language:
    - Python 3.10
- Speach to text:
    - [Whisper CPP](https://github.com/ggerganov/whisper.cpp) is a localized Speech to text model developed by OpenAI. For our use case we have decided to go with Whisper Tiny.
    - We have spoken about the set and instalation of this module below.
- LLM:
    - We are using Llama.1:70B through a API from [Groq](https://console.groq.com/docs/models).
    - Though we are using an LLM API key in some key places due to time shortage but we wil evetually be using a local LLM to improve scerity
    - Curertnly we are using the Llama API as we want to make it mobile for testing purposes. However this can bring up privacy and security issues (as dicussed below).However the in the case when this is being deployed to customers as a product we plan to use local Llama from [Ollama](https://ollama.com/library/llama3.1) as we have already tested with it and it works.

- Multi Threading:
    - currently we have parallelized the Speach to text for the **Document Reader** so that it is not overwhelming for the user.
 
- Text to Speech (TTS):
    - We have used python package [pyttsx3](https://pypi.org/project/pyttsx3/) for speech to text.
    - We are also planning to incorprete speed control and a better TTS. We are curretnly usng this for the prototype only.
---

## Feedback Plan
### Objective
To evaluate the usability and effectiveness of the BlindSight prototype through targeted feedback from end users and accessibility experts.

### Methods
For each participant with consent we wil also take a screen recording of the session to refer back for analysis and further improvements.

1. User Testing Sessions:
   - Participants: 4–6 users from the target demographic.
   - If we are unable to colaborate with Envisioning Access we will simulate by bindfolding users. We will also install BlindSight into their local system for the to experiment with for extra feedback they can provide later below is the setup for when we conduct the interviews only.
   - Setup: Controlled testing environment with pre-defined tasks.
   - Data Collection:
     - User navigation ease. 
     - Accuracy of voice recognition
     - Satisfaction with audio feedback and responses.( This will tell us about the effectiveness of the task we have integrated and also give us information about out Text to speech and Speech to text)

2. Surveys:
   - Distributed post-testing to collect subjective opinions on (For this we will personally ask them the question and note down their responses as indicated in User Incorporation Plan submitted from the previous assignment):
     - Interface intuitiveness.
     - Perceived usability.
     - Suggestions for improvement.

3. Interviews:
   - Conduct one-on-one interviews to gather in-depth insights about user experience.(As mentioned befoer these will be recoreded)
   - Focus Areas:
     - Challenges faced during navigation.
     - Suggestions for additional features.

---
## Final Deliverables Checklist
These are the list of tasks that are currently in work and we will have ready for our final submission of he project
1) expand command line features.
2) Refine and add more document editing features.
3) We will try to have a better Text to speach model with response speed control.
4) Reduce LLM dependence and add further verfication statergies.
5) Multi Threading for the CLI command and Text to speach (this has allread been done for the dociment reader).
6) We will add log files to evaluate the accuracy of the speach to text , text to speach and the LLM response for CLI tasks and document editing.
---

## Set up instructions

### Pre-requisities
- python 3.10
- Good microphone and speakers
- Ram Recomended: 16Gb , Minimum:8Gb
- Whisper Installation (Follow our wisper instalation guide)
  
### Step 1: Create an Anaconda Environment Optional

**You could choose to use the terminal/command prompt base env or create a virtual env (we have shown it through anaconda)**

1. Open your terminal or Anaconda Prompt install [Anaconda](https://docs.anaconda.com/anaconda/install/) for your system .
2. Run the following command to create a new environment:

    ```bash
    conda create -n BlindSight python=3.10
    ```

3. Activate the environment:

    ```bash
    conda activate BlindSight
    ```


### step 2: Clone the GitHub Repository
Clone the repository into a working directory of your choice
```bash
git clone https://github.com/anirudhashastri/BlindSight.git
```
and change into the directory
```bash
cd BlindSight
```

### Step 3: Install Required Packages


# TODO: exact requirements needs to be updated

Install the necessary packages, :

```bash
pip install -r requirements.txt
```
### step 4: create a `.env` file
- In the main working directory (BlindSight) create a .env file and add the keys we mention in the following steps
- **While adding the API key, do not use quotes**


### step 5: Set up whisper for speech to text

#### Mac OS
Following are the steps to install Whisper CPP for Macos (You can also follow the official [Whisper CPP](https://github.com/ggerganov/whisper.cpp) Documentation):
- Clone the Whisper Repository within the BlindSight Project Directory:
  ```bash
  git clone https://github.com/ggerganov/whisper.cpp.git
   ```
- Navigate into the Whisper Folder:
  ```bash
  cd whisper.cpp
   ```
- Download one of the models (tiny.en shown in this example):
  ```bash
  sh ./models/download-ggml-model.sh tiny.en
   ```
- Execute Make command:
  ```bash
   make -j
   ```
- Come out of whisper.cpp:
  ```bash
   cd ..
   ```
- In the .env file add these two lines:
  ```plaintext
   WHISPER_MODEL_PATH = "<Absolute path for whisper.cpp/main>"

   WHISPER_MAIN_PATH= "<Absolute Path for whisper.cpp/models/ggml-tiny.en.bin>"
   ```
Make sure to pass the absolute path of these files as relative paths will cause issues.
Whisper is all set!

#### Windows


#### Prerequisites:

- Ensure the following tools are installed and added to your system's `PATH`:

  1. **Git** [Download Git](https://www.simplilearn.com/tutorials/git-tutorial/git-installation-on-windows)

  2. **CMake** [Download CMake](https://cgold.readthedocs.io/en/latest/first-step/installation.html#windows)

  3. **MSBuild Tools for C++ Development** (includes the C++ compiler) [Download MSBuild Tools](https://learn.microsoft.com/en-us/visualstudio/msbuild/walkthrough-using-msbuild?view=vs-2019)

#### Steps to Set Up Whisper CPP on Windows:

  1) **Clone the Whisper CPP Repository:**
    Open Command Prompt in the blindsight folder and run:
      ```bash
        git clone https://github.com/ggerganov/whisper.cpp.git
      ```

  2) **Navigate to the Repository Directory:**
      ```bash
        cd whisper.cpp
      ```

  3) **Generate Build Files with CMake:**
      ```bash
        cmake . --fresh
      ```

  4) **Build the Project Using MSBuild:**
      ```bash
        msbuild ALL_BUILD.vcxproj /p:Configuration=Release
      ```

  5) **Navigate to the Models Directory:**
      ```bash
        cd models
      ```

  6) **Download the Whisper Model:**
      ```bash
        curl -L https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.en.bin?download=true -o models\ggml-tiny.en.bin
      ```

  7) **Copy Build Files:**
        - Option 1: Using Command Prompt, copy all files from `bin\Release` to the `whisper.cpp` directory:
             ```bash
                xcopy /E /I bin\Release\* ..\ 
              ```
        - **Option 2:** Alternatively, manually copy the files using File Explorer.

  8) **Run the Whisper CPP Executable:**
    - Ensure you're in the `whisper.cpp` directory and execute:
    ```bash
        main -m models\ggml-base.bin -f samples\jfk.wav -t 8
    ```
    **Expected Output:**
    The command should print the transcription:
    ```
    [00:00:00.000 --> 00:00:11.000]   And so my fellow Americans, ask not what your country can do for you, ask what you can do for your country.
    ```

  9) **Rename Folder to whisper_cpp**
    - To avoid "File Not Found" errors, rename `whisper.cpp` to `whisper_cpp`.

  10) **Set .env variables**
        - In the .env file add these two lines:
        ```plaintext
        WHISPER_MODEL_PATH = "<Absolute path for whisper_cpp/main>"

        WHISPER_MAIN_PATH= "<Absolute Path for whisper_cpp/models/ggml-tiny.en.bin>"
        ```
      Make sure to pass the absolute path of these files as relative paths will cause issues.
  Whisper is all set!
 
  

**Credits:**

Special thanks to [this tutorial](https://www.youtube.com/watch?v=yclO67nSufw&t=831s) for guiding the setup process.


### Step 6: Obtain a Groq API Key

1. Visit the [Groq API website](https://www.groq.com) and sign up for a developer account.
2. Generate a free API key from your dashboard under **API Keys**.
3. Copy this key for use in the next step.
4. I have also provided a key for ease of useage in the APIKEY.txt

### Step 7: Add Groq API key in `.env`

- Add your Groq API key in the following format:

    ```plaintext
    GROQ_API_KEY=your_api_key_here
    ```

- For security, ensure `.env` is listed in `.gitignore` (included in this project) to avoid accidentally committing sensitive information.

---

## Running the application
- Once all the steps above are followed you will have
  1) Whisper installed
  2) The environment set up
  3) Groq api key entered
- Now to run the pipeline 
```bash
   python pipeline.py
   ```
- If this doesnt work try
  1) Mac OS
     ```bash
      sudo python pipeline.py
     ```
  2) Windows
    - run comand prompt as administrator
- Once we run pipeline.py the user will be prompted to select a microphone input (This is only for the protoype the final version will ask via voice for mic selection)
- The file manipulation commands can be given directly 
- **Documnet Reader commands: While doing document editing the user needs to hold down the space bar while speaking and realease when he is done and then the task will be executed.**



## Future work
1) Make it a executable file or a docker container for ease of use.
2) Make use of Local LLM models like [Ollama](https://ollama.com/library/llama3.1) so multiple system can access it as a server for scalablity , privacy and security.
3) Fine tune the LLM for our specfic use case for document reading and CLI tasks.
4) Custom voice models for wider inclusivity (accent, tone).
5) Add support for other languages we are only doing it for english now.



## NOTE
Though we are using API key from Groq for now, we have gone through [Groq Privacy policy](https://groq.com/privacy-policy/) and it gaurentees cetain things like:
1) Non data retention
2) Comprehensive compliance
3) No training on personal data




