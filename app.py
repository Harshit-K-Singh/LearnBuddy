import threading
import os
import io
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from gtts import gTTS
import pyttsx3
import cv2
import speech_recognition as sr
from utils.constants import DARK_GRAY_COLOR, PRIMARY_APP_COLOR, APP_CHAT_FONT, PERSONA_NAME_FONT, SOFIA_TUTOR_PERSONA
from groq import Groq
from dotenv import load_dotenv
from streamlit_drawable_canvas import st_canvas
import ollama
import base64
import PyPDF2
from io import StringIO

load_dotenv()

client = Groq(
    api_key="Enter Your Key")

# Your provided Particle.js HTML
particles_js = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Particles.js</title>
  <style>
  #particles-js {
    position: fixed;
    width: 100vw;
    height: 100vh;
    top: 0;
    left: 0;
    z-index: 1;
  }
  .content {
    position: relative;
    z-index: 1;
    color: white;
  }
  </style>
</head>
<body>
  <div id="particles-js"></div>
  <div class="content"></div>
  <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
  <script>
    particlesJS("particles-js", {
      "particles": {
        "number": {
          "value": 300,
          "density": {
            "enable": true,
            "value_area": 800
          }
        },
        "color": {
          "value": "#ffffff"
        },
        "shape": {
          "type": "circle",
          "stroke": {
            "width": 0,
            "color": "#000000"
          },
          "polygon": {
            "nb_sides": 5
          }
        },
        "opacity": {
          "value": 0.5,
          "random": false,
          "anim": {
            "enable": false,
            "speed": 1,
            "opacity_min": 0.2,
            "sync": false
          }
        },
        "size": {
          "value": 2,
          "random": true,
          "anim": {
            "enable": false,
            "speed": 40,
            "size_min": 0.1,
            "sync": false
          }
        },
        "line_linked": {
          "enable": true,
          "distance": 100,
          "color": "#ffffff",
          "opacity": 0.22,
          "width": 1
        },
        "move": {
          "enable": true,
          "speed": 0.2,
          "direction": "none",
          "random": false,
          "straight": false,
          "out_mode": "out",
          "bounce": true,
          "attract": {
            "enable": false,
            "rotateX": 600,
            "rotateY": 1200
          }
        }
      },
      "interactivity": {
        "detect_on": "canvas",
        "events": {
          "onhover": {
            "enable": true,
            "mode": "grab"
          },
          "onclick": {
            "enable": true,
            "mode": "repulse"
          },
          "resize": true
        },
        "modes": {
          "grab": {
            "distance": 100,
            "line_linked": {
              "opacity": 1
            }
          },
          "bubble": {
            "distance": 400,
            "size": 2,
            "duration": 2,
            "opacity": 0.5,
            "speed": 1
          },
          "repulse": {
            "distance": 200,
            "duration": 0.4
          },
          "push": {
            "particles_nb": 2
          },
          "remove": {
            "particles_nb": 3
          }
        }
      },
      "retina_detect": true
    });
  </script>
</body>
</html>
"""

# Update the page config
st.set_page_config(
    page_title="OptiLearn",
    page_icon="⚡",
    layout="wide",
)

class ChatApp:
    def __init__(self, persona):
        self.persona = persona
        self.messages = [{'role': 'system', 'content': self.persona.system_prompts}]
        self.audio_lock = threading.Lock()
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'pdf_content' not in st.session_state:
            st.session_state.pdf_content = None
        self.voice_feedback = None
        if 'particles_visible' not in st.session_state:
            st.session_state.particles_visible = True
        self.setup_chat_interface()

    def setup_chat_interface(self):
        st.title("OptiLearn⚡")
        st.markdown("### Your AI Tutor")

        self.add_custom_css()

        if st.session_state.particles_visible:
            components.html(particles_js, height=350)
        
        # Create a container for chat history
        chat_container = st.container()
        
        # Create a container for input and options at the bottom
        input_container = st.container()

        with input_container:
            col1, col2 = st.columns([3, 1])
            with col1:
                prompt = st.chat_input("Say something", key="chat_input")
                if prompt:
                    self.send_message(prompt)
            with col2:
                with st.expander("Options ⚙️", expanded=False):
                    if st.button("🎤 Mic", key="mic_button"):
                        self.voice_input()
                    st.button("🎥 Live Class", on_click=self.start_live_class)
                    st.button("🖍️ Canvas", on_click=self.toggle_canvas)
                    st.button("📄 PDF Extractor", on_click=self.toggle_pdf_sidebar)

        if st.session_state.get('canvas_open', False):
            self.setup_drawing_canvas()

        if st.session_state.get('pdf_sidebar_open', False):
            self.setup_pdf_sidebar()

        self.update_chat_display(chat_container)


    def add_custom_css(self):
        st.markdown("""
            <style>
            .stApp {
                background-color: rgba(0, 0, 0, 0.8);
                height: 100vh;
                overflow: hidden;
            }
            div[data-testid="stHeader"], div[data-testid="stToolbar"] {
                background-color: rgba(0, 0, 0, 0);
            }
            .stButton button {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }
            .stButton button:hover {
                background-color: #45a049;
            }
            h1, h3 {
                color: white;
                text-align: center;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }
            .chat-container {
                height: calc(100vh - 300px);
                overflow-y: auto;
                padding: 20px;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                backdrop-filter: blur(10px);
            }
            .stExpander {
                background-color: rgba(255, 255, 255, 0.1) !important;
                border-radius: 10px !important;
            }
            .stExpander[data-expanded="true"] {
                transform: scaleY(-1);
            }
            .stExpander[data-expanded="true"] > div {
                transform: scaleY(-1);
            }
            </style>
        """, unsafe_allow_html=True)
    
    def update_particle_background(self):
        """Displays the particle background if visible."""
        if self.particles_visible:
            components.html(particles_js, height=350)
    def hide_particles(self):
        """Hides the particle background."""
        self.particles_visible = False

    def update_chat_display(self, container):
        with container:
            # st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for chat in st.session_state.chat_history:
                st.markdown(f"**{chat['sender']}:** {chat['message']}")
            st.markdown('</div>', unsafe_allow_html=True)

    def send_message(self, text):
        if text:
            st.session_state.particles_visible = False
            
            st.session_state.chat_history.append({'sender': 'You', 'message': text})
            
            # Modify the message to include PDF context if available
            if st.session_state.pdf_content:
                context_message = {
                    'role': 'system', 
                    'content': f"Use the following PDF content as context for answering the question: {st.session_state.pdf_content[:2000]}"
                }
                self.messages.append(context_message)
            
            self.messages.append({'role': 'user', 'content': text})
            response = self.get_response(text)
            st.session_state.chat_history.append({'sender': 'OptiLearn', 'message': response})
            
            # Remove the PDF context message if it was added
            if st.session_state.pdf_content:
                self.messages.pop(-2)
            
            st.rerun()


    def voice_input(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.write("Listening... Speak now.")
            audio = r.listen(source)
            try:
                text = r.recognize_google(audio)
                st.write(f"You said: {text}")
                self.send_message(text)
            except sr.UnknownValueError:
                st.write("Sorry, I couldn't understand that.")
            except sr.RequestError:
                st.write("There was an error with the speech recognition service.")

    def get_response(self, query):
        chat_completion = client.chat.completions.create(
            messages=self.messages, model="llama3-8b-8192", max_tokens=1000
        )
        return chat_completion.choices[0].message.content

    def speak_response(self, response):
        if self.persona.gender == 'female':
            self.respond_online(response)
        else:
            self.respond(response)

    def respond(self, response):
        with self.audio_lock:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[0].id)
            engine.setProperty('rate', 300)
            engine.save_to_file(response, 'temp.wav')
            engine.runAndWait()
            self.auto_play_audio('temp.wav')

    def respond_online(self, response):
        tts = gTTS(text=response, lang='en')
        filename = "temp.mp3"
        tts.save(filename)
        self.auto_play_audio(filename)
    
    def toggle_canvas(self):
        st.session_state['canvas_open'] = not st.session_state.get('canvas_open', False)

    def auto_play_audio(self, filename):
        try:
            with open(filename, "rb") as audio_file:
                audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/mp3')
        except Exception as e:
            st.error(f"Error loading audio file: {e}")

    def start_live_class(self):
        cap = cv2.VideoCapture(0)
        st_frame = st.empty()
        st.write("Press 'Stop' to end the live class.")
        stop_button = st.button("Stop", key="stop_live_class")
        while cap.isOpened() and not stop_button:
            ret, frame = cap.read()
            if ret:
                st_frame.image(frame, channels="BGR")
            else:
                break
        cap.release()
        st.write("Live class ended.")

    def setup_drawing_canvas(self):
        with st.sidebar:
            st.write("Draw something below:")
            canvas_result = st_canvas(
                fill_color="rgba(255, 255, 255, 0)",
                stroke_width=2,
                stroke_color="black",
                background_color="white",
                height=300,
                width=300,
                drawing_mode="freedraw",
                key="canvas"
            )
            if st.button("Interpret Drawing"):
                if canvas_result.image_data is not None:
                    image = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    img_byte_arr = img_byte_arr.getvalue()

                    encoded_image = base64.b64encode(img_byte_arr).decode('utf-8')

                    llava_response = ollama.chat(
                        model="llava",
                        messages=[
                            {
                                "role": "user",
                                "content": "What does this image represent?",
                                "images": [encoded_image]
                            }
                        ]
                    )
                    st.write("LLaVA Response: ", llava_response['message']['content'])
            if st.button("Save Drawing"):
                if canvas_result.image_data is not None:
                    image = Image.fromarray(canvas_result.image_data)
                    image.save("drawing.png")
                    st.success("Drawing saved as drawing.png!")
                else:
                    st.warning("No drawing to save!")

    def toggle_pdf_sidebar(self):
        st.session_state['pdf_sidebar_open'] = not st.session_state.get('pdf_sidebar_open', False)
        st.rerun()

    def setup_pdf_sidebar(self):
        with st.sidebar:
            st.header("PDF Extractor")
            uploaded_file = st.file_uploader("Upload your PDF", type=['pdf'])
            
            if uploaded_file is not None:
                try:
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                    
                    st.session_state.pdf_content = text
                    st.success("PDF uploaded successfully! You can now ask questions about its content.")
                    
                    with st.expander("View PDF Content"):
                        st.text(text[:1000] + "..." if len(text) > 1000 else text)
                
                except Exception as e:
                    st.error(f"Error processing PDF: {str(e)}")

if __name__ == "__main__":
    persona = SOFIA_TUTOR_PERSONA  # Define your persona
    app = ChatApp(persona)
