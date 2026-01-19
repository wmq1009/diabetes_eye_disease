import requests
import json
import base64

class OllamaClient:
    def __init__(self, base_url='http://localhost:11434', model='llava'):
        self.base_url = base_url
        self.model = model
        self.api_url = f'{base_url}/api/generate'
    
    def check_connection(self):
        try:
            response = requests.get(f'{self.base_url}/api/tags', timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def analyze_image(self, image_path, prompt):
        try:
            with open(image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            payload = {
                'model': self.model,
                'prompt': prompt,
                'images': [image_data],
                'stream': False
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                return f'Error: {response.status_code} - {response.text}'
                
        except Exception as e:
            return f'Error: {str(e)}'
    
    def chat_with_image(self, image_path, conversation_history):
        try:
            with open(image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            messages = []
            for msg in conversation_history:
                messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
            
            payload = {
                'model': self.model,
                'messages': messages,
                'images': [image_data],
                'stream': False
            }
            
            response = requests.post(
                f'{self.base_url}/api/chat',
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('message', {}).get('content', '')
            else:
                return f'Error: {response.status_code} - {response.text}'
                
        except Exception as e:
            return f'Error: {str(e)}'
    
    def generate_text(self, prompt):
        try:
            payload = {
                'model': self.model,
                'prompt': prompt,
                'stream': False
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                return f'Error: {response.status_code} - {response.text}'
                
        except Exception as e:
            return f'Error: {str(e)}'
    
    def get_available_models(self):
        try:
            response = requests.get(f'{self.base_url}/api/tags', timeout=5)
            if response.status_code == 200:
                result = response.json()
                return result.get('models', [])
            return []
        except Exception:
            return []
