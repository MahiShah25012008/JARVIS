import pyaudio
import speech_recognition as sr
import pyttsx3
import audioop
import webbrowser
import musicLibrary
import feedparser
import time
import os
from openai import OpenAI
from gtts import gTTS
import pygame

# -----------------------------
# Settings
# -----------------------------

DEVICE_INDEX = 9
INPUT_RATE = 48000
OUTPUT_RATE = 16000
CHANNELS = 2
CHUNK = 1024

# -----------------------------
# Text to speech
# -----------------------------



def speak_old(text):
    print("Jarvis:", text)

    try:
        engine = pyttsx3.init("sapi5")

        engine.setProperty("rate", 160)
        engine.setProperty("volume", 1.0)

        voices = engine.getProperty("voices")

        if voices:
            engine.setProperty("voice", voices[0].id)

        engine.say(str(text))
        engine.runAndWait()

        engine.stop()

    except Exception as e:
        print("TTS Error:", e)

def speak(text):
    tts = gTTS(text)
    tts.save('temp.mp3')

    #Initialize Pygame mixer
    pygame.mixer.init()

    #Load the MP3 file 
    pygame.mixer.music.load('temp.mp3')

    #Play the MP3 file
    pygame.mixer.music.play()

# Keep the program running until the music stops playing 
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.unload()
    os.remove("temp.mp3")


def aiProcess(command):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model="gpt-5.6-luna",
        messages=[
            {
                "role": "system",
                "content": "You are a virtual assistant named Jarvis.Give short responses . "
            },
            {
                "role": "user",
                "content": command
            }
        ]
    )
    return completion.choices[0].message.content



# -----------------------------
# Listen
# -----------------------------

def listen():

    recognizer = sr.Recognizer()

    p = pyaudio.PyAudio()

    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=INPUT_RATE,
            input=True,
            input_device_index=DEVICE_INDEX,
            frames_per_buffer=CHUNK
        )

        print("Listening...")

        frames = []

        # Record for 5 seconds
        for _ in range(int(INPUT_RATE / CHUNK * 5)):
            data = stream.read(
                CHUNK,
                exception_on_overflow=False
            )
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        audio_data = b"".join(frames)

        # -----------------------------
        # Stereo -> Mono
        # -----------------------------

        mono_data = audioop.tomono(
            audio_data,
            2,
            0.5,
            0.5
        )

        # -----------------------------
        # 48000 Hz -> 16000 Hz
        # -----------------------------

        mono_16k, _ = audioop.ratecv(
            mono_data,
            2,
            1,
            INPUT_RATE,
            OUTPUT_RATE,
            None
        )

        # -----------------------------
        # SpeechRecognition AudioData
        # -----------------------------

        audio = sr.AudioData(
            mono_16k,
            OUTPUT_RATE,
            2
        )

        try:
            word = recognizer.recognize_google(audio)

            print("You:", word)

            return word.lower()

        except sr.UnknownValueError:
            print("Could not understand.")
            return ""

        except sr.RequestError as e:
            print("Google Speech Recognition error:", e)
            return ""

    except Exception as e:
        print("Microphone error:", e)

        try:
            p.terminate()
        except:
            pass

        return ""

# -----------------------------
# Jarvis
# -----------------------------

def processCommand(c):
    print("HI")
    if "open google" in c.lower():
       webbrowser.open("https://google.com")
    elif "open facebook" in c.lower():
        webbrowser.open("https://facebook.com")
    elif "open youtube" in c.lower():
       webbrowser.open("https://youtube.com")
    elif "open linkedin" in c.lower():
       webbrowser.open("https://linkedin.com")
    elif c.lower().startswith("play"):
        song = c.lower().split(" ")[1]
        link = musicLibrary.music[song]
        webbrowser.open(link)
    elif "news" in c.lower():
        speak("Getting the latest news.")
        url = "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml"
        try:
            feed = feedparser.parse(url)

            if not feed.entries:
                speak("Sorry, I couldn't find any news right now.")
                return
            speak("Here are the latest headlines.")

            for i, article in enumerate(feed.entries[:5], start=1):
                title = article.get("title", "").strip()

                if title:
                    print(f"Headline {i}: {title}")

                    speak(f"Headline {i}. {title}")

                    time.sleep(0.5)
        except Exception as e:
            print("News error:", e)
            speak("Sorry, I couldn't retrieve the news.")
    
    else:
        # Let OpenAI handle the request
        output = aiProcess(command)
        speak(output)




if __name__ == "__main__":

    speak("Initializing Jarvis")

    while True:

        word = listen()

        if "jarvis" in word :
            speak("Yes?")

            command = listen()

            print("Command:", command)

            # Put your commands here
            processCommand(command)
            time.sleep(1)


