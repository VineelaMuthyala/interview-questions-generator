import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def configure_gemini_api():
    """Configure Gemini API with the key from environment variables"""
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        return True, api_key
    except Exception as e:
        st.error(f"Error configuring Gemini API: {str(e)}")
        return False, None

def generate_questions(topic, question_type, difficulty_level, num_questions=50):
    """Generate questions using Gemini API"""
    
    # Configure the API
    success, api_key = configure_gemini_api()
    if not success:
        return None
    
    # Create the prompt based on question type and difficulty level
    if question_type == "Theoretical":
        prompt_template = f"""
        Generate {num_questions} theoretical interview questions for students on the topic: {topic} with {difficulty_level} difficulty level
        
        Requirements:
        - Questions should be specifically at {difficulty_level} difficulty level
        - No repetation of questions
        - Include conceptual, analytical, and critical thinking questions appropriate for {difficulty_level} level
        - Each question should have a detailed answer
        - Format the output as markdown with the following structure:
          ## Question [number]
          **Question:** [Question text]
          **Answer:** [Detailed answer]
        
        For {difficulty_level} difficulty:
        - Easy: Focus on basic concepts, definitions, and simple explanations
        - Medium: Cover intermediate concepts requiring deeper understanding and application
        - Hard: Include advanced concepts, complex scenarios, and questions requiring synthesis of multiple concepts
        """
    else:  # Code-based
        prompt_template = f"""
        Generate {num_questions} coding interview questions for students on the topic: {topic} with {difficulty_level} difficulty level
        
        Requirements:
        - Questions should be specifically at {difficulty_level} difficulty level
        - No repetation of questions
        - Include questions about syntax, logic, problem-solving, and implementation appropriate for {difficulty_level} level
        - Each question should have a detailed answer with code examples where applicable
        - Format the output as markdown with the following structure:
          ## Question [number]
          **Question:** [Question text]
          **Answer:** [Detailed answer with code examples if needed]
        
        For {difficulty_level} difficulty:
        - Easy: Basic coding tasks, simple algorithms, fundamental concepts
        - Medium: Moderate complexity algorithms, data structures implementation, optimization problems
        - Hard: Complex algorithms, advanced optimization, system design questions, challenging edge cases
        """
    
    try:
        # Try different model names based on availability
        model_names = [
            'gemini-1.5-pro',         # Latest stable model
            'gemini-1.5-flash',       # Faster variant
            'gemini-2.0-flash',       # If available
            'models/gemini-1.5-pro',  # With models/ prefix
            'models/gemini-1.5-flash' # With models/ prefix
        ]
        
        error_messages = []
        
        for model_name in model_names:
            try:
                # Initialize the model
                model = genai.GenerativeModel(model_name)
                
                # Generate response
                response = model.generate_content(prompt_template)
                return response.text
                
            except Exception as e:
                error_messages.append(f"{model_name}: {str(e)}")
                continue
        
        # If all models failed, show all error messages
        st.error("Failed to generate content with all available models:")
        for error in error_messages:
            st.error(f"  - {error}")
        return None
        
    except Exception as e:
        st.error(f"Error generating questions: {str(e)}")
        return None

def save_to_markdown(content, filename):
    """Save content to a markdown file"""
    try:
        # Ensure filename has .md extension
        if not filename.endswith('.md'):
            filename += '.md'
        
        # Create the file path (saves in current directory)
        file_path = os.path.join(os.getcwd(), filename)
        
        # Write content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="Interview Questions Generator",
        page_icon="📝",
        layout="wide"
    )
    
    st.title("📝 Interview Questions Generator")
    st.markdown("Generate interview questions for students using Gemini AI")
    
    # Check if API key exists in environment
    api_key = os.getenv('GEMINI_API_KEY')
    
    # Sidebar for information and status
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        if api_key:
            st.success("✅ Gemini API key loaded from .env file")
            st.info(f"API Key: {'*' * (len(api_key) - 4)}{api_key[-4:]}")
        else:
            st.error("❌ Gemini API key not found!")
            st.warning("Please ensure your .env file contains GEMINI_API_KEY")
            
        st.markdown("---")
        st.markdown("### 📄 .env file example:")
        st.code("GEMINI_API_KEY=your_api_key_here")
        st.markdown("Place the .env file in the same directory as your script.")
    
    # Main interface
    if api_key:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Input fields
            topic = st.text_input(
                "📚 Topic",
                placeholder="e.g., Python Programming, Data Structures, Machine Learning",
                help="Enter the subject topic for the interview questions"
            )
            
            question_type = st.selectbox(
                "❓ Question Type",
                ["Theoretical", "Code-based"],
                help="Choose the type of questions you want to generate"
            )
            
            difficulty_level = st.selectbox(
                "🔄 Difficulty Level",
                ["Easy", "Medium", "Hard", "Mixed"],
                help="Choose the difficulty level for the questions"
            )
            
            num_questions = st.slider(
                "🔢 Number of Questions",
                min_value=10,
                max_value=100,
                value=50,
                step=5,
                help="Select how many questions to generate"
            )
            
            filename = st.text_input(
                "📄 Output Filename",
                value=f"interview_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                help="Enter the filename for the markdown file (without extension)"
            )
        
        with col2:
            st.markdown("### 📋 Instructions")
            st.markdown("""
            1. Ensure .env file contains GEMINI_API_KEY
            2. Specify the topic for questions
            3. Choose question type
            4. Select difficulty level
            5. Set number of questions
            6. Enter output filename
            7. Click 'Generate Questions'
            """)
            
            if topic and filename:
                st.success("✅ Ready to generate!")
        
        # Generate button
        if st.button("🚀 Generate Questions", type="primary", use_container_width=True):
            if not topic:
                st.error("Please enter a topic")
            elif not filename:
                st.error("Please enter a filename")
            else:
                with st.spinner("Generating questions... This may take a moment."):
                    # Handle "Mixed" difficulty level
                    if difficulty_level == "Mixed":
                        # For mixed difficulty, divide questions among the three levels
                        easy_count = num_questions // 3
                        medium_count = num_questions // 3
                        hard_count = num_questions - easy_count - medium_count
                        
                        questions_parts = []
                        
                        # Generate questions for each difficulty level
                        with st.spinner("Generating Easy questions..."):
                            easy_questions = generate_questions(topic, question_type, "Easy", easy_count)
                            if easy_questions:
                                questions_parts.append(f"# Easy Level Questions\n\n{easy_questions}")
                        
                        with st.spinner("Generating Medium questions..."):
                            medium_questions = generate_questions(topic, question_type, "Medium", medium_count)
                            if medium_questions:
                                questions_parts.append(f"# Medium Level Questions\n\n{medium_questions}")
                        
                        with st.spinner("Generating Hard questions..."):
                            hard_questions = generate_questions(topic, question_type, "Hard", hard_count)
                            if hard_questions:
                                questions_parts.append(f"# Hard Level Questions\n\n{hard_questions}")
                        
                        # Combine all questions
                        questions_content = "\n\n---\n\n".join(questions_parts)
                    else:
                        # Generate questions for a single difficulty level
                        questions_content = generate_questions(topic, question_type, difficulty_level, num_questions)
                    
                    if questions_content:
                        # Create markdown content with header
                        markdown_content = f"""# Interview Questions: {topic}

**Type:** {question_type}  
**Difficulty:** {difficulty_level}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Questions:** {num_questions}

---

{questions_content}
"""
                        
                        # Save to file
                        file_path = save_to_markdown(markdown_content, filename)
                        
                        if file_path:
                            st.success(f"✅ Questions generated successfully!")
                            st.info(f"📁 File saved as: {file_path}")
                            
                            # Show preview
                            with st.expander("👀 Preview Generated Questions", expanded=False):
                                st.markdown(questions_content)
                            
                            # Download button
                            with open(file_path, 'r', encoding='utf-8') as f:
                                file_content = f.read()
                            
                            st.download_button(
                                label="⬇️ Download Markdown File",
                                data=file_content,
                                file_name=filename if filename.endswith('.md') else f"{filename}.md",
                                mime="text/markdown"
                            )
    else:
        st.error("Cannot proceed without Gemini API key")
        st.info("Please create a .env file with your GEMINI_API_KEY")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center;">
            <small>Interview Questions Generator | Powered by Google Gemini AI</small>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()