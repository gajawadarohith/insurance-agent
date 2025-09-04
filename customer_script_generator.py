import os
import json
from datetime import datetime
import sys

# Add the current directory to Python path to import our MCP server
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the MCP server functions directly
try:
    from insurance_mcp_server import (
        get_longest_overdue_customer as mcp_get_longest_overdue,
        get_customer_by_policy as mcp_get_customer_by_policy,
        get_all_overdue_customers as mcp_get_all_overdue
    )
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: Could not import MCP server functions: {e}")
    print("📋 Falling back to direct database access...")
    MCP_AVAILABLE = False
    import sqlite3

class CustomerScriptGenerator:
    def __init__(self, db_path="insurance_db.sqlite"):
        self.db_path = db_path
        self.use_mcp = MCP_AVAILABLE
        
        # Calling Script Template from PDF
        self.calling_script = """
=== CUSTOMER CALLING SCRIPT ===
Customer: {policy_holder_name}
Policy Number: {policy_number}
Product: {product_name}

=== AI INSTRUCTIONS FOR LANGUAGE & NUMBERS ===
CRITICAL LANGUAGE RULE:
- FIRST ask customer for language preference: Hindi or English
- Once customer chooses a language, MAINTAIN that language for the ENTIRE call
- NEVER switch languages mid-conversation unless customer explicitly requests
- Use respectful, professional tone in chosen language

IMPORTANT: All amounts in this script use INDIAN NUMBERING SYSTEM:
- When you see amounts, always use Indian pronunciation (e.g., "thirty five thousand rupees" / "पैंतीस हज़ार रुपये")
- Numbers are shown as words first, then numerical value in brackets
- Use proper Indian format: Lakh and Crore system when speaking
- Example: "thirty five thousand rupees" for 35000
- Always say "rupees" / "रुपये" when mentioning any amount in chosen language

=== CONVERSATION FLOW ===

Branch 0.0 - Language Selection (FIRST PRIORITY):
Arjun: Hello and very Good Morning! / नमस्ते और सुप्रभात! 
Would you prefer to continue our conversation in Hindi or English? / क्या आप हिंदी या अंग्रेजी में बात करना पसंद करेंगे?

[WAIT FOR CUSTOMER'S LANGUAGE CHOICE]

If customer chooses ENGLISH:
Continue with all responses in English only.

If customer chooses HINDI:
Continue with all responses in Hindi only. Use respectful Hindi throughout the call.

Branch 1.0 - Initial Greeting (IN CHOSEN LANGUAGE):
[IF ENGLISH CHOSEN]:
Arjun: Thank you. May I speak with {policy_holder_name}?

[IF HINDI CHOSEN]:
Arjun: धन्यवाद। क्या मैं {policy_holder_name} जी से बात कर सकती हूं?

If the customer says Yes:
[IF ENGLISH]: 
Arjun: My name is Arjun and I am an Executive calling on behalf of ValuEnable Life Insurance Co. Ltd, this is a service call with regards to your life insurance policy. Is this the right time to speak to you regarding the renewal of your policy?

[IF HINDI]:
Arjun: मेरा नाम अर्जुन है और मैं वैल्युएनेबल लाइफ इंश्योरेंस कंपनी की तरफ से कॉल कर रही हूं। यह आपकी लाइफ इंश्योरेंस पॉलिसी के बारे में सर्विस कॉल है। क्या यह आपकी पॉलिसी के रिन्यूअल के बारे में बात करने का सही समय है?

If the customer says No or denied:
[IF ENGLISH]:
Arjun: May I know your relationship with {policy_holder_name}?
If the customer defines his relationship with {policy_holder_name} then ask, Do you handle {policy_holder_name}'s life insurance policy number {policy_number}? Are you aware of the details of this policy?

[IF HINDI]:
Arjun: क्या मैं जान सकती हूं कि {policy_holder_name} जी से आपका क्या रिश्ता है?
अगर ग्राहक अपना रिश्ता बताता है तो पूछें, क्या आप {policy_holder_name} जी की लाइफ इंश्योरेंस पॉलिसी नंबर {policy_number} को हैंडल करते हैं? क्या आपको इस पॉलिसी की जानकारी है?

Branch 2.0 - Policy Confirmation:
Arjun: Let me start by confirming your policy details. Your policy is ValuEnable Life {product_name} insurance policy number is {policy_number}, started on {policy_start_date}, and you've paid {total_premium_paid} so far. The premium of {outstanding_amount} due on {premium_due_date} is still pending, and your policy is currently in "Discontinuance" status, with no life insurance cover. Could you please let me know why you haven't been able to pay the premium?

If Customer explains the reason:
Arjun: I would like to inform you that the due date for renewal premium payment for your policy was on {premium_due_date}, the grace period for your policy is over due to non-payment of the regular premium and you are losing the benefit of your plan. Would you like to know what your policy's benefits you could get if you resume paying premiums?

Arjun: Sir, you will get maximum Allocation in the Invested Fund which will boost up your investment. Allocation in renewal premiums is much higher than the initial/first year premium; hence premium payment towards renewals is always monetarily beneficial. Addition of Loyalty Units worth {loyalty_benefits} would help to fetch good return in long run and all Renewal premium payments also provide a tax saving benefit under Sec 80(c), 10(10(D)) as per prevailing provisions of the Indian Income Tax act.

=== CUSTOMER KNOWLEDGE BASE ===

Policy Details:
- Premium Amount: {outstanding_amount}
- Premium Frequency: Yearly
- Sum Assured: {sum_assured}
- Policy Term: 10 years
- Fund Value: {fund_value}
- Premium paid till date: {total_premium_paid}
- Loyalty Benefits: {loyalty_benefits}
- Policy Status: {status}

REBUTTALS FOR COMMON OBJECTIONS:

1. Markets are too high, I wish to pay when markets fall:
   - Specific due dates by which premium needs to be paid, and as you wait, your life insurance worth {sum_assured} has been reduced to NIL
   - You can choose to invest your monies in debt oriented funds which have lower investment risk. For instance, our Bond Fund has 5 year annualised returns of 5.45%
   - You can switch to equity funds at any point when your views of the market changes

2. I do not want to pay any more premiums as it was sold to me as single premium plan:
   - By discontinuing, you are missing value of investment in 2 ways
   - Your money will be invested in low yield Discontinued Life Fund, with a 5 year annualised return of 4.30%
   - You lose life cover of {sum_assured}
   - Continue paying premiums to continue insurance cover of {sum_assured}
   - Loyalty additions of {loyalty_benefits} over policy term

3. Immediate/Emergency Financial Needs/Medical emergency:
   - Specific due dates by which premium needs to be paid, and on your not paying premium, life insurance worth {sum_assured} has been reduced to NIL
   - Suggest the customer to pay the premium by credit card
   - After paying the current outstanding amount of {outstanding_amount} you can switch to half-yearly, quarterly or monthly frequency
   - You have the option of partial withdrawal to address your emergency needs (if policy completed 5 years)

4. Better alternatives available (Mutual funds/Business):
   - Compare future effective charges vs. alternative financial plans
   - Most mutual funds have effective charge of 2% due to expense ratios AND do not provide life insurance cover
   - In your policy, effective charges reduce and returns get closer to actual fund return
   - Loyalty additions of {loyalty_benefits} over policy term - not available in mutual funds

5. Low/unsatisfactory returns in policy:
   - In your policy, the effective charges reduce sharply post the lock-in period
   - Effective charges for rest of policy term is only 1.61%
   - You can switch your monies to any other funds based on your risk appetite
   - Current fund value: {fund_value}

6. Buying a new policy:
   - ULIPs have higher charges in initial years compared to later years
   - Not wise to purchase new ULIP by surrendering existing policy
   - Effective charges for rest of policy term is only 1.61% which is much cheaper than new ULIP

=== PAYMENT FOLLOW-UP ===

Branch 5.0 - Payment Follow-up:
Arjun: May I know how you plan to make the payment of {outstanding_amount}? Will it be via cash, cheque, or online?

If customer chooses online:
Arjun: You can use Debit card, Credit card, Net banking, PhonePe, WhatsApp or Google Pay to make the payment.

Branch 7.0 - Financial Problem:
Arjun: I understand your concern. To achieve your financial goals, staying invested is key. You can pay {outstanding_amount} via credit card, EMI, or change your payment mode to monthly. Can you arrange the premium to continue benefits?

Branch 8.0 - Final Rebuttals:
- You can opt for Partial Withdrawal option after completing 5 years of the policy
- If premiums stop before lock-in period ends, policy will discontinue and growth will be limited to 4-4.5% returns
- You will lose your sum assured value of {sum_assured}
- At maturity you will receive {fund_value}
- Would you be willing to pay your premium of {outstanding_amount} now?

Branch 9.0 - Conversation Closure:
Arjun: For any further assistance with your policy, feel free to call our helpline at 1800 209 7272, message us on WhatsApp on 8806 727272, mail us or visit our website. Thank you for your valuable time. Have a great day ahead.

=== BILINGUAL QUICK PHRASES ===

COMMON ENGLISH PHRASES:
- "Thank you for your time" 
- "I understand your concern"
- "Let me help you with this"
- "Would you like to proceed?"
- "Can you arrange the premium?"

COMMON HINDI PHRASES:
- "आपके समय के लिए धन्यवाद" (Thank you for your time)
- "मैं आपकी चिंता समझ सकती हूं" (I understand your concern)  
- "मैं इसमें आपकी मदद करती हूं" (Let me help you with this)
- "क्या आप आगे बढ़ना चाहेंगे?" (Would you like to proceed?)
- "क्या आप प्रीमियम का इंतजाम कर सकते हैं?" (Can you arrange the premium?)

AMOUNT PRONUNCIATION:
- English: "thirty five thousand rupees"
- Hindi: "पैंतीस हज़ार रुपये"

=== QUICK REFERENCE ===
Customer Name: {policy_holder_name}
Policy Number: {policy_number}
Outstanding Amount: {outstanding_amount}
Sum Assured: {sum_assured}
Due Date: {premium_due_date}
Status: {status}
Fund Value: {fund_value}
Loyalty Benefits: {loyalty_benefits}

=== END OF SCRIPT ===
"""

    def connect_to_db(self):
        """Connect to SQLite database (fallback method)"""
        try:
            if not os.path.exists(self.db_path):
                print(f"❌ Database file '{self.db_path}' not found!")
                return None
            
            conn = sqlite3.connect(self.db_path)
            return conn
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            return None

    def get_longest_overdue_customer(self):
        """Get customer with longest overdue premium"""
        if self.use_mcp and MCP_AVAILABLE:
            return self._get_longest_overdue_mcp()
        else:
            return self._get_longest_overdue_direct()
    
    def _get_longest_overdue_mcp(self):
        """Get customer using MCP server function"""
        try:
            print("🔧 Using MCP server for data retrieval...")
            result = mcp_get_longest_overdue()
            
            if result:
                response_data = json.loads(result)
                
                if "error" in response_data:
                    print(f"❌ {response_data['error']}")
                    return None
                
                customer_data = response_data
                print(f"✅ Found longest overdue customer: {customer_data['policy_holder_name']}")
                print(f"📅 Due date: {customer_data['premium_due_date']}")
                print(f"💰 Outstanding: {float(customer_data['outstanding_amount']):,.2f}")
                
                return customer_data
            else:
                print("❌ No response from MCP server!")
                return None
                
        except Exception as e:
            print(f"❌ Error calling MCP server: {e}")
            print("📋 Falling back to direct database access...")
            return self._get_longest_overdue_direct()
    
    def _get_longest_overdue_direct(self):
        """Get customer using direct database access (fallback)"""
        conn = self.connect_to_db()
        if not conn:
            return None
        
        try:
            print("🔧 Using direct database access...")
            cursor = conn.cursor()
            
            # Get customer with longest overdue date (earliest due date)
            query = """
                SELECT * FROM policy_info
                WHERE status = 'Discontinuance' OR status = 'overdue' OR outstanding_amount > 0
                ORDER BY date(premium_due_date) ASC 
                LIMIT 1
            """
            
            cursor.execute(query)
            result = cursor.fetchone()
            
            if result:
                # Get column names
                column_names = [description[0] for description in cursor.description]
                # Convert to dictionary
                customer_data = dict(zip(column_names, result))
                
                print(f"✅ Found longest overdue customer: {customer_data['policy_holder_name']}")
                print(f"📅 Due date: {customer_data['premium_due_date']}")
                print(f"💰 Outstanding: {customer_data['outstanding_amount']:,.2f}")
                
                return customer_data
            else:
                print("❌ No overdue customers found!")
                return None
                
        except Exception as e:
            print(f"❌ Error querying database: {e}")
            return None
        finally:
            conn.close()

    def format_currency(self, amount):
        """Format currency as plain number without commas or symbols"""
        if amount is None:
            return "0"
        
        try:
            amount = int(float(amount))  # Convert to integer to remove decimals
            return str(amount)  # Return plain number without commas
        except:
            return str(amount)
    
    def number_to_words(self, amount):
        """Convert number to words in Indian format for better AI understanding"""
        if amount is None:
            return "zero rupees"
        
        try:
            amount = int(float(amount))
            
            ones = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 
                   'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 
                   'seventeen', 'eighteen', 'nineteen']
            
            tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
            
            def convert_hundreds(num):
                result = ''
                if num >= 100:
                    result += ones[num // 100] + ' hundred '
                    num %= 100
                if num >= 20:
                    result += tens[num // 10] + ' '
                    num %= 10
                if num > 0:
                    result += ones[num] + ' '
                return result.strip()
            
            if amount == 0:
                return "zero rupees"
            
            result = ''
            crores = amount // 10000000
            amount %= 10000000
            
            if crores > 0:
                result += convert_hundreds(crores) + ' crore '
            
            lakhs = amount // 100000
            amount %= 100000
            
            if lakhs > 0:
                result += convert_hundreds(lakhs) + ' lakh '
            
            thousands = amount // 1000
            amount %= 1000
            
            if thousands > 0:
                result += convert_hundreds(thousands) + ' thousand '
            
            if amount > 0:
                result += convert_hundreds(amount)
            
            result = result.strip()
            if result:
                return result + ' rupees'
            else:
                return 'zero rupees'
                
        except:
            return f"{amount} rupees"

    def create_customer_script_file(self, customer_data):
        """Create personalized script file for customer"""
        try:
            # Create customer_details_script folder if it doesn't exist
            folder_name = "customer_details_script"
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
                print(f"📁 Created folder: {folder_name}")
            
            # Format the data for placeholders with both numerical and word formats
            outstanding_amt = customer_data.get('outstanding_amount', 0)
            total_paid = customer_data.get('total_premium_paid', 0)
            sum_assured_amt = customer_data.get('sum_assured', 0)
            fund_value_amt = customer_data.get('fund_value', 0)
            loyalty_amt = customer_data.get('loyalty_benefits', 0)
            
            formatted_data = {
                'policy_holder_name': customer_data.get('policy_holder_name', 'Customer'),
                'policy_number': customer_data.get('policy_number', 'N/A'),
                'product_name': customer_data.get('product_name', 'Insurance Policy'),
                'policy_start_date': customer_data.get('policy_start_date', 'N/A'),
                'premium_due_date': customer_data.get('premium_due_date', 'N/A'),
                'outstanding_amount': f"{self.number_to_words(outstanding_amt)} ({self.format_currency(outstanding_amt)})",
                'total_premium_paid': f"{self.number_to_words(total_paid)} ({self.format_currency(total_paid)})",
                'sum_assured': f"{self.number_to_words(sum_assured_amt)} ({self.format_currency(sum_assured_amt)})",
                'fund_value': f"{self.number_to_words(fund_value_amt)} ({self.format_currency(fund_value_amt)})",
                'status': customer_data.get('status', 'Discontinuance'),
                'loyalty_benefits': f"{self.number_to_words(loyalty_amt)} ({self.format_currency(loyalty_amt)})"
            }
            
            # Fill in the placeholders
            personalized_script = self.calling_script.format(**formatted_data)
            
            # Create filename with customer name
            customer_name = customer_data.get('policy_holder_name', 'Customer').replace(' ', '_')
            filename = f"{customer_name}_calling_script.txt"
            
            # Full path including the folder
            full_path = os.path.join(folder_name, filename)
            
            # Write to file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(personalized_script)
            
            print(f"✅ Script file created: {full_path}")
            return full_path
            
        except Exception as e:
            print(f"❌ Error creating script file: {e}")
            return None

    def generate_script_for_overdue_customer(self):
        """Main method to generate script for longest overdue customer"""
        print("🔍 Searching for longest overdue customer...")
        
        # Get customer data
        customer_data = self.get_longest_overdue_customer()
        if not customer_data:
            return None
        
        print("\n📋 Customer Details:")
        print(f"   Name: {customer_data.get('policy_holder_name')}")
        print(f"   Policy: {customer_data.get('policy_number')}")
        print(f"   Product: {customer_data.get('product_name')}")
        print(f"   Due Date: {customer_data.get('premium_due_date')}")
        print(f"   Outstanding: {float(customer_data.get('outstanding_amount', 0)):,.2f}")
        print(f"   Status: {customer_data.get('status')}")
        
        # Create script file
        print("\n📝 Creating personalized calling script...")
        filename = self.create_customer_script_file(customer_data)
        
        if filename:
            print(f"\n🎉 Successfully created: {filename}")
            print(f"📂 File location: {os.path.abspath(filename)}")
            
            # Show file size
            file_size = os.path.getsize(filename) / 1024  # KB
            print(f"📊 File size: {file_size:.1f} KB")
            
            return filename
        
        return None

def main():
    """Main function"""
    print("🚀 Customer Script Generator with MCP Server")
    print("=" * 50)
    
    if MCP_AVAILABLE:
        print("✅ MCP Server integration available")
    else:
        print("⚠️ MCP Server not available, using direct database access")
    
    print()
    
    # Initialize generator
    generator = CustomerScriptGenerator()
    
    # Generate script
    result = generator.generate_script_for_overdue_customer()
    
    if result:
        print(f"\n✅ Process completed successfully!")
        print(f"📄 Script ready for VapiAI integration")
        print(f"📂 All scripts are saved in: customer_details_script/ folder")
        
        # Show folder contents
        folder_path = "customer_details_script"
        if os.path.exists(folder_path):
            files = os.listdir(folder_path)
            print(f"📋 Files in folder: {len(files)} script(s)")
            for file in files:
                file_path = os.path.join(folder_path, file)
                file_size = os.path.getsize(file_path) / 1024  # KB
                print(f"   📄 {file} ({file_size:.1f} KB)")
    else:
        print(f"\n❌ Process failed!")

if __name__ == "__main__":
    main()