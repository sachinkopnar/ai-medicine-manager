# 💊 AI Medicine Manager

A smart AI-powered Medicine Management System built using **Python** and **Streamlit** that helps users manage daily medicines, track adherence, scan prescriptions using OCR, and visualize health analytics — all in one place.

---

## 🚀 Live Demo

🔗 **Hugging Face Space**

https://huggingface.co/spaces/bhavyamanashwi/medicine_manager

---

# 🧠 Overview

AI Medicine Manager simplifies medication tracking by combining:

* ✅ Smart medicine scheduling
* ✅ Daily reminders dashboard
* ✅ OCR-based prescription scanning
* ✅ User authentication system
* ✅ Health analytics and adherence tracking

Built entirely with Python and deployed on Hugging Face Spaces for easy accessibility.

---

# ⚙️ Tech Stack

## 🐍 Core Technology

* Python 3.10+

## 🖥️ Frontend & Backend

* Streamlit

## 📊 Data Handling

* Pandas
* JSON Storage

## 🧾 OCR (Prescription Scanning)

* pytesseract
* Pillow

## 📈 Data Visualization

* Matplotlib

## ☁️ Deployment

* Hugging Face Spaces

---

# ✨ Features

## 👤 User Authentication

* Secure Login and Signup
* Password hashing using SHA-256
* User-specific medicine records

---

## 💊 Medicine Management

Users can:

* Add medicines
* Specify dosage
* Set medicine timings
* Track daily medication history
* Mark medicines as taken
* View pending doses

---

## 📅 Smart Dashboard

* Today's medicine schedule
* Real-time updates using Streamlit session state
* Taken vs Pending status

---

## 🧾 OCR Prescription Scanner

Upload prescription images and automatically extract medicine information using OCR.

### Benefits

* Digitizes prescriptions
* Reduces manual entry
* Improves medication organization

---

## 📊 Analytics Dashboard

Visual insights into:

* Medicines taken
* Pending medicines
* Daily adherence patterns

Charts are generated using Matplotlib for easy interpretation.

---

## 🧠 AI-Inspired Smart Logic

The system includes intelligent rule-based features:

* Duplicate medicine detection
* Missed dose tracking
* Safety-oriented awareness checks

---

# 🏗️ Project Structure

```text
AI_MEDICINE_MANAGER_ENHANCED/
│
├── app.py                 # Main Streamlit application
├── auth.py                # Authentication system
├── medicine.py            # Medicine management logic
├── ocr.py                 # Prescription OCR module
├── utils.py               # Helper functions
├── requirements.txt
│
└── data/
    ├── users.json
    └── medicines.json
```

---

# 🚀 Running Locally

## 1️⃣ Clone the Repository

git clone https://github.com/bhavya_manashwi/Medicine_Manager.git


cd Medicine_Manager


## 2️⃣ Install Dependencies

pip install -r requirements.txt


## 3️⃣ Run the Application

python -m streamlit run app.py


The application will open automatically in your browser at:

http://localhost:8501


---

# ☁️ Deployment

The project is deployed using **Hugging Face Spaces (Streamlit SDK).**

### Live Application

https://huggingface.co/spaces/bhavyamanashwi/medicine_manager

---

# 📌 Future Improvements

* 📧 Email reminders
* 📱 WhatsApp notifications
* 💊 AI-based drug interaction detection
* 🗄️ Migration from JSON to SQLite
* 📊 Advanced health analytics
* 📲 Improved mobile responsiveness
* 🌐 Multi-language support (Indian languages)

---

# ⚠️ Disclaimer

This project is developed for **educational purposes only** and should not be considered a substitute for professional medical advice, diagnosis, or treatment.

---

# 👨‍💻 Authors

### Bhavya Manashwi

* AI Developer
* Python & Streamlit Enthusiast

### Sachin Kopnar

* Project Collaborator

---

## ⭐ Support

If you found this project useful, consider giving it a **star ⭐** and sharing it with others!
