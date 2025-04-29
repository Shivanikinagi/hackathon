import json
import re
import speech_recognition as sr
from datetime import datetime
from time import sleep
from pathlib import Path

class ProfileCreator:
    def __init__(self):
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Optimize recognition settings
        self.recognizer.energy_threshold = 3000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # Profile structure
        self.profile = {
            'name': None,
            'age': None,
            'email': None,
            'phone': None,
            'occupation': None,
            'skills': [],
            'education': None,
            'location': None,
            'created_at': None
        }
        
        # Questions and their validation types
        self.questions = [
            ('name', "What is your full name?", 'text'),
            ('age', "What is your age?", 'number'),
            ('email', "What is your email address?", 'email'),
            ('phone', "What is your phone number?", 'phone'),
            ('occupation', "What is your current occupation?", 'text'),
            ('skills', "What are your skills? (separate with and)", 'list'),
            ('education', "What is your highest education level?", 'text'),
            ('location', "Where are you located?", 'text'),
        ]

    def _validate_input(self, field_type, value):
        """Validate user input based on field type."""
        if not value or not value.strip():
            return False
            
        value = value.strip()
        
        validators = {
            'text': lambda x: len(x) >= 2,
            'number': lambda x: x.isdigit() and 0 <= int(x) <= 99,
            'email': lambda x: bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', x)),
            'phone': lambda x: bool(re.match(r'^\d{10}$', x.replace('-', '').replace(' ', ''))),  # Only 10 digits
            'list': lambda x: all(len(item.strip()) > 0 for item in x.split(','))
        }
        
        return validators.get(field_type, lambda x: True)(value)

    def get_voice_input(self, prompt, retries=3):
        """Get and process voice input with smart text processing."""
        for attempt in range(retries):
            print(f"\n🎤 {prompt} (Attempt {attempt + 1}/{retries})")
            with self.microphone as source:
                try:
                    print("Adjusting for ambient noise...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    
                    print("🎙️ Listening..")
                    print("\a")
                    sleep(0.5)
                    
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=5)
                    result = self.recognizer.recognize_google(audio, language='en-US')
                    
                    # Smart text processing based on field type
                    if "age" in prompt.lower():
                        result = result.lower()
                        # Extract numbers from speech
                        nums = ''.join(char for char in result if char.isdigit())
                        if nums:
                            result = nums
                    
                    elif "email" in prompt.lower():
                        result = result.lower()
                        # Clean email formatting
                        result = result.replace('the rate', '')
                        result = result.replace(' at ', '@')
                        result = result.replace('at rate', '@')
                        result = result.replace(' dot ', '.')
                        result = result.replace('dot', '.')
                        result = ''.join(result.split())
                    
                    elif "skills" in prompt.lower():
                        result = result.lower()
                        # Convert speech separators to commas
                        result = result.replace(' and ', ', ')
                        result = result.replace(' comma ', ', ')
                        # Clean up skill list
                        result = ', '.join(item.strip() for item in result.split(','))
                    
                    print(f"👂 Recognized: '{result}'")
                    if input("Is this correct? (y/n): ").lower().startswith('y'):
                        return result
                        
                except sr.WaitTimeoutError:
                    print("⚠️ No speech detected. Please speak louder.")
                except sr.UnknownValueError:
                    print("⚠️ Could not understand. Please speak clearly.")
                except sr.RequestError as e:
                    print(f"⚠️ Service error: {e}")
                    return self.get_text_input(prompt)
                    
        print("\n⌨️ Switching to text input...")
        return self.get_text_input(prompt)

    def get_text_input(self, prompt):
        """Get text input with clear formatting."""
        return input(f"\n⌨️ {prompt}\n> ").strip()

    def create_profile(self):
        """Main profile creation workflow."""
        print("\n🌟 Profile Creation Wizard 🌟")
        print("=" * 50)
        
        use_voice = input("\nUse voice input? (y/n): ").lower().startswith('y')
        
        for field, question, field_type in self.questions:
            while True:
                try:
                    answer = self.get_voice_input(question) if use_voice else self.get_text_input(question)
                    
                    if self._validate_input(field_type, answer):
                        if field == 'skills':
                            self.profile[field] = [s.strip() for s in answer.split(',')]
                        elif field == 'age':
                            self.profile[field] = int(answer)
                        else:
                            self.profile[field] = answer
                        break
                    print(f"❌ Invalid {field} format. Please try again.")
                except Exception as e:
                    print(f"❌ Error: {str(e)}. Please try again.")
        
        self.profile['created_at'] = datetime.now().isoformat()
        self.save_profile()
        self.display_profile()

    def save_profile(self, filename="user_profile.json"):
        """Save profile to JSON with proper formatting."""
        output_dir = Path("profiles")
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.profile, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Profile saved to {filepath}")

    def display_profile(self):
        """Display formatted profile summary."""
        print("\n📋 Profile Summary:")
        print("=" * 50)
        for field, value in self.profile.items():
            if field != 'created_at':
                print(f"{field.title()}: {value}")
        print("=" * 50)

def main():
    """Application entry point with error handling."""
    try:
        creator = ProfileCreator()
        creator.create_profile()
    except KeyboardInterrupt:
        print("\n\n⚠️ Profile creation cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()