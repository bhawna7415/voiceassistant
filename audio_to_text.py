import speech_recognition as sr

def convert_audio_to_text_and_save(audio_file_path, output_text_file):
    recognizer = sr.Recognizer()

    # Load WAV audio file
    with sr.AudioFile(audio_file_path) as source:
        recognizer.energy_threshold = 6000
        recognizer.adjust_for_ambient_noise(source)
        audio_data = recognizer.record(source)

    try:
        # text = recognizer.recognize_google(audio_data)
        text = recognizer.recognize_google(audio_data, language="en-US")

        print("Text from audio: {}".format(text))

        # Write the text to a file
        with open(output_text_file, "w") as text_file:
            text_file.write(text)
        print("Text has been written to '{}'.".format(output_text_file))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio.")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

convert_audio_to_text_and_save('male.wav', 'output_text.txt')