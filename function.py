import speech_recognition as sr
from pathlib import Path
from gtts import gTTS
import pygame
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Text-to-speech function
def text_to_speech(text):
    try:
        speech_file_path = "speech.mp3"
        tts = gTTS(text)
        tts.save(speech_file_path)
        pygame.mixer.init()
        pygame.mixer.music.load(speech_file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(1)
        pygame.mixer.quit()
        os.remove(speech_file_path)
    except Exception as e:
        print(f"Error in text-to-speech: {e}")

# Speech-to-text function
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Listening... Please speak.")
        try:
            audio_data = recognizer.listen(source)
            print("Processing your speech...")
            text = recognizer.recognize_google(audio_data)
            print(f"Recognized text: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand the audio.")
        except sr.RequestError as e:
            print(f"Could not request results from the speech recognition service; {e}")
        return None

# Example usage
if __name__ == "__main__":
    recognized_text = speech_to_text()
    if recognized_text:
        print(f"Speech to Text Output: {recognized_text}")
        text_to_speech(f"You said: {recognized_text}")
