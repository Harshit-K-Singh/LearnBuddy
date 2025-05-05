import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import random
import time
import json
import numpy as np
from PIL import Image
import io
import base64
import PyPDF2
from utils.constants import DARK_GRAY_COLOR, PRIMARY_APP_COLOR, APP_CHAT_FONT, PERSONA_NAME_FONT, SOFIA_TUTOR_PERSONA
from streamlit_drawable_canvas import st_canvas
from groq import Groq
import pdfkit
import os
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Initialize Groq client with API key from environment variable
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Setup page configuration
st.set_page_config(
    page_title="LearnBuddy",
    page_icon="⚡",
    layout="wide",
)

# Particles.js animation HTML
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
    z-index: -1;
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

# Icons for the chat messages
icons = {
    "assistant": "⚡",
    "user": "👤"
}

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant", 
        "content": f"Hello! I'm {SOFIA_TUTOR_PERSONA['name']}, an AI tutor. How can I help you with your learning journey today?",
        "timestamp": datetime.now().strftime("%H:%M")
    }]

if "show_animation" not in st.session_state:
    st.session_state.show_animation = True

if "task_planner_open" not in st.session_state:
    st.session_state.task_planner_open = False

if "learning_tasks" not in st.session_state:
    st.session_state.learning_tasks = []

if "pdf_sidebar_open" not in st.session_state:
    st.session_state.pdf_sidebar_open = False

if "learning_path_open" not in st.session_state:
    st.session_state.learning_path_open = False

if "canvas_open" not in st.session_state:
    st.session_state.canvas_open = False

if "learning_context" not in st.session_state:
    st.session_state.learning_context = {
        "skill_level": "Beginner",
        "subject_focus": [],
        "learning_goals": ""
    }

if "generated_path" not in st.session_state:
    st.session_state.generated_path = ""

if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = None

# Mock LLM response
def get_mock_response(prompt):
    """Simulate an AI response to demonstrate the UI"""
    # Using a simple template system for demo purposes
    responses = [
        f"I understand you're asking about '{prompt}'. As your AI tutor, I'd suggest breaking this down step by step.",
        f"That's a great question about '{prompt}'! Let me explain this concept in a way that's easy to understand.",
        f"When it comes to '{prompt}', there are a few key principles to keep in mind. First, let's clarify the fundamentals.",
        f"I'd be happy to help you learn about '{prompt}'. This is actually a fascinating topic that connects to many other areas."
    ]
    return random.choice(responses) + "\n\nIs there a specific aspect of this topic you'd like to explore further?"

# Function to add custom CSS
def add_custom_css():
    st.markdown("""
        <style>
        /* Main App Styling */
        .stApp {
            background: linear-gradient(135deg, #1a1a1a, #0a0a0a);
            color: white;
            font-family: 'Inter', sans-serif;
        }
        
        /* Hide default Streamlit elements */
        div[data-testid="stHeader"],
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        footer {
            display: none !important;
        }
        
        /* Main Title */
        .main-title {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            padding: 10px;
            border-radius: 20px;
            margin: 10px auto;
            max-width: 800px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(76, 175, 80, 0.2);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .main-title h1 {
            margin: 0;
            font-size: 2.2em;
            font-weight: 700;
            background: linear-gradient(120deg, #ffffff, #e0e0e0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .main-title h3 {
            margin: 5px 0 0 0;
            font-size: 1.1em;
            opacity: 0.9;
            font-weight: 500;
        }

        # /* Chat Container */
        # .chat-container {
        #     height: calc(100vh - 200px);
        #     overflow-y: auto;
        #     margin-bottom: 80px;
        #     padding: 10px;
        #     border-radius: 10px;
        #     background: rgba(0, 0, 0, 0.2);
        # }
        
        /* Streamlit Chat Message Styling */
        [data-testid="stChatMessage"] {
            background: transparent !important;
            border: none !important;
            margin-bottom: 15px !important;
            padding: 10px !important;
            border-radius: 15px !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        
        /* User message styling */
        [data-testid="stChatMessage"][data-testid="stChatMessageUser"] {
            background: rgba(76, 175, 80, 0.1) !important;
        }
        
        /* Assistant message styling */
        [data-testid="stChatMessage"][data-testid="stChatMessageAssistant"] {
            background: rgba(255, 255, 255, 0.05) !important;
        }

        .stChatMessage [data-testid="stMarkdownContainer"] p {
            font-size: 1em;
            line-height: 1.5;
            margin: 0;
        }
        
        /* Message timestamp */
        .message-timestamp {
            font-size: 0.7em;
            color: rgba(255, 255, 255, 0.6);
            text-align: right;
            margin-top: 5px;
        }

        /* Input Container - Fixed at the bottom */
        .chat-input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: rgba(26, 26, 26, 0.95);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            padding: 15px;
            z-index: 1000;
        }

        /* Input Styling */
        .stChatInputContainer {
            background-color: transparent !important;
            border: none !important;
            padding: 0 !important;
        }

        .stChatInputContainer textarea {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 25px !important;
            color: white !important;
            padding: 15px 25px !important;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: rgba(0, 0, 0, 0.3);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Options menu */
        .stExpander {
            background: rgba(255, 255, 255, 0.05) !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            margin-bottom: 10px !important;
        }
        
        /* Task styling */
        .task-item {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .task-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 5px;
        }
        
        .task-title {
            font-weight: bold;
            color: #4CAF50;
        }
        
        .task-priority-high {
            color: #ff5252;
        }
        
        .task-priority-medium {
            color: #ffb142;
        }
        
        .task-priority-low {
            color: #2ed573;
        }
        
        .task-completed {
            text-decoration: line-through;
            opacity: 0.7;
        }
        
        /* Learning path container */
        .learning-path-container {
            background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .section-header {
            color: #4CAF50;
            font-size: 1.2em;
            margin-top: 15px;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

def toggle_task_planner():
    st.session_state.task_planner_open = not st.session_state.task_planner_open
    st.session_state.pdf_sidebar_open = False
    st.session_state.learning_path_open = False
    st.session_state.canvas_open = False

def toggle_pdf_sidebar():
    st.session_state.pdf_sidebar_open = not st.session_state.pdf_sidebar_open
    st.session_state.task_planner_open = False
    st.session_state.learning_path_open = False
    st.session_state.canvas_open = False
    
def toggle_learning_path():
    st.session_state.learning_path_open = not st.session_state.get('learning_path_open', False)
    st.session_state.task_planner_open = False
    st.session_state.pdf_sidebar_open = False
    st.session_state.canvas_open = False
    
def toggle_canvas():
    st.session_state.canvas_open = not st.session_state.get('canvas_open', False)
    st.session_state.task_planner_open = False
    st.session_state.pdf_sidebar_open = False
    st.session_state.learning_path_open = False

def setup_task_planner():
    st.header("Learning Path Tasks")
    
    # Initialize task list in session state if not exists
    if 'learning_tasks' not in st.session_state:
        st.session_state.learning_tasks = []
    
    # Add new task
    st.subheader("Add New Task")
    
    # Create input widgets with empty default values
    task_title = st.text_input("Task Title", key="new_task_title")
    task_description = st.text_area("Task Description", key="new_task_description")
    task_due_date = st.date_input("Due Date", key="new_task_due_date")
    task_priority = st.select_slider(
        "Priority",
        ["Low", "Medium", "High"],
        value="Medium",
        key="new_task_priority"
    )
    
    if st.button("Add Task", key="add_task"):
        if task_title:
            new_task = {
                "title": task_title,
                "description": task_description,
                "due_date": task_due_date.strftime("%Y-%m-%d"),
                "priority": task_priority,
                "completed": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.learning_tasks.append(new_task)
            st.success("Task added successfully!")
            # Clear inputs by rerunning the app
            st.rerun()
        else:
            st.warning("Please enter a task title!")
    
    # Display tasks
    st.subheader("Your Tasks")
    if st.session_state.learning_tasks:
        for i, task in enumerate(st.session_state.learning_tasks):
            with st.expander(f"{'✅' if task['completed'] else '⏳'} {task['title']}", expanded=False):
                st.write(f"**Description:** {task['description']}")
                st.write(f"**Due Date:** {task['due_date']}")
                st.write(f"**Priority:** {task['priority']}")
                st.write(f"**Created:** {task['created_at']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Toggle Complete", key=f"toggle_{i}"):
                        st.session_state.learning_tasks[i]['completed'] = not st.session_state.learning_tasks[i]['completed']
                        st.rerun()
                with col2:
                    if st.button("Delete Task", key=f"delete_{i}"):
                        st.session_state.learning_tasks.pop(i)
                        st.rerun()
        
        # Task statistics
        completed_tasks = sum(1 for task in st.session_state.learning_tasks if task['completed'])
        total_tasks = len(st.session_state.learning_tasks)
        progress = completed_tasks / total_tasks if total_tasks > 0 else 0
        
        st.progress(progress)
        st.write(f"Progress: {completed_tasks}/{total_tasks} tasks completed")
        
        # Sort tasks by priority and due date
        sorted_tasks = sorted(
            st.session_state.learning_tasks,
            key=lambda x: (not x['completed'], x['priority'] == 'High', x['due_date'])
        )
        
        # Display upcoming tasks
        st.subheader("Upcoming Tasks")
        for task in sorted_tasks[:3]:  # Show top 3 tasks
            if not task['completed']:
                st.write(f"• {task['title']} (Due: {task['due_date']})")
    else:
        st.info("No tasks yet. Add some tasks to get started!")
    
    # Export/Import tasks
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Export Tasks"):
            tasks_json = json.dumps(st.session_state.learning_tasks, indent=2)
            st.download_button(
                label="Download Tasks",
                data=tasks_json,
                file_name="learning_tasks.json",
                mime="application/json"
            )
    with col2:
        uploaded_file = st.file_uploader("Import Tasks", type=['json'])
        if uploaded_file:
            try:
                imported_tasks = json.load(uploaded_file)
                st.session_state.learning_tasks.extend(imported_tasks)
                st.success("Tasks imported successfully!")
                st.rerun()
            except:
                st.error("Error importing tasks. Please check the file format.")

def setup_pdf_sidebar():
    st.header("📄 PDF Extractor")
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
            
            # Add PDF Question functionality
            st.subheader("Ask about this PDF")
            pdf_question = st.text_input("Enter your question about the PDF:", key="pdf_question_input")
            
            if st.button("Ask Question", key="ask_pdf_question"):
                if pdf_question:
                    # Create a prompt combining the question and PDF content
                    pdf_prompt = f"""
                    Based on the following document content, please answer this question:
                    
                    QUESTION: {pdf_question}
                    
                    DOCUMENT CONTENT:
                    {text[:3000]}  # Limit content to avoid token limits
                    
                    Please provide a detailed, accurate answer based only on the information in the document.
                    """
                    
                    with st.spinner("Analyzing PDF content..."):
                        # Call Groq API for response
                        completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": pdf_prompt}],
                            model="llama3-8b-8192",
                            max_tokens=1000
                        )
                        
                        response = completion.choices[0].message.content
                    
                    # Add the question and response to chat history
                    current_time = datetime.now().strftime("%H:%M")
                    
                    # Add user question to chat
                    st.session_state.messages.append({
                        'role': 'user',
                        'content': f"📄 PDF Question: {pdf_question}",
                        'timestamp': current_time
                    })
                    
                    # Add AI response to chat
                    st.session_state.messages.append({
                        'role': 'assistant',
                        'content': response,
                        'timestamp': datetime.now().strftime("%H:%M")
                    })
                    
                    st.success("Response added to chat!")
                    
                    # Force app rerun to update chat
                    st.rerun()
                else:
                    st.warning("Please enter a question first!")
        
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")

def setup_learning_path():
    st.header("Learning Path")
    
    # Add custom CSS for better UI
    st.markdown("""
        <style>
        .learning-path-container {
            background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .section-header {
            color: #4CAF50;
            font-size: 1.2em;
            margin-top: 15px;
            margin-bottom: 10px;
        }
        .stButton>button {
            width: 100%;
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px;
            margin: 5px 0;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Learning Context
    with st.container():
        st.markdown('<div class="learning-path-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Learning Context</div>', unsafe_allow_html=True)
        
        st.session_state.learning_context["skill_level"] = st.select_slider(
            "Skill Level", 
            ["Beginner", "Intermediate", "Advanced"],
            value=st.session_state.learning_context["skill_level"],
            key="learning_path_skill_level"
        )
        st.session_state.learning_context["subject_focus"] = st.multiselect(
            "Subject Focus", 
            ["Art", "Science", "Math", "Language", "History", "Geography", "Music", "Design", "Technology"],
            default=st.session_state.learning_context["subject_focus"],
            key="learning_path_subjects"
        )
        st.session_state.learning_context["learning_goals"] = st.text_area(
            "Learning Goals",
            value=st.session_state.learning_context["learning_goals"],
            placeholder="What do you want to learn?",
            key="learning_path_goals"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Learning Style
    with st.container():
        st.markdown('<div class="learning-path-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Learning Style</div>', unsafe_allow_html=True)
        
        learning_style = st.selectbox(
            "Preferred Learning Style",
            ["Visual", "Auditory", "Reading/Writing", "Kinesthetic", "Mixed"],
            key="learning_path_style"
        )
        pace = st.select_slider(
            "Learning Pace",
            ["Slow", "Moderate", "Fast"],
            value="Moderate",
            key="learning_path_pace"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Time Commitment
    with st.container():
        st.markdown('<div class="learning-path-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Time Commitment</div>', unsafe_allow_html=True)
        
        weekly_hours = st.slider(
            "Hours per week",
            min_value=1,
            max_value=40,
            value=10,
            key="learning_path_hours"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Generate Learning Path
    if st.button("Generate Learning Path", key="generate_path"):
        # Create a prompt for the AI to generate a personalized learning path
        learning_path_prompt = f"""
        Create a personalized learning path for a {st.session_state.learning_context['skill_level']} student
        interested in {', '.join(st.session_state.learning_context['subject_focus'])}.
        Learning goals: {st.session_state.learning_context['learning_goals']}
        Learning style: {learning_style}
        Learning pace: {pace}
        Weekly commitment: {weekly_hours} hours

        Please provide a detailed learning path including:
        1. Learning Objectives
           - Short-term goals (1-2 weeks)
           - Medium-term goals (1-2 months)
           - Long-term goals (3-6 months)
        
        2. Learning Sequence
           - Week-by-week breakdown
           - Daily learning activities
           - Practice exercises
        
        3. Resources
           - Recommended books
           - Online courses
           - Tools and software
           - Practice materials
        
        4. Assessment Points
           - Weekly checkpoints
           - Monthly progress reviews
           - Skill assessments
        
        5. Support System
           - Peer learning opportunities
           - Expert guidance
           - Community resources
        """
        
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": learning_path_prompt}],
            model="llama3-8b-8192",
            max_tokens=2000
        )
        
        # Store the generated path in session state
        st.session_state.generated_path = completion.choices[0].message.content
        
        with st.expander("View Learning Path", expanded=True):
            st.markdown(st.session_state.generated_path)
            
            # Add download button for PDF
            if st.button("Download Learning Path as PDF", key="download_path"):
                try:
                    # Create a temporary HTML file
                    html_content = """
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            body {{ 
                                font-family: Arial, sans-serif; 
                                line-height: 1.6;
                                margin: 40px;
                                color: #333;
                            }}
                            h1 {{ 
                                color: #4CAF50; 
                                text-align: center;
                                border-bottom: 2px solid #4CAF50;
                                padding-bottom: 10px;
                            }}
                            h2 {{ 
                                color: #45a049;
                                margin-top: 30px;
                            }}
                            .section {{ 
                                margin: 20px 0;
                                padding: 15px;
                                background: #f9f9f9;
                                border-radius: 5px;
                            }}
                            .info-box {{ 
                                background: #f5f5f5; 
                                padding: 20px; 
                                border-radius: 5px; 
                                margin: 20px 0;
                                border-left: 4px solid #4CAF50;
                            }}
                            .info-box h3 {
                                margin-top: 0;
                                color: #4CAF50;
                            }}
                            .info-box p {
                                margin: 5px 0;
                            }}
                            ul {{ 
                                margin-left: 20px;
                            }}
                            li {{ 
                                margin: 5px 0;
                            }}
                        </style>
                    </head>
                    <body>
                        <h1>Your Personalized Learning Path</h1>
                        
                        <div class="info-box">
                            <h3>Learning Context</h3>
                            <p><strong>Skill Level:</strong> {st.session_state.learning_context['skill_level']}</p>
                            <p><strong>Subject Focus:</strong> {', '.join(st.session_state.learning_context['subject_focus'])}</p>
                            <p><strong>Learning Goals:</strong> {st.session_state.learning_context['learning_goals']}</p>
                            <p><strong>Learning Style:</strong> {learning_style}</p>
                            <p><strong>Learning Pace:</strong> {pace}</p>
                            <p><strong>Weekly Commitment:</strong> {weekly_hours} hours</p>
                        </div>

                        <div class="section">
                            {st.session_state.generated_path.replace('\n', '<br>')}
                        </div>
                    </body>
                    </html>
                    """
                    
                    # Save HTML content to a temporary file
                    with open("temp_learning_path.html", "w", encoding="utf-8") as f:
                        f.write(html_content)
                    
                    # Get wkhtmltopdf path from environment variable or use default based on OS
                    wkhtmltopdf_path = os.getenv('PDF_WKHTMLTOPDF_PATH', 
                                                '/usr/local/bin/wkhtmltopdf' if os.name != 'nt' else 
                                                'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
                    
                    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
                    pdf = pdfkit.from_file("temp_learning_path.html", False, configuration=config)
                    
                    # Clean up temporary file
                    os.remove("temp_learning_path.html")
                    
                    # Create download button
                    st.download_button(
                        label="Download PDF",
                        data=pdf,
                        file_name="learning_path.pdf",
                        mime="application/pdf"
                    )
                    
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
                    st.info("""
                        To generate PDFs, please:
                        1. Install wkhtmltopdf:
                           - Windows: Download from https://wkhtmltopdf.org/downloads.html
                           - Linux: `sudo apt-get install wkhtmltopdf`
                           - Mac: `brew install wkhtmltopdf`
                        2. Install pdfkit: `pip install pdfkit`
                        3. Make sure wkhtmltopdf is in your system PATH
                    """)

def setup_drawing_canvas():
    st.sidebar.header("🖍️ Drawing Canvas")
    
    with st.sidebar:
        st.write("Choose how to create your image:")
        
        # Simple toggle switch for draw/upload
        input_method = st.radio("Input Method", ["Draw", "Upload"], horizontal=True)
        
        if input_method == "Draw":
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
            image_data = canvas_result.image_data if canvas_result.image_data is not None else None
        else:
            uploaded_image = st.file_uploader("Choose an image...", type=['png', 'jpg', 'jpeg'], key="image_uploader")
            if uploaded_image is not None:
                image = Image.open(uploaded_image)
                image = image.resize((300, 300))
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                image_data = np.array(image)
            else:
                image_data = None
        
        # Add text input for custom questions
        custom_question = st.text_input("Ask a question about your image:", 
                                      placeholder="e.g., What does this image represent?",
                                      key="drawing_question")
        
        if st.button("Analyze Image", key="analyze_image"):
            if image_data is not None:
                # Convert image to bytes
                img_byte_arr = io.BytesIO()
                image = Image.fromarray(image_data.astype('uint8'), 'RGBA')
                image.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                encoded_image = base64.b64encode(img_byte_arr).decode('utf-8')

                # Use the custom question if provided, otherwise use default
                question = custom_question if custom_question else "What does this image represent?"

                # Use Groq Vision model with correct message format
                completion = client.chat.completions.create(
                    model="meta-llama/llama-4-maverick-17b-128e-instruct",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": question
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{encoded_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    temperature=1,
                    max_completion_tokens=1024,
                    top_p=1,
                    stream=False,
                    stop=None,
                )
                
                # Add user message to chat history
                current_time = datetime.now().strftime("%H:%M")
                st.session_state.messages.append({
                    'role': 'user',
                    'content': f"{question} [Image uploaded]",
                    'timestamp': current_time
                })
                
                # Add AI response to chat history
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': completion.choices[0].message.content,
                    'timestamp': datetime.now().strftime("%H:%M")
                })
                
                st.success("Analysis complete! Check the chat for results.")
                st.rerun()
            else:
                st.warning("Please either draw something or upload an image first!")

# Add custom CSS
add_custom_css()

# Render the title
st.markdown("""
    <div class="main-title">
        <h1>LearnBuddy⚡</h1>
        <h3>Your AI Tutor</h3>
    </div>
""", unsafe_allow_html=True)

# Show particles animation if enabled
if st.session_state.show_animation:
    components.html(particles_js, height=150)

# Render the chat history in a scrollable container
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for chat in st.session_state.messages:
        with st.chat_message(
            name=chat['role'].lower(),
            avatar=icons[chat['role']]
        ):
            st.write(f"{chat['message'] if 'message' in chat else chat['content']}")
            st.markdown(f'<div class="message-timestamp">Sent at {chat["timestamp"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar with options
with st.sidebar:
    st.title("Options")
    
    with st.expander("Tools ⚙️", expanded=False):
        if st.button("🎤 Voice Input", help="Use voice input to ask questions", key="voice_btn"):
            st.toast("Voice input is not implemented in this demo")
            
        if st.button("🎥 Live Class", help="Start an interactive live class session", key="live_btn"):
            st.toast("Live class is not implemented in this demo")
            
        if st.button("🖍️ Drawing", help="Open drawing canvas for visual explanations", key="draw_btn"):
            toggle_canvas()
            st.rerun()
            
        if st.button("📄 PDF Upload", help="Upload and analyze PDF documents", key="pdf_btn"):
            toggle_pdf_sidebar()
            st.rerun()
            
        if st.button("📚 Learning Path", help="Create your personalized learning path", key="path_btn"):
            toggle_learning_path()
            st.rerun()
            
        if st.button("📋 Tasks", help="Manage your learning tasks", key="task_btn"):
            toggle_task_planner()
            st.rerun()
    
    with st.expander("Settings 🛠️", expanded=False):
        if st.button("Clear Chat History"):
            st.session_state.messages = [{
                "role": "assistant", 
                "content": "Chat history cleared. How can I help you?",
                "timestamp": datetime.now().strftime("%H:%M")
            }]
            st.session_state.show_animation = True
            st.rerun()
        
        animation_toggle = st.toggle("Show Particles Animation", value=st.session_state.show_animation)
        if animation_toggle != st.session_state.show_animation:
            st.session_state.show_animation = animation_toggle
            st.rerun()
    
    # Display task planner or PDF sidebar based on state
    if st.session_state.task_planner_open:
        setup_task_planner()
    
    if st.session_state.pdf_sidebar_open:
        setup_pdf_sidebar()
        
    if st.session_state.learning_path_open:
        setup_learning_path()
        
    if st.session_state.canvas_open:
        setup_drawing_canvas()

# Fixed chat input at the bottom
st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
prompt = st.chat_input("Ask me anything...", key="chat_input")
st.markdown('</div>', unsafe_allow_html=True)

# Handle message sending
if prompt:
    st.session_state.show_animation = False
    
    # Add user message to chat history
    current_time = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({
        'role': 'user',
        'content': prompt,
        'timestamp': current_time
    })
    
    # Get AI response - in real implementation, this would call an LLM
    with st.spinner("Thinking..."):
        # Simulate a slight delay to mimic LLM processing
        time.sleep(1)
        assistant_response = get_mock_response(prompt)
    
    # Add assistant response to chat history
    st.session_state.messages.append({
        'role': 'assistant',
        'content': assistant_response,
        'timestamp': datetime.now().strftime("%H:%M")
    })
    
    st.rerun()
