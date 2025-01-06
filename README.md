# *OptiLearn⚡ - Interactive Learning Assistant*

OptiLearn⚡ is an interactive AI-powered learning assistant designed to enhance the educational experience through conversational AI, real-time video interactions, voice input, and a drawable canvas for interactive learning. It leverages cutting-edge AI models for responsive chat, voice feedback, and image recognition.

> 🚧 *This project is currently under development.* Some features may change or be enhanced in future updates.

## *Features*

- *Conversational AI:* Communicate with an AI-powered tutor using text or voice.
- *Voice Feedback:* Get responses via voice using pyttsx3 and Google TTS.
- *Live Class Integration:* Join real-time live video classes via webcam using OpenCV.
- *Drawable Canvas:* Interactive drawing board where users can draw and submit images for AI interpretation.
- *AI Image Interpretation:* Integration with LLaVA model (via Ollama) to interpret user drawings in real-time.
- *Voice Input Support:* Speak your queries via microphone using Google’s speech recognition API.

## *Tech Stack*

- *Streamlit:* For building the web-based user interface.
- *OpenCV:* For capturing real-time video in the live class feature.
- *SpeechRecognition:* For handling voice inputs via a microphone.
- *pyttsx3 and gTTS:* For generating voice feedback.
- *Pillow:* For image processing on the drawable canvas.
- *Groq API (LLM):* For generating intelligent responses from the Llama model.
- *Ollama (LLaVA Model):* For interpreting user drawings on the canvas.
- *Streamlit Drawable Canvas:* For adding the interactive drawing interface.

## *Installation*

1. *Clone the repository:*
   bash
   git clone https://github.com/yourusername/optilearn.git
   cd optilearn

2. **Install required dependencies:**
   bash
   pip install -r requirements.txt

3. *Set up environment variables:*
   
   Create a .env file in the project directory with your API keys:

   plaintext
   GROQ_API_KEY=your_groq_api_key
   OLLAMA_API_KEY=your_ollama_api_key

4. **Run the application:**

   To run the application, use the following command:

   bash
   streamlit run app.py

## *Usage*

1. *Text Chat:* Type your questions in the input field and click "Send" to get a response.
2. *Voice Input:* Use the microphone button to ask a question via voice.
3. *Live Class:* Click "🎥 Live Class" to start a live video session.
4. *Canvas:* Click "🖍 Canvas" to open the drawing board. Draw and then click "Interpret Drawing" to get an AI response about your drawing.
5. *Save Drawings:* Save your drawings locally by clicking "Save Drawing."

## *Project Structure*

   bash
   OptiLearn/
   │
   ├── app.py               # Main entry point for the Streamlit app
   ├── requirements.txt     # Dependencies
   ├── .env                 # Environment variables (excluded from version control)
   ├── utils/               # Helper modules and constants
   ├── assets/              # Persona images and other assets
   └── README.md            # Project documentation
   

## *Future Development*

- *Refined AI Models:* Future updates will enhance the intelligence of the AI model to handle more complex queries and interactions.
- *Real-Time Feedback:* Introducing real-time speech feedback and enhancements to the voice recognition pipeline.
- *Improved Canvas Integration:* Expanding the capabilities of the drawing canvas to handle more complex interpretations and image recognition.
- *Live Class Enhancements:* Adding multi-user support for the live class feature.
