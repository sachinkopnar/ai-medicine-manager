# 💊 AI Medicine Manager

A smart, AI-powered medicine management system built with **Python and Streamlit**. It helps users and their families manage daily medicines, get dose reminders, scan prescriptions with OCR, track adherence, and generate reports, all in one place.

## 🚀 Live Demo

🔗 **https://YOUR-APP-NAME.streamlit.app**

> Data on the hosted demo is stored in server files and resets when the app restarts. Create a fresh account when you try it.

## 🧠 Overview

AI Medicine Manager combines:

- ✅ Multiple patient and family profiles under one account
- ✅ Smart medicine scheduling with dose tracking
- ✅ Alarm-style dosage reminders
- ✅ OCR-based prescription scanning with AI parsing
- ✅ AI medicine assistant (chatbot)
- ✅ Automatic PDF medication reports
- ✅ Low-stock alerts and appointment tracking
- ✅ Adherence analytics and visual dashboards

## ✨ Features

### 👤 User Authentication
- Secure login and signup
- Password hashing using SHA-256
- Crash-safe data saving (atomic file writes), so records are not corrupted if the app closes mid-save

### 👨‍👩‍👧 Multiple Patient / Family Profiles
- One account can manage Self, Father, Mother, Spouse, children, and more
- Each profile has its own medicines, schedule, dose history, stock, and appointments
- Profile switcher in the sidebar and a Manage Profiles page (add, edit, delete)

### 💊 Medicine Management
- Add, edit, and delete medicines with dosage, frequency, timings, notes, and start/end dates
- Mark doses as taken, with undo
- Duplicate medicine detection and overdose-risk warnings
- AI-based drug interaction check in My Medicines

### 🔔 Dosage Reminders
- Due Now banner on the Dashboard with one-tap Taken button
- Browser desktop notifications with an alarm-style sound (stay on screen until dismissed)
- Settings page: enable/disable, sound, alert window (minutes before a dose), check interval
- Automatic periodic checks without logging the user out

> Browser notifications work while the app tab is open in the browser.

### 📦 Low Stock Alerts
- Optional stock tracking per medicine
- Stock counts down automatically when a dose is marked taken (and restores on undo)
- Dashboard Low Stock banner with a quick Restock button
- Stock shown in My Medicines and in the PDF report

### 📅 Appointment Tracker
- Add, edit, and delete doctor or clinic appointments per profile
- Upcoming and past appointment lists
- Next Appointment highlight card on the Dashboard

### 📑 Automatic Medication Report (PDF)
- One-click downloadable PDF for the active profile
- Includes patient info, current medicines (with stock), today's adherence summary, and 7-day history
- Handy to bring to a doctor's visit

### 🧾 OCR Prescription Scanner
- Upload a prescription image and extract medicine details using OCR
- AI enhancement parses the text and auto-fills the Add Medicine form

### 🤖 AI Medicine Assistant
- Ask questions such as "what is this medicine for?"
- Uses the active profile's medicine list as context
- Supports multiple AI providers: Groq, OpenAI, Anthropic, Gemini, and Ollama (local)

### 📊 Analytics Dashboard
- Today's taken, missed, and pending doses
- Adherence percentage and dose history charts (Matplotlib)

### 🎨 Interface
- Dark and light themes
- Multi-language UI: English, Hindi, Telugu

## ⚙️ Tech Stack

| Area | Technology |
|------|------------|
| Language | Python 3.9+ |
| App framework | Streamlit |
| Data handling | Pandas, JSON storage |
| OCR | pytesseract, Pillow |
| Charts | Matplotlib |
| PDF reports | ReportLab |
| Auto-refresh | streamlit-autorefresh |
| AI providers | Groq, OpenAI, Anthropic, Gemini, Ollama |
| Deployment | Streamlit Community Cloud |

## 🏗️ Project Structure

```
medicine_manager-main/
│
├── app.py              # Main Streamlit application and all pages
├── auth.py             # Login / signup and password hashing
├── profiles.py         # Family / patient profile management
├── medicine.py         # Medicines, dose log, stock, analytics logic
├── reminders.py        # Due-now dose detection for reminders
├── appointments.py     # Doctor appointment tracker
├── reports.py          # PDF medication report generator
├── ocr.py              # Prescription OCR module
├── ai_backend.py       # AI providers (chat, OCR parsing, interactions)
├── theme.py            # Dark / light theme
├── languages.py        # Multi-language text
├── utils.py            # Helper functions
├── requirements.txt    # Python dependencies
├── packages.txt        # System packages (Tesseract OCR) for hosting
│
└── data/               # Created automatically at runtime (not uploaded to Git)
```

## 🚀 Running Locally

**1. Clone the repository**

```
https://github.com/sachinkopnar/ai-medicine-manager.git
```

**2. Install dependencies**

```
pip install -r requirements.txt
```

On Windows, if `pip` is not recognized, use:

```
py -m pip install -r requirements.txt
```

**3. Run the app**

```
python -m streamlit run app.py
```

On Windows you can also use `py -m streamlit run app.py`. The app opens at `http://localhost:8501`.

**4. (Optional) Enable the OCR scanner**

Install the Tesseract OCR program on your computer. All other features work without it.

**5. (Optional) Enable AI features**

Add your API key in the app's AI Settings page, or set an environment variable such as `GROQ_API_KEY`.

## ☁️ Deployment

The app is deployed on **Streamlit Community Cloud** from a public GitHub repository:

1. Push the project files to GitHub (do not upload the `data/` folder or any `.env` file).
2. Sign in at share.streamlit.io with GitHub and click Create app.
3. Choose the repository, branch `main`, and main file `app.py`.
4. In Advanced settings, choose Python 3.11 or 3.12 and, optionally, add `GROQ_API_KEY = "your-key"` under Secrets.
5. Click Deploy.

## 📌 Future Improvements

- 📤 CSV / Excel export of medicine and dose history
- 📈 Advanced analytics (weekly and monthly trends, adherence streaks)
- 💾 Data backup and restore
- 📧 Email reminders
- 📱 WhatsApp notifications
- 🗄️ Migration from JSON to SQLite
- 📲 Improved mobile responsiveness

 ⚠️ Disclaimer

This project is developed for educational purposes only and should not be considered a substitute for professional medical advice, diagnosis, or treatment.

 👨‍💻 Authors
**Bhavya Manashwi**
- AI Developer
- Python and Streamlit Enthusiast

**Sachin Kopnar**
- Project Collaborator: Family Profiles, Dosage Reminders, PDF Medication Reports, Low Stock Alerts, Appointment Tracker, and deployment

⭐ Support
If you found this project useful, consider giving it a star on GitHub.
