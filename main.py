import os
import speech_recognition as sr
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.document_loaders import TextLoader
from langchain.prompts import PromptTemplate
from gtts import gTTS
from pydub import AudioSegment
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor()

def split_audio(input_file, output_folder, chunk_duration_ms):
    ffmpeg_path = "/usr/bin/ffmpeg"  
    AudioSegment.ffmpeg = ffmpeg_path

    sound = AudioSegment.from_wav(input_file)
    duration = len(sound)
    
    for i, start in enumerate(range(0, duration, chunk_duration_ms)):
        chunk = sound[start:start + chunk_duration_ms]
        chunk.export(os.path.join(output_folder, f"chunk_{i + 1}.wav"), format="wav")

# def split_audio(input_file, output_folder, chunk_duration_ms):
#     ffmpeg_path = "/usr/bin/ffmpeg"
#     AudioSegment.ffmpeg = ffmpeg_path

#     sound = AudioSegment.from_wav(input_file)
#     duration = len(sound)
    
#     with ThreadPoolExecutor() as executor:
#         futures = []

#         for i, start in enumerate(range(0, duration, chunk_duration_ms)):
#             chunk = sound[start:start + chunk_duration_ms]
#             output_file = os.path.join(output_folder, f"chunk_{i + 1}.wav")

#             futures.append(executor.submit(chunk.export, output_file, format="wav"))

#         # Wait for all threads to complete                               
#         for future in futures:
#             future.result()

def convert_chunks_to_text(input_folder, output_text_file):
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 3000 
    with open(output_text_file, "w") as text_file:
        for filename in os.listdir(input_folder):
            if filename.endswith(".wav"):
                audio_file_path = os.path.join(input_folder, filename)
                with sr.AudioFile(audio_file_path) as source:
                    recognizer.adjust_for_ambient_noise(source)
                    try:
                        audio_data = recognizer.record(source)
                        text_chunk = recognizer.recognize_google(audio_data, language="en-US")
                        text_file.write(text_chunk + '\n')
                    except sr.UnknownValueError:
                        print(f"Could not recognize speech in {filename}")

def summarize_text(input_text_file, output_summary_file):
    loader = TextLoader(input_text_file)
    docs = loader.load()

    prompt_template = """Write a concise summary of the following:
    "{text}"
    CONCISE SUMMARY:"""
    prompt = PromptTemplate.from_template(prompt_template)

    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    summarize_chain = load_summarize_chain(llm=llm, document_variable_name="text")

    result = summarize_chain.run(docs)
    print(result)

    with open(output_summary_file, "w") as summary_file:
        summary_file.write(result)
    print("Summary has been written to '{}'.".format(output_summary_file))

def convert_summary_to_audio(summary_text, output_audio_file):
    tts = gTTS(text=summary_text, lang='en')
    tts.save(output_audio_file)
    print(f"Summary audio saved to {output_audio_file}")

# Provide the path to your input audio file
input_audio_file = os.getcwd() + "/demo1.wav"

# Set the folder where you want to save the chunks
output_folder = os.getcwd() + "/chunks"

# Create or replace the "chunks" folder
if os.path.exists(output_folder):
    for file in os.listdir(output_folder):
        os.remove(os.path.join(output_folder, file))
else:
    os.makedirs(output_folder)

# Define the duration of each chunk in milliseconds
chunk_duration_ms = 30000  

# Call the function to split the audio
split_audio(input_audio_file, output_folder, chunk_duration_ms)

# Convert chunked audio files to text
output_text_file = os.getcwd() + "/output_text.txt"
convert_chunks_to_text(output_folder, output_text_file)

# Summarize text file
output_summary_file = os.getcwd() + "/output_summary.txt"
summarize_text(output_text_file, output_summary_file)

# Convert summary text to audio
output_audio_file = os.getcwd() + "/output_summary_audio.wav"
with open(output_summary_file, 'r') as file:
    summary_text = file.read()
convert_summary_to_audio(summary_text, output_audio_file)
