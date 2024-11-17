import pyttsx3

engine = pyttsx3.init()


# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()