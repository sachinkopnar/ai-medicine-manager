"""
languages.py - i18n / l10n for AI Medicine Manager
Supports: English (en), Hindi (hi), Telugu (te)

i18n  = internationalisation: structuring the app to support multiple languages
l10n  = localisation: providing the actual translated strings for each locale

Usage:
    from languages import LANGUAGES, get_text
    t = LANGUAGES["te"]          # get Telugu dict
    label = t["dashboard"]       # "డాష్‌బోర్డ్"
"""

LANGUAGES: dict[str, dict[str, str]] = {

    # ── English ───────────────────────────────────────────────────────────────
    "en": {
        # Meta
        "lang_name": "English",
        "lang_flag": "🇬🇧",

        # App shell
        "title":          "AI Medicine Manager",
        "welcome":        "Welcome to the Medicine Manager",
        "app_tagline":    "Your personal AI health companion - track, manage, and never miss a dose.",
        "logout":         "Logout",

        # Navigation
        "dashboard":      "Dashboard",
        "add_medicine":   "Add Medicine",
        "my_medicines":   "My Medicines",
        "ocr":            "OCR Scanner",
        "analytics":      "Analytics",
        "ai_assistant":   "AI Assistant",
        "ai_settings":    "AI Settings",

        # Auth
        "login":              "Login",
        "signup":             "Sign Up",
        "username":           "Username",
        "password":           "Password",
        "confirm_password":   "Confirm Password",
        "email_optional":     "Email (optional)",
        "create_account":     "Create Account",
        "welcome_back":       "Welcome back",
        "create_account_h":   "Create account",
        "demo_hint":          "Demo: create an account in Sign Up, then log in.",
        "passwords_no_match": "Passwords do not match.",

        # Dashboard
        "greeting_morning":   "Good morning",
        "greeting_afternoon": "Good afternoon",
        "greeting_evening":   "Good evening",
        "medicines":          "Medicines",
        "todays_doses":       "Today's Doses",
        "taken":              "Taken",
        "missed":             "Missed",
        "adherence":          "Adherence",
        "pending":            "Pending",
        "todays_overview":    "Today's Overview",
        "todays_schedule":    "Today's Schedule",
        "no_medicines_hint":  "No medicines scheduled for today. Go to **Add Medicine** to get started.",
        "ai_tip":             "💡 AI Tip",

        # Medicine form
        "add_new_medicine":   "➕ Add New Medicine",
        "edit_medicine":      "✏️ Edit Medicine",
        "medicine_name":      "Medicine Name *",
        "medicine_name_ph":   "e.g. Paracetamol",
        "dosage":             "Dosage *",
        "dosage_ph":          "e.g. 500mg, 10ml",
        "frequency":          "Frequency *",
        "start_date":         "Start Date",
        "set_end_date":       "Set end date",
        "end_date":           "End Date",
        "dose_times":         "Dose Times",
        "notes_optional":     "Notes (optional)",
        "notes_ph":           "e.g. Take with food, avoid alcohol",
        "add_medicine_btn":   "➕ Add Medicine",
        "update_medicine_btn":"💾 Update Medicine",
        "time_label":         "Time",
        "ai_explainer_title": "🤖 AI Medicine Explainer",
        "medicine_to_explain":"Medicine to explain",
        "explain_ph":         "e.g. Metformin",
        "dosage_explain_ph":  "e.g. 500mg",
        "explain_btn":        "🤖 Explain This Medicine",
        "configure_ai_hint":  "💡 Configure AI in **AI Settings** to enable the medicine explainer.",

        # My Medicines
        "my_medicines_h":     "💊 My Medicines",
        "search_ph":          "Type name or dosage…",
        "check_interactions": "🤖 Check Interactions",
        "no_medicines_yet":   "You haven't added any medicines yet. Use **Add Medicine** to get started.",
        "frequency_label":    "Frequency:",
        "times_label":        "Times:",
        "start_label":        "Start:",
        "end_label":          "End:",
        "ongoing":            "Ongoing",
        "notes_label":        "Notes:",
        "edit_btn":           "✏️ Edit",
        "delete_btn":         "🗑️ Delete",
        "explain_btn_short":  "🤖 Explain",
        "suggest_schedule":   "📅 AI: Suggest Optimal Schedule",
        "configure_ai_first": "Configure AI in **AI Settings** first.",

        # OCR
        "ocr_title":          "📷 Prescription Scanner",
        "ocr_subtitle":       "Upload a prescription image. OCR extracts text; AI can further parse and structure the medicines.",
        "upload_label":       "Upload prescription image",
        "upload_hint":        "Clear, well-lit photos work best. Max ~10 MB.",
        "upload_placeholder": "Upload a prescription image to extract medicine details",
        "uploaded_prescription":"Uploaded Prescription",
        "extracted_info":     "Extracted Information",
        "rule_medicines":     "🔵 Rule-based Medicines:",
        "detected_dosages":   "🟡 Detected Dosages:",
        "medicine_lines":     "Medicine lines",
        "full_text":          "📄 Full extracted text",
        "ai_enhanced_parse":  "🤖 AI Enhanced Parse",
        "ai_parse_btn":       "🤖 AI: Parse Prescription",
        "quick_add_label":    "➕ Quick-add (rule-based):",
        "select_medicine":    "Select medicine",
        "go_add_medicine":    "Go to Add Medicine →",
        "ocr_tips":           "💡 **Tips:**\n- High-resolution photo\n- Good lighting\n- Horizontal text\n- No shadows",

        # Analytics
        "analytics_title":    "📊 Analytics",
        "active_medicines":   "Active Medicines",
        "todays_adherence":   "Today's Adherence",
        "7day_adherence":     "7-Day Adherence",
        "7day_chart_title":   "7-Day Dose Adherence",
        "todays_summary":     "Today's Summary",
        "by_frequency":       "Medicines by Frequency",
        "weekly_breakdown":   "Weekly Breakdown Table",
        "date_col":           "Date",
        "total_col":          "Total",
        "adherence_col":      "Adherence %",
        "ai_coach_title":     "🤖 AI Adherence Coach",
        "get_coaching":       "🤖 Get Personalised Coaching",
        "configure_ai_coach": "Configure AI in **AI Settings** to unlock the adherence coach.",

        # AI Assistant
        "ai_assistant_title": "🤖 AI Assistant",
        "ai_assistant_sub":   "Ask anything about your medicines, schedules, side effects, or general health questions.",
        "configure_ai_first_long": "⚙️ Please configure your AI provider in **AI Settings** first.",
        "go_ai_settings":     "Go to AI Settings →",
        "quick_actions":      "Quick Actions:",
        "drug_interactions":  "🔬 Drug Interactions",
        "optimise_schedule":  "📅 Optimise Schedule",
        "adherence_tips":     "📈 Adherence Tips",
        "clear_chat":         "🗑️ Clear Chat",
        "you":                "You",
        "ai":                 "AI",
        "ask_placeholder":    "e.g. Can I take ibuprofen with metformin? What are common side effects of lisinopril?",
        "include_meds":       "Include my medicine list as context",
        "send_btn":           "Send 📤",
        "ai_thinking":        "AI is thinking…",

        # AI Settings
        "ai_settings_title":  "⚙️ AI Settings",
        "ai_settings_sub":    "Configure your preferred AI backend. All keys are stored only in your browser session.",
        "ai_provider_label":  "AI Provider",
        "select_provider":    "Select provider",
        "test_connection":    "🔍 Test Connection",
        "test_api_key":       "🔍 Test API Key",
        "ollama_url":         "Ollama base URL",
        "select_model":       "Select model",
        "api_key_label":      "API Key",
        "privacy_note":       "🔒 **Privacy:** API keys are stored only in your Streamlit session (memory). They are never saved to disk or sent to any server other than the selected AI provider. Using Ollama means all data stays entirely on your device.",

        # Dose actions
        "mark_taken":         "✅ Taken",
        "undo_taken":         "↩ Undo",
        "status_taken":       "Taken",
        "status_missed":      "Missed",
        "status_pending":     "Pending",

        # AI status
        "ai_status_running":  "running",
        "ai_status_offline":  "offline",
        "ai_status_ready":    "ready",
        "ai_status_no_key":   "(no key)",

        # Misc
        "search_label":       "🔍 Search medicines",
        "no_dose_data":       "No dose data for the past 7 days.",
        "no_medicines_data":  "No medicines added yet.",
        "language_label":     "🌐 Language",
        "ai_found":           "AI found",
        "medicines_word":     "medicine(s)!",
    },

    # ── Hindi (हिन्दी) ────────────────────────────────────────────────────────
    "hi": {
        # Meta
        "lang_name": "हिन्दी",
        "lang_flag": "🇮🇳",

        # App shell
        "title":          "एआई दवा प्रबंधक",
        "welcome":        "मेडिसिन मैनेजर में आपका स्वागत है",
        "app_tagline":    "आपका व्यक्तिगत एआई स्वास्थ्य साथी - ट्रैक करें, प्रबंधित करें, और कोई खुराक न छोड़ें।",
        "logout":         "लॉग आउट",

        # Navigation
        "dashboard":      "डैशबोर्ड",
        "add_medicine":   "दवा जोड़ें",
        "my_medicines":   "मेरी दवाइयाँ",
        "ocr":            "OCR स्कैनर",
        "analytics":      "एनालिटिक्स",
        "ai_assistant":   "एआई सहायक",
        "ai_settings":    "एआई सेटिंग्स",

        # Auth
        "login":              "लॉग इन",
        "signup":             "साइन अप",
        "username":           "उपयोगकर्ता नाम",
        "password":           "पासवर्ड",
        "confirm_password":   "पासवर्ड की पुष्टि करें",
        "email_optional":     "ईमेल (वैकल्पिक)",
        "create_account":     "खाता बनाएं",
        "welcome_back":       "वापस स्वागत है",
        "create_account_h":   "खाता बनाएं",
        "demo_hint":          "डेमो: साइन अप में खाता बनाएं, फिर लॉग इन करें।",
        "passwords_no_match": "पासवर्ड मेल नहीं खाते।",

        # Dashboard
        "greeting_morning":   "सुप्रभात",
        "greeting_afternoon": "नमस्कार",
        "greeting_evening":   "शुभ संध्या",
        "medicines":          "दवाइयाँ",
        "todays_doses":       "आज की खुराकें",
        "taken":              "ली गई",
        "missed":             "छूटी हुई",
        "adherence":          "अनुपालन",
        "pending":            "बाकी",
        "todays_overview":    "आज का सारांश",
        "todays_schedule":    "आज का कार्यक्रम",
        "no_medicines_hint":  "आज के लिए कोई दवा निर्धारित नहीं है। शुरुआत करने के लिए **दवा जोड़ें** पर जाएं।",
        "ai_tip":             "💡 एआई सुझाव",

        # Medicine form
        "add_new_medicine":   "➕ नई दवा जोड़ें",
        "edit_medicine":      "✏️ दवा संपादित करें",
        "medicine_name":      "दवा का नाम *",
        "medicine_name_ph":   "जैसे: पैरासिटामोल",
        "dosage":             "खुराक *",
        "dosage_ph":          "जैसे: 500mg, 10ml",
        "frequency":          "आवृत्ति *",
        "start_date":         "शुरुआत की तारीख",
        "set_end_date":       "समाप्ति तिथि सेट करें",
        "end_date":           "समाप्ति तिथि",
        "dose_times":         "खुराक का समय",
        "notes_optional":     "नोट्स (वैकल्पिक)",
        "notes_ph":           "जैसे: खाने के साथ लें, शराब से बचें",
        "add_medicine_btn":   "➕ दवा जोड़ें",
        "update_medicine_btn":"💾 दवा अपडेट करें",
        "time_label":         "समय",
        "ai_explainer_title": "🤖 एआई दवा व्याख्याकार",
        "medicine_to_explain":"समझाने के लिए दवा",
        "explain_ph":         "जैसे: मेटफॉर्मिन",
        "dosage_explain_ph":  "जैसे: 500mg",
        "explain_btn":        "🤖 इस दवा को समझाएं",
        "configure_ai_hint":  "💡 दवा व्याख्याकार सक्षम करने के लिए **एआई सेटिंग्स** में एआई कॉन्फ़िगर करें।",

        # My Medicines
        "my_medicines_h":     "💊 मेरी दवाइयाँ",
        "search_ph":          "नाम या खुराक टाइप करें…",
        "check_interactions": "🤖 इंटरेक्शन जांचें",
        "no_medicines_yet":   "आपने अभी तक कोई दवा नहीं जोड़ी। **दवा जोड़ें** का उपयोग करके शुरू करें।",
        "frequency_label":    "आवृत्ति:",
        "times_label":        "समय:",
        "start_label":        "शुरुआत:",
        "end_label":          "समाप्ति:",
        "ongoing":            "जारी",
        "notes_label":        "नोट्स:",
        "edit_btn":           "✏️ संपादित करें",
        "delete_btn":         "🗑️ हटाएं",
        "explain_btn_short":  "🤖 समझाएं",
        "suggest_schedule":   "📅 एआई: इष्टतम समय-सारिणी सुझाएं",
        "configure_ai_first": "पहले **एआई सेटिंग्स** में एआई कॉन्फ़िगर करें।",

        # OCR
        "ocr_title":          "📷 प्रिस्क्रिप्शन स्कैनर",
        "ocr_subtitle":       "प्रिस्क्रिप्शन की छवि अपलोड करें। OCR टेक्स्ट निकालता है; एआई दवाओं को पार्स और संरचित कर सकता है।",
        "upload_label":       "प्रिस्क्रिप्शन छवि अपलोड करें",
        "upload_hint":        "स्पष्ट, अच्छी रोशनी वाली तस्वीरें सबसे अच्छी काम करती हैं।",
        "upload_placeholder": "दवा विवरण निकालने के लिए प्रिस्क्रिप्शन छवि अपलोड करें",
        "uploaded_prescription":"अपलोड की गई प्रिस्क्रिप्शन",
        "extracted_info":     "निकाली गई जानकारी",
        "rule_medicines":     "🔵 नियम-आधारित दवाइयाँ:",
        "detected_dosages":   "🟡 पाई गई खुराकें:",
        "medicine_lines":     "दवा की पंक्तियाँ",
        "full_text":          "📄 पूर्ण निकाला गया टेक्स्ट",
        "ai_enhanced_parse":  "🤖 एआई उन्नत पार्स",
        "ai_parse_btn":       "🤖 एआई: प्रिस्क्रिप्शन पार्स करें",
        "quick_add_label":    "➕ त्वरित जोड़ें (नियम-आधारित):",
        "select_medicine":    "दवा चुनें",
        "go_add_medicine":    "दवा जोड़ें पर जाएं →",
        "ocr_tips":           "💡 **सुझाव:**\n- उच्च-रिज़ॉल्यूशन फोटो\n- अच्छी रोशनी\n- क्षैतिज टेक्स्ट\n- कोई छाया नहीं",

        # Analytics
        "analytics_title":    "📊 एनालिटिक्स",
        "active_medicines":   "सक्रिय दवाइयाँ",
        "todays_adherence":   "आज का अनुपालन",
        "7day_adherence":     "7-दिन का अनुपालन",
        "7day_chart_title":   "7-दिन की खुराक अनुपालन",
        "todays_summary":     "आज का सारांश",
        "by_frequency":       "आवृत्ति अनुसार दवाइयाँ",
        "weekly_breakdown":   "साप्ताहिक विवरण तालिका",
        "date_col":           "तारीख",
        "total_col":          "कुल",
        "adherence_col":      "अनुपालन %",
        "ai_coach_title":     "🤖 एआई अनुपालन कोच",
        "get_coaching":       "🤖 व्यक्तिगत कोचिंग प्राप्त करें",
        "configure_ai_coach": "अनुपालन कोच अनलॉक करने के लिए **एआई सेटिंग्स** में एआई कॉन्फ़िगर करें।",

        # AI Assistant
        "ai_assistant_title": "🤖 एआई सहायक",
        "ai_assistant_sub":   "अपनी दवाओं, समय-सारिणी, दुष्प्रभावों या सामान्य स्वास्थ्य प्रश्नों के बारे में कुछ भी पूछें।",
        "configure_ai_first_long": "⚙️ कृपया पहले **एआई सेटिंग्स** में अपना एआई प्रदाता कॉन्फ़िगर करें।",
        "go_ai_settings":     "एआई सेटिंग्स पर जाएं →",
        "quick_actions":      "त्वरित क्रियाएँ:",
        "drug_interactions":  "🔬 दवा इंटरेक्शन",
        "optimise_schedule":  "📅 समय-सारिणी अनुकूलित करें",
        "adherence_tips":     "📈 अनुपालन सुझाव",
        "clear_chat":         "🗑️ चैट साफ करें",
        "you":                "आप",
        "ai":                 "एआई",
        "ask_placeholder":    "जैसे: क्या मैं मेटफॉर्मिन के साथ इबुप्रोफेन ले सकता हूँ?",
        "include_meds":       "संदर्भ के रूप में मेरी दवाओं की सूची शामिल करें",
        "send_btn":           "भेजें 📤",
        "ai_thinking":        "एआई सोच रहा है…",

        # AI Settings
        "ai_settings_title":  "⚙️ एआई सेटिंग्स",
        "ai_settings_sub":    "अपना पसंदीदा एआई बैकएंड कॉन्फ़िगर करें। सभी कुंजियाँ केवल आपके ब्राउज़र सत्र में संग्रहीत हैं।",
        "ai_provider_label":  "एआई प्रदाता",
        "select_provider":    "प्रदाता चुनें",
        "test_connection":    "🔍 कनेक्शन परीक्षण",
        "test_api_key":       "🔍 API कुंजी परीक्षण",
        "ollama_url":         "Ollama बेस URL",
        "select_model":       "मॉडल चुनें",
        "api_key_label":      "API कुंजी",
        "privacy_note":       "🔒 **गोपनीयता:** API कुंजियाँ केवल आपके Streamlit सत्र में संग्रहीत हैं। वे कभी भी डिस्क पर सहेजी नहीं जाती हैं।",

        # Dose actions
        "mark_taken":         "✅ ली गई",
        "undo_taken":         "↩ वापस लें",
        "status_taken":       "ली गई",
        "status_missed":      "छूट गई",
        "status_pending":     "बाकी",

        # AI status
        "ai_status_running":  "चल रहा है",
        "ai_status_offline":  "ऑफलाइन",
        "ai_status_ready":    "तैयार",
        "ai_status_no_key":   "(कुंजी नहीं)",

        # Misc
        "search_label":       "🔍 दवाइयाँ खोजें",
        "no_dose_data":       "पिछले 7 दिनों के लिए कोई खुराक डेटा नहीं।",
        "no_medicines_data":  "अभी तक कोई दवा नहीं जोड़ी गई।",
        "language_label":     "🌐 भाषा",
        "ai_found":           "एआई को मिलीं",
        "medicines_word":     "दवा(एं)!",
    },

    # ── Telugu (తెలుగు) ───────────────────────────────────────────────────────
    "te": {
        # Meta
        "lang_name": "తెలుగు",
        "lang_flag": "🇮🇳",

        # App shell
        "title":          "ఏఐ మందుల నిర్వాహకుడు",
        "welcome":        "మందుల నిర్వాహకుడుకి స్వాగతం",
        "app_tagline":    "మీ వ్యక్తిగత ఏఐ ఆరోగ్య సహాయకుడు - ట్రాక్ చేయండి, నిర్వహించండి, మోతాదు మర్చిపోకండి.",
        "logout":         "లాగ్ అవుట్",

        # Navigation
        "dashboard":      "డాష్‌బోర్డ్",
        "add_medicine":   "మందు జోడించు",
        "my_medicines":   "నా మందులు",
        "ocr":            "OCR స్కానర్",
        "analytics":      "విశ్లేషణలు",
        "ai_assistant":   "ఏఐ సహాయకుడు",
        "ai_settings":    "ఏఐ సెట్టింగులు",

        # Auth
        "login":              "లాగిన్",
        "signup":             "సైన్ అప్",
        "username":           "వినియోగదారు పేరు",
        "password":           "పాస్‌వర్డ్",
        "confirm_password":   "పాస్‌వర్డ్ నిర్ధారించండి",
        "email_optional":     "ఇమెయిల్ (ఐచ్ఛికం)",
        "create_account":     "ఖాతా తెరవండి",
        "welcome_back":       "తిరిగి స్వాగతం",
        "create_account_h":   "ఖాతా తెరవండి",
        "demo_hint":          "డెమో: సైన్ అప్‌లో ఖాతా తెరవండి, తర్వాత లాగిన్ చేయండి.",
        "passwords_no_match": "పాస్‌వర్డ్‌లు సరిపోలడం లేదు.",

        # Dashboard
        "greeting_morning":   "శుభోదయం",
        "greeting_afternoon": "నమస్కారం",
        "greeting_evening":   "శుభ సాయంత్రం",
        "medicines":          "మందులు",
        "todays_doses":       "నేటి మోతాదులు",
        "taken":              "తీసుకున్నవి",
        "missed":             "తప్పిపోయినవి",
        "adherence":          "అనుసరణ",
        "pending":            "పెండింగ్",
        "todays_overview":    "నేటి సారాంశం",
        "todays_schedule":    "నేటి షెడ్యూల్",
        "no_medicines_hint":  "నేటికి మందులు ప్లాన్ చేయబడలేదు. **మందు జోడించు** కి వెళ్ళండి.",
        "ai_tip":             "💡 ఏఐ సూచన",

        # Medicine form
        "add_new_medicine":   "➕ కొత్త మందు జోడించు",
        "edit_medicine":      "✏️ మందు సవరించు",
        "medicine_name":      "మందు పేరు *",
        "medicine_name_ph":   "ఉదా: పారాసెటమాల్",
        "dosage":             "మోతాదు *",
        "dosage_ph":          "ఉదా: 500mg, 10ml",
        "frequency":          "పౌనఃపున్యం *",
        "start_date":         "ప్రారంభ తేదీ",
        "set_end_date":       "ముగింపు తేదీ సెట్ చేయండి",
        "end_date":           "ముగింపు తేదీ",
        "dose_times":         "మోతాదు సమయాలు",
        "notes_optional":     "గమనికలు (ఐచ్ఛికం)",
        "notes_ph":           "ఉదా: భోజనంతో తీసుకోండి, మద్యం మానండి",
        "add_medicine_btn":   "➕ మందు జోడించు",
        "update_medicine_btn":"💾 మందు అప్‌డేట్ చేయి",
        "time_label":         "సమయం",
        "ai_explainer_title": "🤖 ఏఐ మందు వివరణ",
        "medicine_to_explain":"వివరించాల్సిన మందు",
        "explain_ph":         "ఉదా: మెట్‌ఫార్మిన్",
        "dosage_explain_ph":  "ఉదా: 500mg",
        "explain_btn":        "🤖 ఈ మందును వివరించండి",
        "configure_ai_hint":  "💡 మందు వివరణను ఎనేబుల్ చేయడానికి **ఏఐ సెట్టింగులు**లో ఏఐని కాన్ఫిగర్ చేయండి.",

        # My Medicines
        "my_medicines_h":     "💊 నా మందులు",
        "search_ph":          "పేరు లేదా మోతాదు టైప్ చేయండి…",
        "check_interactions": "🤖 ఇంటరాక్షన్స్ తనిఖీ",
        "no_medicines_yet":   "మీరు ఇంకా ఏ మందులూ జోడించలేదు. **మందు జోడించు** ఉపయోగించండి.",
        "frequency_label":    "పౌనఃపున్యం:",
        "times_label":        "సమయాలు:",
        "start_label":        "ప్రారంభం:",
        "end_label":          "ముగింపు:",
        "ongoing":            "కొనసాగుతోంది",
        "notes_label":        "గమనికలు:",
        "edit_btn":           "✏️ సవరించు",
        "delete_btn":         "🗑️ తొలగించు",
        "explain_btn_short":  "🤖 వివరించు",
        "suggest_schedule":   "📅 ఏఐ: సరైన షెడ్యూల్ సూచించు",
        "configure_ai_first": "ముందు **ఏఐ సెట్టింగులు**లో ఏఐ కాన్ఫిగర్ చేయండి.",

        # OCR
        "ocr_title":          "📷 ప్రిస్క్రిప్షన్ స్కానర్",
        "ocr_subtitle":       "ప్రిస్క్రిప్షన్ చిత్రం అప్‌లోడ్ చేయండి. OCR టెక్స్ట్ తీస్తుంది; ఏఐ మందులను పార్స్ చేయగలదు.",
        "upload_label":       "ప్రిస్క్రిప్షన్ చిత్రం అప్‌లోడ్ చేయండి",
        "upload_hint":        "స్పష్టమైన, మంచి వెలుతురు ఫోటోలు బాగా పని చేస్తాయి.",
        "upload_placeholder": "మందు వివరాలు తీయడానికి ప్రిస్క్రిప్షన్ చిత్రం అప్‌లోడ్ చేయండి",
        "uploaded_prescription":"అప్‌లోడ్ చేసిన ప్రిస్క్రిప్షన్",
        "extracted_info":     "తీయబడిన సమాచారం",
        "rule_medicines":     "🔵 నియమ-ఆధారిత మందులు:",
        "detected_dosages":   "🟡 గుర్తించబడిన మోతాదులు:",
        "medicine_lines":     "మందు వరుసలు",
        "full_text":          "📄 పూర్తి తీయబడిన టెక్స్ట్",
        "ai_enhanced_parse":  "🤖 ఏఐ మెరుగైన పార్స్",
        "ai_parse_btn":       "🤖 ఏఐ: ప్రిస్క్రిప్షన్ పార్స్ చేయి",
        "quick_add_label":    "➕ త్వరగా జోడించు (నియమ-ఆధారిత):",
        "select_medicine":    "మందు ఎంచుకోండి",
        "go_add_medicine":    "మందు జోడించుకు వెళ్ళు →",
        "ocr_tips":           "💡 **సూచనలు:**\n- అధిక రిజల్యూషన్ ఫోటో\n- మంచి వెలుతురు\n- అడ్డు టెక్స్ట్\n- నీడలు లేకుండా",

        # Analytics
        "analytics_title":    "📊 విశ్లేషణలు",
        "active_medicines":   "క్రియాశీల మందులు",
        "todays_adherence":   "నేటి అనుసరణ",
        "7day_adherence":     "7-రోజుల అనుసరణ",
        "7day_chart_title":   "7-రోజుల మోతాదు అనుసరణ",
        "todays_summary":     "నేటి సారాంశం",
        "by_frequency":       "పౌనఃపున్యం వారీగా మందులు",
        "weekly_breakdown":   "వారపు వివరాల పట్టిక",
        "date_col":           "తేదీ",
        "total_col":          "మొత్తం",
        "adherence_col":      "అనుసరణ %",
        "ai_coach_title":     "🤖 ఏఐ అనుసరణ కోచ్",
        "get_coaching":       "🤖 వ్యక్తిగత కోచింగ్ పొందండి",
        "configure_ai_coach": "అనుసరణ కోచ్ అన్‌లాక్ చేయడానికి **ఏఐ సెట్టింగులు**లో ఏఐ కాన్ఫిగర్ చేయండి.",

        # AI Assistant
        "ai_assistant_title": "🤖 ఏఐ సహాయకుడు",
        "ai_assistant_sub":   "మీ మందులు, షెడ్యూలు, దుష్ప్రభావాలు లేదా సాధారణ ఆరోగ్య ప్రశ్నల గురించి ఏదైనా అడగండి.",
        "configure_ai_first_long": "⚙️ దయచేసి ముందు **ఏఐ సెట్టింగులు**లో మీ ఏఐ ప్రొవైడర్ కాన్ఫిగర్ చేయండి.",
        "go_ai_settings":     "ఏఐ సెట్టింగులకు వెళ్ళు →",
        "quick_actions":      "త్వరిత చర్యలు:",
        "drug_interactions":  "🔬 మందు ఇంటరాక్షన్స్",
        "optimise_schedule":  "📅 షెడ్యూల్ ఆప్టిమైజ్ చేయి",
        "adherence_tips":     "📈 అనుసరణ చిట్కాలు",
        "clear_chat":         "🗑️ చాట్ క్లియర్ చేయి",
        "you":                "మీరు",
        "ai":                 "ఏఐ",
        "ask_placeholder":    "ఉదా: మెట్‌ఫార్మిన్‌తో ఇబుప్రోఫెన్ తీసుకోవచ్చా?",
        "include_meds":       "నా మందుల జాబితాను సందర్భంగా చేర్చండి",
        "send_btn":           "పంపు 📤",
        "ai_thinking":        "ఏఐ ఆలోచిస్తోంది…",

        # AI Settings
        "ai_settings_title":  "⚙️ ఏఐ సెట్టింగులు",
        "ai_settings_sub":    "మీకు నచ్చిన ఏఐ బ్యాకెండ్ కాన్ఫిగర్ చేయండి. అన్ని కీలు మీ బ్రౌజర్ సెషన్‌లో మాత్రమే నిల్వ చేయబడతాయి.",
        "ai_provider_label":  "ఏఐ ప్రొవైడర్",
        "select_provider":    "ప్రొవైడర్ ఎంచుకోండి",
        "test_connection":    "🔍 కనెక్షన్ పరీక్షించు",
        "test_api_key":       "🔍 API కీ పరీక్షించు",
        "ollama_url":         "Ollama బేస్ URL",
        "select_model":       "మోడల్ ఎంచుకోండి",
        "api_key_label":      "API కీ",
        "privacy_note":       "🔒 **గోప్యత:** API కీలు మీ Streamlit సెషన్‌లో మాత్రమే నిల్వ చేయబడతాయి. అవి డిస్క్‌లో సేవ్ కాదు.",

        # Dose actions
        "mark_taken":         "✅ తీసుకున్నాను",
        "undo_taken":         "↩ రద్దు చేయి",
        "status_taken":       "తీసుకున్నారు",
        "status_missed":      "తప్పిపోయింది",
        "status_pending":     "పెండింగ్",

        # AI status
        "ai_status_running":  "నడుస్తోంది",
        "ai_status_offline":  "ఆఫ్‌లైన్",
        "ai_status_ready":    "సిద్ధంగా ఉంది",
        "ai_status_no_key":   "(కీ లేదు)",

        # Misc
        "search_label":       "🔍 మందులు వెతకండి",
        "no_dose_data":       "గత 7 రోజులకు మోతాదు డేటా లేదు.",
        "no_medicines_data":  "ఇంకా మందులు జోడించలేదు.",
        "language_label":     "🌐 భాష",
        "ai_found":           "ఏఐ కనుగొంది",
        "medicines_word":     "మందు(లు)!",
    },
}

# Language selector display names (for dropdown)
LANGUAGE_OPTIONS = {
    "en": "🇬🇧 English",
    "hi": "🇮🇳 हिन्दी",
    "te": "🇮🇳 తెలుగు",
}


def get_text(lang: str, key: str, fallback: str = "") -> str:
    """
    Safe accessor - returns the string for *key* in *lang*,
    falling back to English, then to *fallback*.
    """
    return (
        LANGUAGES.get(lang, {}).get(key)
        or LANGUAGES["en"].get(key)
        or fallback
        or key
    )