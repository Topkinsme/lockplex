from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import speech_recognition as sr
from pydub import AudioSegment

def home(request):
    return redirect('lockplex')

def lockplex(request):
    return render(request, 'lockplex.html')

def start(request):
    return render(request, 'start.html')

@csrf_exempt  # Disable CSRF for this endpoint (for testing purposes)
def upload_audio(request):
    if request.method == 'POST':
        audio_file = request.FILES.get('audio')
        recording_number = request.POST.get('recording_number')
        random_word = request.POST.get('random_word')
        unique_id = request.POST.get('unique_id')  # Get the unique ID from the request

        if audio_file:
            # Save the file to a specific location (e.g., in a folder named "uploads")
            file_name = f'recording_{unique_id}_{recording_number}_{random_word}.wav'  # Use unique ID in the file name
            with open(f'uploads/{file_name}', 'wb+') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)
            return JsonResponse({'message': 'Audio uploaded successfully!'})
        return JsonResponse({'error': 'No audio file received!'}, status=400)

    return JsonResponse({'error': 'Invalid request method!'}, status=405)


def recordings_list(request):
    # Get the filenames passed in the request (GET parameters)
    filenames = request.GET.getlist('filenames')

    transcriptions = []  # List to hold transcriptions
    recognizer = sr.Recognizer()  # Initialize the recognizer
    score = 0  # Initialize score
    total_files = len(filenames)  # Total number of files

    for filename in filenames:
        file_path = os.path.join('uploads', filename)  # Reference the uploads folder
        absolute_file_path = os.path.abspath(file_path)  # Get the absolute file path
        print(f"Processing file: {absolute_file_path}")  # Debug: Show the absolute file path

        # Convert audio to text
        try:
            # Check if the file exists before trying to load it
            if not os.path.exists(absolute_file_path):
                print(f"File does not exist: {absolute_file_path}")  # Debug: file not found
                transcriptions.append((filename, "File not found.", 0))  # Add score 0 for missing file
                continue  # Skip to the next file

            # Convert the audio file to WAV format using pydub
            wav_file_path = os.path.splitext(absolute_file_path)[0] + '.wav'  # Change extension to .wav
            print(f"Converting to WAV: {wav_file_path}")  # Debug: Show export path

            # Load the audio file using pydub
            audio = AudioSegment.from_file(absolute_file_path)  # Load the original audio file
            audio.export(wav_file_path, format='wav')  # Export as WAV
            print(f"Exported audio to WAV: {wav_file_path}")  # Debug: Confirm export

            # Process the WAV file with speech_recognition
            with sr.AudioFile(wav_file_path) as source:
                audio_data = recognizer.record(source)  # Read the WAV audio file
                text = recognizer.recognize_google(audio_data)  # Convert audio to text
                print(f"Transcript for {filename}: {text}")  # Debug: Show the transcript
                
                # Extract the original word from the filename
                original_word = filename.split('_')[-1].replace('.wav', '')  # Get word before .wav
                print(f"Original word for {filename}: {original_word}")  # Debug: Show original word
                
                # Check if the original word is in the transcript
                if original_word in text.lower():  # Convert to lower case for case-insensitive comparison
                    score += 1  # Increment score if the word is found
                
                transcriptions.append((filename, text, 1 if original_word in text.lower() else 0))  # Append score to transcriptions
        
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            transcriptions.append((filename, "Could not transcribe.", 0))  # Add score 0 for errors

    # Calculate the final score and message
    final_score = score / total_files * 100 if total_files > 0 else 0  # Calculate percentage score
    message = "You're mostly not suffering from a stroke." if final_score > 50 else "You might be suffering a stroke."
    for filename in filenames:
        file_path = os.path.join('uploads', filename)  # Reference the uploads folder
        absolute_file_path = os.path.abspath(file_path)
        wav_file_path = os.path.splitext(absolute_file_path)[0] + '.wav'
        try:
            if os.path.exists(absolute_file_path):
                os.remove(absolute_file_path)  # Delete the original file
                print(f"Deleted original file: {absolute_file_path}")  # Debug: confirm deletion
        except:
            pass
        try:
            if os.path.exists(wav_file_path):
                    os.remove(wav_file_path)  # Delete the WAV file
                    print(f"Deleted WAV file: {wav_file_path}")  # Debug: confirm deletion
        except:
            pass
    return render(request, 'recordings_list.html', {'transcriptions': transcriptions, 'message': message})