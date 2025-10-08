# 🚀 Equipment Tracker - AI-Powered Equipment Management

> **Stop wasting time on manual tracking. Your drivers snap photos, AI extracts data, you get real-time visibility.**

An AI-powered equipment management system for rental companies. Drivers photograph delivery notes, AI extracts the data instantly, and your office gets real-time visibility of all equipment.

## ⚡ Quick Links

**📖 [START HERE: Launch Guide](LAUNCH_GUIDE.md)** - Your complete guide to deployment

**🔒 [Security Checklist](SECURITY_CHECKLIST.md)** - Security audit before deployment

**🚀 [Deployment Commands](DEPLOYMENT_COMMANDS.md)** - Step-by-step deployment

**📢 [Marketing Strategy](MARKETING_ASSETS.md)** - Complete marketing playbook

**✅ [Deployment Ready](DEPLOYMENT_READY.md)** - System status & next steps

---

## 🎯 Features

### Core Functionality
- 📸 **AI Photo Recognition** - Upload delivery notes, AI extracts all data
- 📊 **Real-Time Tracking** - Know exactly where all equipment is, always
- 🚚 **Smart Driver Instructions** - Auto-generated collection reminders
- 👥 **Fleet Management** - Track drivers, vehicles, licenses, MOT, insurance
- 💰 **Balance Tracking** - Customer equipment balances with threshold alerts
- 📱 **Mobile-First** - Optimized driver app for phones

### Security & Performance
- 🔐 **JWT Authentication** - Secure login with role-based access
- ⚡ **Rate Limiting** - 60 requests/min protection
- 🛡️ **Security Headers** - XSS, clickjacking protection
- 🔒 **SSL/TLS** - Encrypted data in transit
- 💾 **Database Encryption** - Encrypted data at rest

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **AI Service**: Claude Sonnet integration for image processing
- **Database Models**: SQLAlchemy models for equipment movements and balances
- **Balance Service**: Automatic balance calculation and threshold monitoring
- **Storage Service**: S3 integration for image storage
- **API Endpoints**: RESTful endpoints for all operations

### Frontend (React)
- **Dashboard**: Overview of system status and recent activity
- **Photo Upload**: Drag-and-drop interface for delivery note photos
- **Alerts Management**: View and manage equipment threshold alerts
- **Movement History**: Searchable and filterable movement records
- **Customer Balances**: Real-time equipment balance monitoring

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL database
- Anthropic API key (for Claude Sonnet)
- AWS S3 bucket (optional, for image storage)

## 🛠️ Installation

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd equipment_management_logistics

# Make quick start script executable
chmod +x quick_start.bash
```

### 2. Backend Setup

```bash
# Run the quick start script
./quick_start.bash
```

Or manually:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp env.example .env
# Edit .env with your API keys and database settings
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm start
```

### 4. Database Setup

Create a PostgreSQL database and update the `DATABASE_URL` in your `.env` file:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/equipment_tracker
```

## 🔧 Configuration

Edit the `.env` file with your configuration:

```env
# Required: Anthropic API Key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/equipment_tracker

# Optional: AWS S3 for image storage
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET_NAME=equipment-tracker-images

# Optional: Twilio for WhatsApp integration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

## 🚀 Running the Application

### Backend
```bash
python main.py
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Frontend
```bash
cd frontend
npm start
```

The dashboard will be available at: http://localhost:3000

## 📡 API Endpoints

### Core Endpoints

- `POST /upload-photo` - Upload delivery note photo for AI processing
- `GET /movements` - Retrieve equipment movements (with filtering)
- `GET /balances` - Get customer equipment balances
- `GET /alerts` - Get threshold breach alerts
- `POST /movements/{id}/verify` - Mark movement as verified
- `GET /health` - System health check

### Example Usage

```bash
# Upload a photo
curl -X POST "http://localhost:8000/upload-photo" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@delivery_note.jpg" \
  -F "driver_name=John Doe"

# Get movements
curl "http://localhost:8000/movements?customer_name=Acme%20Corp&limit=10"

# Get alerts
curl "http://localhost:8000/alerts"
```

## 🔍 How It Works

1. **Photo Upload**: Driver takes photo of delivery note/paperwork
2. **AI Processing**: Claude Sonnet extracts:
   - Customer name
   - Equipment type (pallets, cages, dollies, stillages)
   - Quantities
   - Direction (in/out from customer perspective)
   - Confidence score
3. **Data Storage**: Movement record created in database
4. **Balance Update**: Customer equipment balance automatically updated
5. **Alert Generation**: System checks thresholds and creates alerts if needed
6. **Dashboard Display**: Real-time visibility through web interface

## 🎯 Equipment Types Supported

- **Pallets**: Standard wooden/plastic pallets
- **Cages**: Metal transport cages
- **Dollies**: Wheeled transport equipment
- **Stillages**: Specialized storage frames
- **Other**: Custom equipment types

## 📊 Monitoring & Alerts

The system automatically monitors:
- **Over Threshold**: Customer has more equipment than their limit
- **Negative Balance**: Customer has negative equipment balance
- **High Priority**: Excess equipment > 150% of threshold
- **Medium Priority**: Excess equipment > 100% of threshold

## 🔒 Security Features

- Input validation and sanitization
- File type restrictions for uploads
- Confidence scoring for AI extractions
- Admin verification workflow
- CORS protection

## 🚧 Future Enhancements

- WhatsApp Business API integration for driver uploads
- SMS/Email alert notifications
- Mobile app for drivers
- Advanced analytics and reporting
- Multi-tenant support
- API authentication and authorization

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions, please open an issue in the repository.

