📄 README.md
markdown
# 🚀 AssetFlow AI - Intelligent Enterprise Asset Management Platform

> **Built for Odoo Hackathon 2026** by Team AssetFlow

---

## 👥 Team Members

| Name | Role | Contribution |
|------|------|--------------|
| **Purushottam Kumar Thakur** |Full Stack Developer | Architecture, Backend, AI Integration |
| **Harsh Prajapati** | Team Lead / UI/UX Designer & Frontend Developer | Premium UI, Glassmorphism Design |
| **Deepak Soni** | Database & API Developer | Database Design, REST APIs |
| **Ayush Jha** | AI & ML Engineer | AI Assistant, Predictions, Recommendations |

---

## 📖 About AssetFlow AI

AssetFlow AI is a **premium enterprise asset management platform** designed to solve real-world asset tracking problems. Built for companies managing 500+ laptops, 200+ projectors, 40+ meeting rooms, and more.

### 🎯 Problem We Solve

| Problem | Solution |
|---------|----------|
| ❌ Excel-based tracking is chaotic | ✅ Centralized digital asset management |
| ❌ No visibility of asset location | ✅ Real-time tracking & QR codes |
| ❌ Booking conflicts for resources | ✅ Smart booking with overlap detection |
| ❌ Maintenance requests get lost | ✅ Automated maintenance workflow |
| ❌ No insights on asset utilization | ✅ AI-powered analytics & recommendations |

---

## ✨ Features

### 🏆 Core Features
- **Asset Management** - CRUD operations with automatic tag generation (AF-0001)
- **Asset Allocation** - Assign assets to employees with transfer workflow
- **Resource Booking** - Book meeting rooms, projectors, vehicles with conflict detection
- **Maintenance Management** - Raise, approve, and track maintenance requests
- **QR Code Generation** - Every asset gets a unique QR code
- **Digital Twin 3D View** - Interactive 3D visualization of all assets

### 🤖 AI Features
- **AI Assistant** - Natural language queries (e.g., "Show overdue assets")
- **Smart Recommendations** - Idle assets, redistribution, replacement suggestions
- **Asset Health Score** - Auto-calculated based on age, maintenance, usage
- **Predictive Analytics** - Predict maintenance needs and asset lifespan
- **Daily Insights** - Auto-generated insights on dashboard

### 🎨 Premium UI
- **Milky Way Background** - Animated starfield with shooting stars
- **Glassmorphism Design** - Apple VisionOS style frosted glass
- **Command Palette** - Ctrl+K global search (like VSCode)
- **Responsive Design** - Works on all devices
- **Dark Theme** - Eye-friendly dark mode

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.10+, Flask 2.3.2 |
| **Database** | SQLite (with SQLAlchemy ORM) |
| **Frontend** | HTML5, CSS3, JavaScript |
| **UI Framework** | Custom Glassmorphism + Chart.js |
| **3D Visualization** | Three.js |
| **QR Code** | qrcode 7.4.2 |
| **AI** | Custom NLP engine (no external API) |

---

## 📁 Project Structure
AssetFlow_AI/
├── app.py # Main application entry point
├── config.py # Configuration settings
├── requirements.txt # Python dependencies
├── assetflow.db # SQLite database (auto-created)
├── README.md # This file
│
├── database/ # Database layer
│ ├── database.py # DB connection
│ ├── models.py # All models (User, Asset, etc.)
│ ├── init_db.py # DB initialization
│ └── seed_data.py # Sample data seeding
│
├── routes/ # Route handlers
│ ├── auth.py # Login, Signup, Profile
│ ├── dashboard.py # Dashboard & stats
│ ├── assets.py # Asset CRUD
│ ├── allocation.py # Asset allocation
│ ├── booking.py # Resource booking
│ ├── maintenance.py # Maintenance requests
│ ├── reports.py # Reports & export
│ ├── notifications.py # Notifications
│ ├── qr.py # QR code generation
│ ├── ai.py # AI endpoints
│ ├── health.py # Health score
│ ├── digital_twin.py # 3D visualization data
│ └── settings.py # Settings
│
├── ai/ # AI Module
│ ├── assistant.py # NLP chat assistant
│ ├── recommendation.py # Smart recommendations
│ ├── asset_prediction.py # Predictive analytics
│ ├── smart_search.py # Intelligent search
│ ├── rule_engine.py # Business rules
│ └── knowledge.py # Knowledge base
│
├── templates/ # HTML templates
│ ├── login.html
│ ├── signup.html
│ ├── dashboard.html
│ ├── assets.html
│ ├── allocation.html
│ ├── booking.html
│ ├── maintenance.html
│ ├── reports.html
│ ├── notifications.html
│ ├── profile.html
│ ├── ai_assistant.html
│ ├── digital_twin.html
│ ├── analytics.html
│ └── settings.html
│
├── static/ # Static files
│ ├── css/
│ │ ├── style.css
│ │ ├── login.css
│ │ ├── dashboard.css
│ │ ├── ai.css
│ │ └── digital.css
│ ├── js/
│ │ ├── dashboard.js
│ │ ├── ai.js
│ │ ├── charts.js
│ │ ├── assets.js
│ │ ├── login.js
│ │ ├── signup.js
│ │ ├── notifications.js
│ │ ├── qr.js
│ │ └── twin.js
│ ├── images/ # Auto-generated
│ └── uploads/ # User uploads
│
├── generated_qr/ # Generated QR codes
└── uploads/ # Uploaded assets images

text

---

## 🚀 How to Run

### 1️⃣ Prerequisites

```bash
# Python 3.10+ required
python --version
2️⃣ Install Dependencies
bash
# Install all required packages
pip install -r requirements.txt
