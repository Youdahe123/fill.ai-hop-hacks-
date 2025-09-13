#!/usr/bin/env python3
"""
Human-like conversation system for Fill.ai
Makes the AI feel more natural, friendly, and engaging
"""
import random
import time

class HumanConversationAI:
    def __init__(self):
        self.user_name = None
        self.field_count = 0
        self.total_fields = 0
        self.jokes_told = 0
        self.encouragement_given = 0
        
        # Personality traits
        self.personalities = [
            "enthusiastic", "friendly", "professional", "casual", "encouraging"
        ]
        self.current_personality = random.choice(self.personalities)
        
        # Jokes for different field types
        self.field_jokes = {
            'name': [
                "I promise I won't judge if you have a really cool middle name! 😄",
                "Don't worry, I'm not going to stalk you on social media... much! 😉",
                "I hope your name isn't 'John Doe' - that would be too easy! 😂"
            ],
            'email': [
                "Please tell me it's not 'notspam@definitelynotspam.com'! 📧",
                "I hope you have a better email than my first one: 'coolguy123@aol.com'! 😅",
                "Email addresses are like fingerprints - unique and sometimes embarrassing! 📬"
            ],
            'phone': [
                "I promise I won't call you at 3 AM asking about your car's extended warranty! 📞",
                "Please don't give me 867-5309... that's Jenny's number! 🎵",
                "I hope your phone number isn't just 123-456-7890! 😄"
            ],
            'address': [
                "I promise I won't show up unannounced for dinner! 🏠",
                "Please don't give me 123 Main Street - that's where everyone lives! 😂",
                "I hope you don't live at 1600 Pennsylvania Avenue - that's the White House! 🏛️"
            ],
            'job': [
                "I hope you're not a professional couch potato! 🛋️",
                "Please don't say 'unemployed' - I'll feel bad! 😅",
                "I hope your job title isn't 'Supreme Overlord of the Universe'! 👑"
            ],
            'company': [
                "I hope you don't work for 'Evil Corp' - that sounds suspicious! 😈",
                "Please don't say 'Mom and Dad's Basement Inc.' - I'll laugh! 😂",
                "I hope your company isn't called 'Definitely Not a Pyramid Scheme'! 📈"
            ]
        }
        
        # Encouraging phrases
        self.encouragement = [
            "You're doing great!",
            "Almost there!",
            "You're a form-filling champion!",
            "This is going so smoothly!",
            "You're making this look easy!",
            "Fantastic work!",
            "You're on fire!",
            "This is going perfectly!"
        ]
        
        # Greeting variations
        self.greetings = [
            "Hey there! I'm Fill.ai, your friendly form-filling assistant!",
            "Hello! I'm Fill.ai, and I'm here to make this form super easy for you!",
            "Hi! I'm Fill.ai, your personal form-filling buddy!",
            "Hey! I'm Fill.ai, and I'm excited to help you fill out this form!",
            "Hello there! I'm Fill.ai, and I promise this will be fun!"
        ]
        
        # Field-specific responses
        self.field_responses = {
            'first_name': [
                "Nice to meet you, {name}! That's a great name!",
                "Pleasure to meet you, {name}! I love that name!",
                "Hey {name}! That's such a cool name!",
                "Hi {name}! I'm so glad to meet you!",
                "Hello {name}! That's a beautiful name!"
            ],
            'last_name': [
                "Nice to meet you, {name}! I love that last name!",
                "Pleasure to meet you, {name}! That's a great surname!",
                "Hey {name}! I love that family name!",
                "Hi {name}! That's such a cool last name!",
                "Hello {name}! I'm so glad to meet you!"
            ],
            'email': [
                "Perfect! I'll make sure to send you a copy of this form at {email}!",
                "Great! I'll send you the completed form at {email}!",
                "Awesome! I'll email you the finished form at {email}!",
                "Perfect! I'll make sure you get a copy at {email}!",
                "Great! I'll send the completed form to {email}!"
            ],
            'phone': [
                "Perfect! I'll call you if I have any questions about {phone}!",
                "Great! I'll text you the completed form to {phone}!",
                "Awesome! I'll make sure to call you at {phone} if needed!",
                "Perfect! I'll send you updates at {phone}!",
                "Great! I'll contact you at {phone} if I need anything!"
            ]
        }
    
    def get_greeting(self):
        """Get a random greeting"""
        return random.choice(self.greetings)
    
    def get_field_question(self, field, field_type):
        """Get a human-like question for a field"""
        label = field.get('label', '').lower()
        field_type = field_type.lower()
        
        # Base questions with personality
        questions = {
            'first_name': [
                "What's your first name? I'm excited to meet you!",
                "Could you tell me your first name? I'd love to know!",
                "What should I call you? I mean, what's your first name?",
                "I'd love to know your first name! What is it?",
                "What's your first name? I promise I'll remember it!"
            ],
            'last_name': [
                "And what's your last name? I'm curious about your family name!",
                "Could you tell me your last name? I'd love to know!",
                "What's your surname? I'm interested in your family name!",
                "And your last name? I'd love to know!",
                "What's your family name? I'm curious!"
            ],
            'email': [
                "What's your email address? I'll send you a copy of this form!",
                "Could you give me your email? I'll make sure you get a copy!",
                "What's your email address? I'll send you the completed form!",
                "Could you tell me your email? I'll send you a copy!",
                "What's your email? I'll make sure you get this form!"
            ],
            'phone': [
                "What's your phone number? I'll call you if I have questions!",
                "Could you give me your phone number? I'll text you updates!",
                "What's your phone? I'll contact you if needed!",
                "Could you tell me your phone number? I'll keep you updated!",
                "What's your phone? I'll make sure to reach out if needed!"
            ],
            'address': [
                "What's your address? I promise I won't show up unannounced!",
                "Could you give me your address? I'll keep it safe!",
                "What's your home address? I'll make sure it's secure!",
                "Could you tell me your address? I'll protect your privacy!",
                "What's your address? I'll keep it confidential!"
            ],
            'city': [
                "What city do you live in? I'm curious about your hometown!",
                "Could you tell me your city? I'd love to know!",
                "What city are you in? I'm interested in your location!",
                "Could you give me your city? I'd love to know!",
                "What's your city? I'm curious about where you live!"
            ],
            'state': [
                "What state are you in? I'm curious about your location!",
                "Could you tell me your state? I'd love to know!",
                "What state do you live in? I'm interested!",
                "Could you give me your state? I'd love to know!",
                "What's your state? I'm curious about where you are!"
            ],
            'zip_code': [
                "What's your zip code? I need it for the address!",
                "Could you give me your zip code? I need it!",
                "What's your postal code? I need it for the address!",
                "Could you tell me your zip code? I need it!",
                "What's your zip? I need it for the address!"
            ],
            'company_name': [
                "What company do you work for? I'm curious about your job!",
                "Could you tell me your company name? I'd love to know!",
                "What's your company? I'm interested in your work!",
                "Could you give me your company name? I'd love to know!",
                "What company are you with? I'm curious!"
            ],
            'job_title': [
                "What's your job title? I'm curious about what you do!",
                "Could you tell me your job title? I'd love to know!",
                "What do you do for work? I'm interested!",
                "Could you give me your job title? I'd love to know!",
                "What's your position? I'm curious about your work!"
            ],
            'start_date': [
                "When did you start this job? I'm curious about your career!",
                "Could you tell me your start date? I'd love to know!",
                "When did you begin this position? I'm interested!",
                "Could you give me your start date? I'd love to know!",
                "What's your start date? I'm curious about your career!"
            ],
            'reason_for_leaving': [
                "Why are you leaving this job? I'm curious about your career move!",
                "Could you tell me why you're leaving? I'd love to know!",
                "What's your reason for leaving? I'm interested!",
                "Could you give me your reason for leaving? I'd love to know!",
                "Why are you moving on? I'm curious about your career!"
            ]
        }
        
        # Get appropriate questions
        if label in questions:
            return random.choice(questions[label])
        elif field_type in questions:
            return random.choice(questions[field_type])
        else:
            return f"What's your {label.replace('_', ' ')}? I'd love to know!"
    
    def get_field_response(self, field, value):
        """Get a human-like response after getting a field value"""
        label = field.get('label', '').lower()
        field_type = field.get('type', '').lower()
        
        # Store user name for personalization
        if 'first_name' in label or 'name' in label:
            self.user_name = value
        
        # Get appropriate response
        if label in self.field_responses:
            response = random.choice(self.field_responses[label])
            if '{name}' in response:
                response = response.format(name=value)
            elif '{email}' in response:
                response = response.format(email=value)
            elif '{phone}' in response:
                response = response.format(phone=value)
            return response
        else:
            return f"Perfect! I got your {label.replace('_', ' ')}: {value}"
    
    def should_tell_joke(self):
        """Determine if we should tell a joke"""
        if self.jokes_told >= 3:  # Max 3 jokes per session
            return False
        return random.random() < 0.3  # 30% chance
    
    def get_joke(self, field_type):
        """Get a joke for a specific field type"""
        if field_type in self.field_jokes:
            return random.choice(self.field_jokes[field_type])
        else:
            return "I'm running out of jokes! 😄"
    
    def should_encourage(self):
        """Determine if we should give encouragement"""
        if self.encouragement_given >= 5:  # Max 5 encouragements per session
            return False
        return random.random() < 0.4  # 40% chance
    
    def get_encouragement(self):
        """Get an encouraging phrase"""
        return random.choice(self.encouragement)
    
    def get_progress_comment(self):
        """Get a comment about progress"""
        progress = self.field_count / self.total_fields if self.total_fields > 0 else 0
        
        if progress < 0.25:
            return "We're just getting started! ��"
        elif progress < 0.5:
            return "We're making great progress! 📈"
        elif progress < 0.75:
            return "We're more than halfway done! 🎯"
        elif progress < 1.0:
            return "We're almost there! 🏁"
        else:
            return "All done! You're amazing! 🎉"
    
    def get_completion_message(self):
        """Get a completion message"""
        messages = [
            f"Fantastic work, {self.user_name if self.user_name else 'friend'}! You've filled out all the fields!",
            f"Amazing job, {self.user_name if self.user_name else 'friend'}! This form is complete!",
            f"You're incredible, {self.user_name if self.user_name else 'friend'}! All done!",
            f"Outstanding work, {self.user_name if self.user_name else 'friend'}! Form complete!",
            f"You're a form-filling champion, {self.user_name if self.user_name else 'friend'}! All done!"
        ]
        return random.choice(messages)
