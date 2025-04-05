import json
import os
from flask import Flask, request, jsonify, render_template, send_from_directory
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class OpenAIQuizGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key
    
    def generate_quiz(self, topic, num_questions=5):
        """
        Generate a quiz on the specified topic using OpenAI
        """
        # Construct the prompt that demonstrates proper prompt engineering
        system_prompt = ("You are an expert quiz creator. Create well-formed, educational quiz questions "
                         "that test knowledge but are also interesting and engaging.")
        
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
        
        # Make the API call to OpenAI
        return self._call_openai_api(system_prompt, user_prompt)
    
    def _call_openai_api(self, system_prompt, user_prompt):
        """Make API call to OpenAI"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                # Parse the JSON content from the response
                return self._parse_quiz_json(content)
            else:
                error_message = f"API Error: {response.status_code} - {response.text}"
                print(error_message)
                return {"error": error_message}
                
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            return {"error": str(e)}
    
    def _parse_quiz_json(self, content):
        """
        Extract and parse JSON from AI response
        This demonstrates the text parsing concepts from NLP output
        """
        try:
            # Handle potential markdown code blocks in the response
            if "```json" in content:
                # Extract content between ```json and ```
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                # Extract content between ``` and ```
                json_str = content.split("```")[1].strip()
            else:
                # Assume the entire response is JSON
                json_str = content
            
            # Parse the JSON
            quiz_data = json.loads(json_str)
            return quiz_data
            
        except Exception as e:
            print(f"Error parsing quiz JSON: {str(e)}")
            print(f"Raw content: {content}")
            return {"error": "Failed to parse AI response as JSON. Check the logs for details."}


# API endpoint to generate a quiz
@app.route('/api/generate_quiz', methods=['POST'])
def generate_quiz():
    data = request.json
    api_key = data.get('api_key')
    topic = data.get('topic')
    num_questions = int(data.get('num_questions', 5))
    
    if not api_key or not topic:
        return jsonify({"error": "API key and topic are required"}), 400
    
    quiz_generator = OpenAIQuizGenerator(api_key)
    result = quiz_generator.generate_quiz(topic, num_questions)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)