# 🤖 NITROS Insurance Bot - AI-Powered Customer Outreach

> **Automated Insurance Premium Collection with AI Voice Calls**

## 🎯 Overview

**NITROS Insurance Bot** is an intelligent automated system that identifies overdue insurance customers and makes personalized AI voice calls to collect outstanding premiums. The system uses advanced natural language processing to handle customer objections and maintain professional conversations.

### 🌟 Key Features

- 🎯 **Smart Customer Targeting**: Automatically finds longest overdue customers
- 🤖 **AI Voice Assistant**: Professional "Veena" persona with Indian English accent
- 📝 **Personalized Scripts**: Dynamic script generation based on customer data
- 📞 **Automated Calling**: One-click campaign execution
- 💾 **Transcript Storage**: Complete conversation records
- 📊 **Database Integration**: SQLite-based customer management

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- VAPI Account ([Sign up here](https://vapi.ai))

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp env_example.txt .env
# Edit .env with your VAPI credentials

# 3. Create database
python data_insertion/create_database.py

# 4. Run the bot! 🎯
python vapi_insurance_bot.py
```

### Environment Variables
```bash
VAPI_API_KEY=your_vapi_private_api_key
VAPI_PHONE_NUMBER_ID=your_vapi_phone_number_id
DATABASE_PATH=insurance_db.sqlite
```

---

## 📁 Project Structure

```
Customer_Bot/
├── 🤖 vapi_insurance_bot.py          # Main AI bot orchestrator
├── 📝 customer_script_generator.py   # Dynamic script generation
├── 🎭 system_promt.py                # AI assistant personality
├── 📊 Data_Insertion/
│   └── create_database.py            # Database setup & sample data
├── 📂 Customer_Details_Script/       # Generated customer scripts
├── 📂 Customer_transcripts/          # Call conversation records
├── 💾 insurance_db.sqlite           # Customer database
├── 🔧 insurance_mcp_server.py       # MCP server configuration
├── 📦 requirements.txt              # Python dependencies
└── 📖 README.md                     # This file
```

---

## 🎭 AI Assistant - "Veena"

**Persona**: Professional female insurance agent  
**Voice**: Azure `en-IN-NeerjaNeural` (Indian English)  
**Language**: Indian English with polite, persistent approach  
**Specialty**: Premium collection and customer retention

### Conversation Flow
1. **Greeting**: Professional introduction
2. **Identity Verification**: Confirm speaking with policy holder
3. **Policy Details**: Review outstanding premium information
4. **Objection Handling**: Address common customer concerns
5. **Payment Collection**: Secure payment commitment
6. **Closure**: Professional call ending

---

## 🔧 How It Works

### 1. Database Management
- **SQLite Database**: Stores customer policy information
- **Automatic Querying**: Finds longest overdue customers
- **Customer Data**: Retrieves policy details and contact information

### 2. Script Generation
- **Dynamic Templates**: Personalized scripts per customer
- **Policy Integration**: Includes specific customer data
- **Objection Handling**: Built-in rebuttals for common concerns

### 3. VAPI Integration
- **Assistant Creation**: Automatic AI setup with customer context
- **Voice Configuration**: Professional Indian English voice
- **Call Management**: Automated outbound calling system

### 4. Transcript Management
- **Auto-Saving**: Complete conversation records
- **Organized Storage**: Customer-specific file naming
- **Metadata Tracking**: Call duration, status, and analytics

---

## 📊 Database Structure

```sql
-- Customer Policy Information
CREATE TABLE policy_info (
    id INTEGER PRIMARY KEY,
    policy_holder_name TEXT,      -- Customer name
    policy_number TEXT,           -- Unique policy ID
    product_name TEXT,            -- Insurance product
    outstanding_amount REAL,      -- Due premium amount
    premium_due_date TEXT,        -- Payment deadline
    phone_number TEXT,            -- Contact number
    status TEXT,                  -- Policy status
    total_premium_paid REAL,      -- Total paid amount
    sum_assured REAL,             -- Policy coverage amount
    fund_value REAL,              -- Current fund value
    loyalty_benefits REAL         -- Loyalty benefits
);
```

---

## 🎯 Usage

### Run Automated Campaign
```bash
python vapi_insurance_bot.py
```

### Expected Output
```
🚀 Starting VAPI Insurance Bot Campaign
============================================================
🔍 Finding customer with longest overdue premium...
✅ Found longest overdue customer: Pratik Jadhav
📅 Due date: 2024-08-15
💰 Outstanding: ₹15,500.00

🎯 Target Customer: Pratik Jadhav
📋 Policy: PN1001
💰 Outstanding: ₹15,500.00

📝 Generating script for Pratik Jadhav...
🤖 Creating VAPI assistant for Pratik Jadhav...
✅ Assistant created successfully: asst_abc123
📞 Making call to customer...
✅ Call initiated successfully: call_xyz789
⏳ Monitoring call for up to 15 minutes...
📊 Call status: completed
✅ Transcript saved: Customer_Transcripts/Pratik_Jadhav_20241201_143022.txt

🎉 Campaign completed successfully!
```

---

## 🛠️ Customization

### Voice Configuration
```python
# In vapi_insurance_bot.py
"voice": {
    "provider": "azure",
    "voiceId": "en-IN-NeerjaNeural",  # Change voice here
    "speed": 1.0
}
```

### System Prompt
Edit `system_promt.py` to customize the AI assistant's personality and conversation style.

### Database Schema
Modify `data_insertion/create_database.py` to add new customer fields or change data structure.

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `VAPI_API_KEY not found` | Check `.env` file exists with correct API key |
| `No overdue customers found` | Run `create_database.py` to generate sample data |
| `Failed to create assistant` | Verify VAPI API key has correct permissions |
| `Call failed to connect` | Check phone number ID and VAPI account credits |
| `No transcript available` | Ensure artifactPlan is enabled in assistant config |

---

## 📈 Scaling

### Multi-Customer Campaigns
```python
# Process multiple overdue customers
overdue_customers = get_all_overdue_customers()
for customer in overdue_customers:
    run_single_campaign(customer)
    time.sleep(300)  # 5-minute delay
```

### Integration Options
- **CRM Systems**: Connect to existing customer management
- **Payment Gateways**: Integrate for immediate payment collection
- **Analytics Dashboard**: Web interface for campaign monitoring
- **SMS Notifications**: Pre-call customer alerts

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **VAPI.ai** for providing the AI voice calling platform
- **Azure Cognitive Services** for natural-sounding voice synthesis
- **SQLite** for lightweight database management
- **OpenAI GPT-4** for intelligent conversation handling

---

<div align="center">

**Made with ❤️ for Automated Customer Outreach**

[![VAPI](https://img.shields.io/badge/Powered%20by-VAPI-orange?style=for-the-badge&logo=vapi)](https://vapi.ai)

*Transform your customer communication with AI-powered voice calls! 🚀*

</div> 