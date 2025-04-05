# Import the json module for handling JSON data (parsing and serializing)
# json is a file format 
import json
# Import os module for operating system related functionality
import os
# Import Flask and related components from the flask module
from flask import Flask, request, jsonify, render_template, send_from_directory
# Import requests library for making HTTP requests to the OpenAI API
import requests
# Import CORS from flask_cors to enable Cross-Origin Resource Sharing
from flask_cors import CORS

# Create a new Flask application instance
app = Flask(__name__)
# Enable CORS for all routes in the application to allow cross-origin requests from the frontend
CORS(app)  # Enable CORS for all routes

# Store the OpenAI API key as a constant 
OPENAI_API_KEY = "HELOOOOsABCDk-ABCDproj-XK_7fB7izf1Tyi8q-ABCDJBG7SQo8BHOFn7ABCD-Qmla96wVCqlC6m41jzrshpqA0jGZ_ee2Q3kmBDtABCDS06T3BlbABCDkFJvaQYJT01cFbmHplSHltABCDOwiaG-xzkAIBkIIG_ABCD46y70UwalsfsIoKvzUdayPyHZq04jbrEABCDiWzY4A"

# Define a class to handle quiz generation using OpenAI API
class OpenAIQuizGenerator:
    # Constructor method that initializes the class with an optional API key
    def __init__(self, api_key=None):
        # Store the API key as an instance variable
        self.api_key = api_key
    
    # Method to generate a quiz on a specific topic with a specified number of questions
    def generate_quiz(self, topic, num_questions=5):

        # Create the system prompt that sets the AI's role as a quiz creator
        system_prompt = ("You are an expert quiz creator. Create well-formed, educational quiz questions "
                         "that test knowledge but are also interesting and engaging.")
        
        # Create the user prompt with detailed instructions for quiz format and structure
        user_prompt = f"""Generate a multiple-choice quiz with {num_questions} questions about {topic}.
        For each question:
        - Make the question clear and concise
        - Provide 4 options (labeled A, B, C, D)
        - Make sure exactly one option is correct
        - Make the distractors plausible but clearly incorrect
        - Indicate which option is correct
        
        Format your response as valid JSON following this exact structure:
        {{
            "title": "Quiz title related to the topic",
            "questions": [
                {{
                    "question": "Question text",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_index": 0  # 0-based index of the correct answer
                }},
                # More questions...
            ]
        }}
        
        Ensure your response can be parsed by Python's json.loads() function.
        """
        
        # Call the private method to make the actual API call to OpenAI
        return self._call_openai_api(system_prompt, user_prompt)
    
    # Private method to handle the API call to OpenAI
    def _call_openai_api(self, system_prompt, user_prompt):
        """Make API call to OpenAI"""
        # Set up the request headers with content type and authorization
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Prepare the request data for the OpenAI API
        data = {
            "model": "gpt-3.5-turbo",  # Specify which OpenAI model to use
            "messages": [
                {"role": "system", "content": system_prompt},  # Set the AI's role
                {"role": "user", "content": user_prompt}       # Provide the user instructions
            ],
            "temperature": 0.7  # Set the creativity level (0.7 is balanced)
        }
        
        # Try to make the API call and handle any errors
        try:
            # Send a POST request to the OpenAI API
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Extract the generated content from the response
                content = response.json()["choices"][0]["message"]["content"]
                # Parse the JSON content and return it
                return self._parse_quiz_json(content)
            else:
                # Create an error message if the request failed
                error_message = f"API Error: {response.status_code} - {response.text}"
                # Print the error for debugging
                print(error_message)
                # Return an error object
                return {"error": error_message}
                
        # Catch any exceptions that occur during the API call
        except Exception as e:
            # Print the error for debugging
            print(f"Error calling OpenAI API: {str(e)}")
            # Return an error object
            return {"error": str(e)}
    
    # Private method to parse and extract JSON from the AI response
    def _parse_quiz_json(self, content):
        """
        Extract and parse JSON from AI response
        This demonstrates the text parsing concepts from NLP output
        """
        # Try to parse the JSON, handling different possible formats
        try:
            # Check if the response contains a JSON code block with language specification
            if "```json" in content:
                # Extract content between ```json and ```
                json_str = content.split("```json")[1].split("```")[0].strip()
            # Check if the response contains a generic code block
            elif "```" in content:
                # Extract content between ``` and ```
                json_str = content.split("```")[1].strip()
            else:
                # Assume the entire response is JSON
                json_str = content
            
            # Parse the JSON string into a Python dictionary
            quiz_data = json.loads(json_str)
            # Return the parsed quiz data
            return quiz_data
            
        # Handle any errors that occur during parsing
        except Exception as e:
            # Print the error for debugging
            print(f"Error parsing quiz JSON: {str(e)}")
            # Print the raw content for debugging
            print(f"Raw content: {content}")
            # Return an error object
            return {"error": "Failed to parse AI response as JSON. Check the logs for details."}


# Define a Flask route for the quiz generation API endpoint
@app.route('/api/generate_quiz', methods=['POST'])
def generate_quiz():
    # Extract JSON data from the incoming request
    data = request.json
    # Get the 'topic' from the request data
    topic = data.get('topic')
    # Get the 'num_questions' from the request data, default to 5 if not provided
    num_questions = int(data.get('num_questions', 5))
    
    # Check if a topic was provided
    if not topic:
        # Return an error if no topic was provided
        return jsonify({"error": "Topic is required"}), 400
    
    # Create an instance of the quiz generator with the API key
    quiz_generator = OpenAIQuizGenerator(OPENAI_API_KEY)
    # Generate a quiz with the specified topic and number of questions
    result = quiz_generator.generate_quiz(topic, num_questions)
    
    # Return the quiz data as a JSON response
    return jsonify(result)

# Check if this file is being run directly (not imported)
if __name__ == '__main__':
    # Start the Flask development server in debug mode
    app.run(debug=True)
