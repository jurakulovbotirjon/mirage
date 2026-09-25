import pyttsx3

engine = pyttsx3.init()


def speak(text):
    print(f"Mirage > {text}")

    engine.say(text)
    engine.runAndWait()
