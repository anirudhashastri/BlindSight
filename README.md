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
- [Interface Design](#Interface-Design)  
- [Feedback Plan](#Feedback-Plan)
    - [Objective](#Objective)
    - [Methods](#Methods)
- [Set up instructions](#Set-up-instructions)
    - [Step 1: Create an Anaconda Environment](#Step-1:-Create-an-Anaconda-Environment)
    - [Step 2: Install Required Packages](#Step-2:-Install-Required-Packages)
    - [step-3: Set up wisper for speech to text](#step-3:-Set-up-wisper-for-speech-to-text)
    - [Step 4: Obtain a Groq API Key](#Step-4:-Obtain-a-Groq-API-Key)
    - [Step 5: Configure the `.env` File](#Step-5:-Configure-the-`.env`-File)
- [Running the application](#Running-the-application)



## Overview
This repository contains the first high-fidelity prototype of the BlindSight project. The prototype focuses on delivering an intuitive user interface to empower visually impaired and physically disabled individuals to navigate and manage their computer's file system through voice commands. This prototype serves as a foundational step toward the final product and is designed to collect valuable user feedback for iterative improvements.

---

## Objectives
1. Develop a functional prototype with a **user-friendly interface** that aligns with the core functionality of the project.
2. Demonstrate how design ideas have been translated into an **interactive prototype**.
3. Lay the groundwork for **testing and refining the interface** based on feedback from target users.

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
- Mode Switching:
  - Flexibility to operate via voice commands or keyboard inputs.
- Minimalistic Layout (CLI/Prototype Display):
  - Ensures clarity and usability for visually impaired users.

---

## Interface Design
The prototype interface has been carefully designed to meet accessibility requirements:
1. Voice Interaction Flow:
   - Supports real-time recognition and execution of commands, with immediate feedback.
2. Document Viewer:
   - Seamlessly integrates file reading, summarizing, and editing functionalities.
3. Error Handling:
   - Clear voice and visual alerts in case of invalid commands or errors.

---

## Feedback Plan
### Objective
To evaluate the usability and effectiveness of the BlindSight prototype through targeted feedback from end users and accessibility experts.

### Methods
1. User Testing Sessions:
   - Participants: 4–6 users from the target demographic (visually impaired and physically disabled).
   - Setup: Controlled testing environment with pre-defined tasks.
   - Data Collection:
     - User navigation ease.
     - Accuracy of voice recognition.
     - Satisfaction with audio feedback and responses.

2. Surveys:
   - Distributed post-testing to collect subjective opinions on:
     - Interface intuitiveness.
     - Perceived usability.
     - Suggestions for improvement.

3. Interviews:
   - Conduct one-on-one interviews to gather in-depth insights about user experience.
   - Focus Areas:
     - Challenges faced during navigation.
     - Suggestions for additional features.

---

## Set up instructions

### Step 1: Create an Anaconda Environment

1. Open your terminal or Anaconda Prompt install [Anaconda](https://docs.anaconda.com/anaconda/install/) for your system .
2. Run the following command to create a new environment:

    ```bash
    conda create -n BlindSight python=3.10
    ```

3. Activate the environment:

    ```bash
    conda activate BlindSight
    ```

### Step 2: Install Required Packages


# TODO: exact requirements needs to be updated

Install the necessary packages, :

```bash
pip install groq dotenv pyttsx3 pyaudio SpeechRecognition
```

### step-3: Set up wisper for speech to text


### Step 4: Obtain a Groq API Key

1. Visit the [Groq API website](https://www.groq.com) and sign up for a developer account.
2. Generate a free API key from your dashboard under **API Keys**.
3. Copy this key for use in the next step.
4. I have also provided a key for ease of useage in the APIKEY.txt

### Step 5: Configure the `.env` File

1. In the root directory of your project, create a `.env` file (if it doesn’t already exist).
2. Add your Groq API key in the following format:

    ```plaintext
    GROQ_API_KEY=your_api_key_here
    ```

3. For security, ensure `.env` is listed in `.gitignore` (included in this project) to avoid accidentally committing sensitive information.

---

## Running the application



