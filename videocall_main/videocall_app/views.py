from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import pickle
import base64
import numpy as np
from PIL import Image
from io import BytesIO
import os
import cv2

# Load the ISL model when the server starts
model_path = os.path.join('C:/Users/HP/OneDrive/Desktop/hack1/HACK-SYNTHESIS-2024/videocall_main/model_pickle.pickle', 'model_pickle.pickle')
with open('C:/Users/HP/OneDrive/Desktop/hack1/HACK-SYNTHESIS-2024/videocall_main/model_pickle.pickle', 'rb') as f:
    isl_model = pickle.load(f)

# Define class labels corresponding to the output of the model
class_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 
                'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 
                'U', 'V', 'W', 'X', 'Y', 'Z']  # Update this list based on your model's output

def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'login.html', {'success': "Registration successful. Please login."})
        else:
            error_message = form.errors.as_text()
            return render(request, 'register.html', {'error': error_message})

    return render(request, 'register.html')

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("/dashboard")
        else:
            return render(request, 'login.html', {'error': "Invalid credentials. Please try again."})

    return render(request, 'login.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {'name': request.user.first_name})

@login_required
def videocall(request):
    return render(request, 'videocall.html', {'name': request.user.first_name + " " + request.user.last_name})

@login_required
def logout_view(request):
    logout(request)
    return redirect("/login")

@login_required
def join_room(request):
    if request.method == 'POST':
        roomID = request.POST['roomID']
        return redirect("/meeting?roomID=" + roomID)
    return render(request, 'joinroom.html')

@login_required
def process_frame(request):
    if request.method == 'POST':
        try:
            # Get the base64-encoded frame from the request
            data = request.POST.get('frame')
            if not data:
                return JsonResponse({'error': 'No frame data provided'}, status=400)

            # Decode the base64 image
            image_data = base64.b64decode(data.split(',')[1])
            image = Image.open(BytesIO(image_data))  # Open the image
            image = np.array(image)  # Convert to NumPy array

            # Preprocess the image (resize and convert to grayscale)
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)  # Convert to grayscale
            image = cv2.resize(image, (48, 48))  # Resize based on model input size
            image = np.expand_dims(image, axis=-1)  # Add a channel dimension
            image = np.expand_dims(image, axis=0)  # Add batch dimension

            # Make prediction with the ISL model
            prediction = isl_model.predict(image)[0]  # Assumes single prediction

            # Convert the one-hot encoded vector to the actual letter
            predicted_index = np.argmax(prediction)  # Get the index of the max value
            predicted_letter = class_labels[predicted_index]  # Map index to letter

            return JsonResponse({'text': predicted_letter})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
