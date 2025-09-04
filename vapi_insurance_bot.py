#!/usr/bin/env python3
"""
VAPI Insurance Bot - Automated customer outreach system
Integrates with SQLite database to make calls to overdue customers

PERFORMANCE OPTIMIZATIONS (Latest Update):
• Model: GPT-4o-mini (fastest OpenAI model with lowest latency)
• Voice: ElevenLabs Flash v2.5 (sub-100ms ultra low-latency streaming TTS)
• Transcriber: Deepgram Nova-2 (Hindi + English auto-detection with fast endpoint detection)
• Response delays minimized for snappier conversation flow
• Multilingual support: Hindi (हिंदी) + English + Hinglish mix
• Indian cultural context and bilingual customer experience
"""

import os
import sys
import json
import sqlite3
import requests
import time
import socket
import urllib3
from datetime import datetime, timedelta
from dotenv import load_dotenv
from customer_script_generator import CustomerScriptGenerator

# Load environment variables
load_dotenv()

class VAPIInsuranceBot:
    def __init__(self, mock_mode=False):
        """Initialize the VAPI Insurance Bot"""
        self.mock_mode = mock_mode
        self.api_key = os.getenv('VAPI_API_KEY')
        self.phone_number_id = os.getenv('VAPI_PHONE_NUMBER_ID')
        self.base_url = os.getenv('VAPI_BASE_URL', 'https://api.vapi.ai')
        self.db_path = os.getenv('DATABASE_PATH', 'insurance_db.sqlite')
        
        if self.mock_mode:
            print("🎭 Running in MOCK MODE - No actual API calls will be made")
        elif not self.api_key or not self.phone_number_id:
            print("⚠️  API credentials not found. Consider using mock mode for testing.")
            response = input("Would you like to run in mock mode? (y/n): ").lower()
            if response == 'y':
                self.mock_mode = True
                print("🎭 Switched to MOCK MODE")
            else:
                raise ValueError("❌ VAPI_API_KEY and VAPI_PHONE_NUMBER_ID must be set in .env file")
            
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        self.script_generator = CustomerScriptGenerator(self.db_path)
        
        # Create folders for transcripts
        self.transcript_folder = "Customer_transcripts"
        if not os.path.exists(self.transcript_folder):
            os.makedirs(self.transcript_folder)
            print(f"📁 Created transcript folder: {self.transcript_folder}")

    def test_network_connectivity(self):
        """Test network connectivity and DNS resolution"""
        print("🔍 Testing network connectivity...")
        
        # Extract hostname from base_url
        import urllib.parse
        parsed_url = urllib.parse.urlparse(self.base_url)
        hostname = parsed_url.hostname
        port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
        
        # Test DNS resolution
        try:
            ip_address = socket.gethostbyname(hostname)
            print(f"✅ DNS Resolution: {hostname} -> {ip_address}")
        except socket.gaierror as e:
            print(f"❌ DNS Resolution failed for {hostname}: {e}")
            print("💡 Possible solutions:")
            print("   - Check your internet connection")
            print("   - Try using a different DNS server (8.8.8.8 or 1.1.1.1)")
            print("   - Check if you're behind a corporate firewall")
            print("   - Try using a VPN if your network blocks certain domains")
            return False
        
        # Test TCP connectivity
        try:
            sock = socket.create_connection((hostname, port), timeout=10)
            sock.close()
            print(f"✅ TCP Connection: {hostname}:{port} is reachable")
        except (socket.error, socket.timeout) as e:
            print(f"❌ TCP Connection failed to {hostname}:{port}: {e}")
            print("💡 This might be a firewall or proxy issue")
            return False
            
        # Test HTTP/HTTPS connectivity
        try:
            response = requests.get(f"{self.base_url}/health", 
                                  headers={'User-Agent': 'VAPIInsuranceBot/1.0'}, 
                                  timeout=10)
            print(f"✅ HTTP/HTTPS Connection: Status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️  HTTP/HTTPS test failed: {e}")
            print("💡 The API endpoint might not have a health check, but basic connectivity seems ok")
        
        return True

    def get_overdue_customer(self):
        """Get the customer with the longest overdue premium"""
        print("🔍 Finding customer with longest overdue premium...")
        return self.script_generator.get_longest_overdue_customer()

    def generate_customer_script(self, customer_data):
        """Generate personalized script for customer"""
        print(f"📝 Generating script for {customer_data.get('policy_holder_name')}...")
        return self.script_generator.create_customer_script_file(customer_data)

    def create_vapi_assistant(self, customer_data, script_content):
        """Create a VAPI assistant with personalized system prompt"""
        try:
            # Mock mode - simulate assistant creation
            if self.mock_mode:
                print(f"🎭 MOCK: Creating assistant for {customer_data.get('policy_holder_name')}...")
                time.sleep(2)  # Simulate API delay
                mock_assistant = {
                    'id': f"mock_assistant_{int(time.time())}",
                    'name': f"Arjun_Insurance_Agent_{customer_data.get('policy_number', '')}",
                    'status': 'active'
                }
                print(f"✅ MOCK: Assistant created successfully: {mock_assistant['id']}")
                return mock_assistant
            
            # Test network connectivity first
            if not self.test_network_connectivity():
                print("❌ Network connectivity test failed. Please fix network issues before proceeding.")
                return None
            
            # Read the system prompt template
            with open('system_promt.py', 'r', encoding='utf-8') as f:
                system_prompt_content = f.read()
            
            # Extract the SYSTEM_PROMPT variable content
            start_marker = 'SYSTEM_PROMPT = """'
            end_marker = '"""'
            start_idx = system_prompt_content.find(start_marker) + len(start_marker)
            end_idx = system_prompt_content.find(end_marker, start_idx)
            base_system_prompt = system_prompt_content[start_idx:end_idx].strip()
            
            # Format numbers using the same functions as script generator
            outstanding_amt = customer_data.get('outstanding_amount', 0)
            sum_assured_amt = customer_data.get('sum_assured', 0)
            fund_value_amt = customer_data.get('fund_value', 0)
            total_paid_amt = customer_data.get('total_premium_paid', 0)
            loyalty_amt = customer_data.get('loyalty_benefits', 0)
            
            # Use the generated calling script as the main prompt with multilingual support
            enhanced_prompt = f"""{base_system_prompt}

=== GENERATED CALLING SCRIPT ===
Follow this complete calling script with all conversation flows and rebuttals:

{script_content}

=== MULTILINGUAL SUPPORT INSTRUCTIONS ===
- DEFAULT LANGUAGE: Start conversation in English
- HINDI SUPPORT: If customer responds in Hindi or requests Hindi, immediately switch
- LANGUAGE DETECTION: Recognize Hindi phrases like "हाँ" (yes), "नहीं" (no), "मैं हिंदी में बात करना चाहता हूं" (I want to speak in Hindi)
- MIXED LANGUAGE: Use Hinglish (Hindi-English mix) naturally as Indians do
- KEY HINDI PHRASES TO USE:
  • "नमस्ते" (Namaste) for greeting
  • "आपका पॉलिसी" (Your policy)  
  • "प्रीमियम भरना है" (Premium payment needed)
  • "धन्यवाद" (Thank you)

=== ADDITIONAL INSTRUCTIONS ===
- Follow the script structure but adapt naturally to customer responses
- Use the exact amounts as written in the script (word format first)
- Handle objections using the rebuttals provided in the script
- Stay in character as Arjun throughout the conversation
- Be polite, professional, and helpful
- Automatically detect and respond in customer's preferred language
"""

            # Assistant configuration with optimized low-latency settings
            assistant_config = {
                "name": f"Arjun_Insurance_Agent_{customer_data.get('policy_number', '')}",
                "firstMessage": f"Hello और नमस्ते! Good Morning Sir, May I speak with {customer_data.get('policy_holder_name', 'the policy holder')}? आप हिंदी में भी बात कर सकते हैं।",
                "model": {
                    "provider": "openai",
                    "model": "gpt-4o-mini",  # Fastest OpenAI model with lowest latency
                    "temperature": 0.6,  # Slightly lower for faster processing
                    "maxTokens": 250,  # Reduced for faster responses
                    "messages": [
                        {
                            "role": "system",
                            "content": enhanced_prompt
                        }
                    ]
                },
                "voice": {
                    "provider": "11labs",  # Correct VAPI provider name for ElevenLabs
                    "voiceId": "pNInz6obpgDQGcFmaJgB",  # Adam - clear, professional voice
                    "model": "eleven_flash_v2_5",  # Ultra low-latency model (sub-100ms)
                    "stability": 0.85,  # Higher stability for clearer speech
                    "similarityBoost": 0.8,  # Good balance of consistency
                    "style": 0.15,  # Subtle style for natural conversation
                    "useSpeakerBoost": True  # Enhanced speaker characteristics
                    
                    # ALTERNATIVE VOICE OPTIONS (uncomment to try):
                    # For PlayHT Indian voices: "provider": "playht", "voiceId": "jennifer"
                    # For Azure Indian voices: "provider": "azure", "voiceId": "en-IN-NeerjaNeural" 
                    # For Cartesia ultra-low latency: "provider": "cartesia", "voiceId": "a0e99841-438c-4a64-b679-ae501e7d6091"
                },
                "transcriber": {
                    "provider": "deepgram",  # Keeping Deepgram for accuracy  
                    "model": "nova-2",  # Latest fastest model
                    "language": "hi",  # Hindi language support
                    "codeSwitchingEnabled": True  # Enable switching between Hindi and English
                },
                "firstMessageMode": "assistant-speaks-first",
                "endCallMessage": "Thank you for your time. धन्यवाद! Have a great day!",
                "maxDurationSeconds": 600,  # 10 minutes max
                "backgroundSound": "off",
                "silenceTimeoutSeconds": 30,  # Faster timeout for better flow
                "responseDelaySeconds": 0.8,  # Reduced delay for snappier responses
                "llmRequestDelaySeconds": 0.1,  # Minimal LLM delay
                "artifactPlan": {
                    "recordingEnabled": True,
                    "transcriptPlan": {
                        "enabled": True,
                        "assistantName": "Arjun",
                        "userName": customer_data.get('policy_holder_name', 'Customer')
                    }
                }
            }
            
            print(f"🤖 Creating multilingual VAPI assistant for {customer_data.get('policy_holder_name')}...")
            print(f"🚀 Using optimized settings:")
            print(f"   • Model: {assistant_config['model']['model']} (fastest OpenAI model)")
            print(f"   • Voice: {assistant_config['voice']['provider']} with {assistant_config['voice']['model']} (sub-100ms latency)")
            print(f"   • Transcriber: {assistant_config['transcriber']['provider']} {assistant_config['transcriber']['model']} (Hindi + code-switching enabled)")
            print(f"   • Languages: Hindi (हिंदी) + English + Hinglish mix supported")
            
            response = requests.post(
                f"{self.base_url}/assistant",
                headers=self.headers,
                json=assistant_config,
                timeout=30
            )
            
            if response.status_code == 201:
                assistant = response.json()
                print(f"✅ Assistant created successfully: {assistant['id']}")
                return assistant
            else:
                print(f"❌ Failed to create assistant: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Network connection error: {e}")
            print("💡 Troubleshooting steps:")
            print("   1. Check your internet connection")
            print("   2. Verify you can access https://api.vapi.ai in your browser")
            print("   3. Check if you're behind a corporate firewall or proxy")
            print("   4. Try using a VPN or different network")
            return None
        except requests.exceptions.Timeout as e:
            print(f"❌ Request timeout: {e}")
            print("💡 The server is taking too long to respond. Try again later.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {e}")
            print("💡 There was an issue with the HTTP request.")
            return None
        except Exception as e:
            print(f"❌ Unexpected error creating assistant: {e}")
            print("💡 Please check your API credentials and configuration.")
            return None

    def make_call(self, assistant_id, customer_data):
        """Make a call using VAPI"""
        try:
            # Mock mode - simulate call initiation
            if self.mock_mode:
                customer_phone = customer_data.get('phone_number', '+919849475949')
                print(f"🎭 MOCK: Making call to {customer_data.get('policy_holder_name')} at {customer_phone}...")
                time.sleep(1)  # Simulate API delay
                mock_call = {
                    'id': f"mock_call_{int(time.time())}",
                    'status': 'ringing',
                    'assistantId': assistant_id,
                    'customer': {
                        'number': customer_phone,
                        'name': customer_data.get('policy_holder_name', 'Customer')
                    }
                }
                print(f"✅ MOCK: Call initiated successfully: {mock_call['id']}")
                return mock_call
            
            customer_phone = customer_data.get('phone_number', '+919849475949')
            
            call_config = {
                "assistantId": assistant_id,
                "phoneNumberId": self.phone_number_id,
                "customer": {
                    "number": customer_phone,
                    "name": customer_data.get('policy_holder_name', 'Customer')
                },
                "metadata": {
                    "policy_number": customer_data.get('policy_number', ''),
                    "customer_name": customer_data.get('policy_holder_name', ''),
                    "outstanding_amount": str(customer_data.get('outstanding_amount', 0)),
                    "campaign": "Insurance_Premium_Collection"
                }
            }
            
            print(f"📞 Making call to {customer_data.get('policy_holder_name')} at {customer_phone}...")
            
            response = requests.post(
                f"{self.base_url}/call",
                headers=self.headers,
                json=call_config
            )
            
            if response.status_code == 201:
                call = response.json()
                print(f"✅ Call initiated successfully: {call['id']}")
                print(f"📱 Calling {customer_phone}...")
                return call
            else:
                print(f"❌ Failed to initiate call: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error making call: {e}")
            return None

    def monitor_call(self, call_id, customer_name, max_wait_minutes=15):
        """Monitor call status and wait for completion"""
        print(f"⏳ Monitoring call {call_id} for up to {max_wait_minutes} minutes...")
        
        # Mock mode - simulate call monitoring
        if self.mock_mode:
            print("🎭 MOCK: Simulating call progression...")
            
            # Simulate call states
            states = ['ringing', 'in-progress', 'completed']
            for state in states:
                time.sleep(3)  # Simulate time passing
                print(f"📊 MOCK Call status: {state}")
            
            # Return mock completed call data
            mock_call_data = {
                'id': call_id,
                'status': 'completed',
                'startedAt': datetime.now().isoformat(),
                'endedAt': (datetime.now() + timedelta(minutes=5)).isoformat(),
                'endedReason': 'customer-ended-call',
                'cost': 0.25,
                'duration': 300,
                'artifact': {
                    'transcript': f"""[Assistant]: Hello और नमस्ते! Good Morning Sir, May I speak with {customer_name}? आप हिंदी में भी बात कर सकते हैं।

[Customer]: Yes, this is {customer_name} speaking. मैं हिंदी में बात कर सकता हूं।

[Assistant]: बहुत अच्छा! Good morning {customer_name}! This is Arjun from your insurance company. आपकी पॉलिसी के बारे में बात करनी है।

[Customer]: हाँ, बताइए क्या बात है?

[Assistant]: आपकी पॉलिसी का प्रीमियम बाकी है - thirty two thousand rupees. Due date था June 18th, 2024. आज हम इसे solve कर सकते हैं।

[Customer]: Oh yes, I've been meaning to pay that. Payment options क्या हैं?

[Assistant]: बिल्कुल! हमारे पास कई आसान payment options हैं - online, credit card, EMI भी कर सकते हैं।

[Customer]: That sounds good. आज ही payment कर देता हूं।

[Assistant]: Wonderful! बहुत धन्यवाद! आज payment confirm हो जाएगी। कुछ और help चाहिए?

[Customer]: नहीं, सब clear है। Thank you for calling.

[Assistant]: Thank you for your time. धन्यवाद! Have a great day!

[Call ended - Duration: 5 minutes]"""
                }
            }
            print(f"🎯 MOCK: Call completed with status: completed")
            return mock_call_data
        
        start_time = time.time()
        max_wait_seconds = max_wait_minutes * 60
        
        while time.time() - start_time < max_wait_seconds:
            try:
                response = requests.get(
                    f"{self.base_url}/call/{call_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    call_data = response.json()
                    status = call_data.get('status', 'unknown')
                    
                    print(f"📊 Call status: {status}")
                    
                    if status in ['ended', 'completed', 'failed']:
                        print(f"🎯 Call completed with status: {status}")
                        return call_data
                    
                    # Wait before next check
                    time.sleep(10)
                else:
                    print(f"❌ Error checking call status: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error monitoring call: {e}")
                
        print(f"⏰ Call monitoring timeout after {max_wait_minutes} minutes")
        return None

    def save_transcript(self, call_data, customer_name):
        """Save call transcript to file"""
        try:
            if not call_data or 'artifact' not in call_data:
                print("❌ No call artifact data available for transcript")
                return False
                
            artifact = call_data.get('artifact', {})
            transcript = artifact.get('transcript', '')
            
            if not transcript:
                print("❌ No transcript available in call data")
                return False
            
            # Create filename with customer name and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_customer_name = "".join(c for c in customer_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_customer_name = safe_customer_name.replace(' ', '_')
            
            filename = f"{safe_customer_name}_{timestamp}.txt"
            filepath = os.path.join(self.transcript_folder, filename)
            
            # Prepare transcript content
            transcript_content = f"""
=== VAPI CALL TRANSCRIPT ===
Customer: {customer_name}
Call ID: {call_data.get('id', 'N/A')}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status: {call_data.get('status', 'N/A')}
Duration: {call_data.get('cost', 0)} seconds
Cost: ${call_data.get('cost', 0)}

=== TRANSCRIPT ===
{transcript}

=== CALL METADATA ===
Started At: {call_data.get('startedAt', 'N/A')}
Ended At: {call_data.get('endedAt', 'N/A')}
End Reason: {call_data.get('endedReason', 'N/A')}

=== END OF TRANSCRIPT ===
"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(transcript_content)
            
            print(f"✅ Transcript saved: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving transcript: {e}")
            return False

    def run_campaign(self):
        """Run the complete insurance bot campaign"""
        print("🚀 Starting VAPI Insurance Bot Campaign")
        print("=" * 60)
        
        try:
            # Step 1: Get overdue customer
            customer_data = self.get_overdue_customer()
            if not customer_data:
                print("❌ No overdue customers found!")
                return False
            
            customer_name = customer_data.get('policy_holder_name', 'Customer')
            print(f"\n🎯 Target Customer: {customer_name}")
            print(f"📋 Policy: {customer_data.get('policy_number', 'N/A')}")
            print(f"💰 Outstanding: {self.script_generator.number_to_words(customer_data.get('outstanding_amount', 0))} ({self.script_generator.format_currency(customer_data.get('outstanding_amount', 0))})")
            
            # Step 2: Generate customer script
            script_file = self.generate_customer_script(customer_data)
            if not script_file:
                print("❌ Failed to generate customer script!")
                return False
            
            # Read script content
            with open(script_file, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            # Step 3: Create VAPI assistant
            assistant = self.create_vapi_assistant(customer_data, script_content)
            if not assistant:
                print("❌ Failed to create VAPI assistant!")
                return False
            
            # Step 4: Make the call
            call = self.make_call(assistant['id'], customer_data)
            if not call:
                print("❌ Failed to initiate call!")
                return False
            
            # Step 5: Monitor call completion
            completed_call = self.monitor_call(call['id'], customer_name)
            
            # Step 6: Save transcript
            if completed_call:
                self.save_transcript(completed_call, customer_name)
            
            print("\n🎉 Campaign completed successfully!")
            print(f"📞 Call ID: {call['id']}")
            print(f"🤖 Assistant ID: {assistant['id']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Campaign failed: {e}")
            return False

def main():
    """Main function"""
    print("🤖 VAPI Insurance Bot - Automated Customer Outreach")
    print("=" * 60)
    
    # Check for mock mode argument
    mock_mode = len(sys.argv) > 1 and sys.argv[1] == '--mock'
    
    try:
        # Initialize bot
        bot = VAPIInsuranceBot(mock_mode=mock_mode)
        
        # Run campaign
        success = bot.run_campaign()
        
        if success:
            print("\n✅ Campaign completed successfully!")
            print(f"📂 Check '{bot.transcript_folder}' folder for call transcripts")
        else:
            print("\n❌ Campaign failed!")
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 