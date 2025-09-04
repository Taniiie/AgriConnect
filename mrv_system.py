import sqlite3
import hashlib
from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# --- Database Setup ---
# This function is executed once when the application starts up
def setup_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Call the setup function immediately
setup_database()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# --- Security Functions ---
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def check_password(hashed_password, user_password):
    return hashed_password == hash_password(user_password)

# --- API Endpoints ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AgriConnect</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {
                font-family: 'Inter', sans-serif;
            }
            .bg-green-600 { background-color: #059669; }
            .bg-green-700 { background-color: #047857; }
            .text-green-500 { color: #10B981; }
            .border-green-500 { border-color: #10B981; }
            .modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                display: none;
                justify-content: center;
                align-items: center;
                z-index: 1000;
            }
            .modal-content {
                background-color: white;
                padding: 2rem;
                border-radius: 0.5rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                max-width: 90%;
                text-align: center;
                max-height: 80%;
                overflow-y: auto;
            }
        </style>
    </head>
    <body class="bg-gray-100 font-sans leading-normal tracking-normal">
        <!-- Main Application Content (Initially Hidden) -->
        <div id="mainApp" class="hidden">
            <div class="container mx-auto p-4 md:p-8">
                <header class="text-center py-6 bg-green-600 text-white rounded-lg shadow-lg flex flex-col md:flex-row justify-between items-center px-6">
                    <div class="md:text-left mb-4 md:mb-0">
                        <h1 class="text-3xl md:text-4xl font-bold" data-translate-key="appTitle">AgriConnect for Smallholder Agriculture</h1>
                        <p class="mt-2 text-sm md:text-base opacity-90" data-translate-key="appSubtitle">A NABARD Hackathon Solution</p>
                    </div>
                    <div class="flex flex-col md:flex-row items-center gap-4">
                        <select id="languageSelect" class="bg-white text-gray-800 rounded-md p-2">
                            <option value="en">English</option>
                            <option value="hi">हिन्दी (Hindi)</option>
                            <option value="ta">தமிழ் (Tamil)</option>
                            <option value="te">తెలుగు (Telugu)</option>
                            <option value="ml">മലയാളം (Malayalam)</option>
                        </select>
                        <button id="logoutBtn" class="px-4 py-2 bg-red-500 text-white rounded-md font-semibold hover:bg-red-600 transition-colors duration-300" data-translate-key="logoutBtn">
                            Logout
                        </button>
                    </div>
                </header>

                <main class="mt-8 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    <!-- Section 1: Data Collection -->
                    <section class="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300">
                        <h2 class="text-xl font-semibold text-green-700" data-translate-key="dataCollectionTitle">1. Data Collection</h2>
                        <p class="mt-4 text-gray-600" data-translate-key="dataCollectionText">
                            Easily collect field data on a mobile device. Record crop type, planting dates, and climate-smart practices.
                        </p>
                        <button id="addDataBtn" class="mt-4 px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors duration-300" data-translate-key="addDataBtn">
                            Add New Entry
                        </button>
                    </section>

                    <!-- Section 2: Reporting -->
                    <section class="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300">
                        <h2 class="text-xl font-semibold text-green-700" data-translate-key="reportingTitle">2. Real-time Reporting</h2>
                        <p class="mt-4 text-gray-600" data-translate-key="reportingText">
                            Generate comprehensive reports on carbon sequestration and sustainability metrics automatically.
                        </p>
                        <button id="viewReportsBtn" class="mt-4 px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors duration-300" data-translate-key="viewReportsBtn">
                            View Reports
                        </button>
                    </section>

                    <!-- Section 3: Verification -->
                    <section class="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300">
                        <h2 class="text-xl font-semibold text-green-700" data-translate-key="verificationTitle">3. Efficient Verification</h2>
                        <p class="mt-4 text-gray-600" data-translate-key="verificationText">
                            Streamline the verification process with geotagged data and a secure, transparent record-keeping system.
                        </p>
                        <button id="startVerificationBtn" class="mt-4 px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors duration-300" data-translate-key="startVerificationBtn">
                            Start Verification
                        </button>
                    </section>
                </main>

                <footer class="mt-8 text-center text-gray-500">
                    &copy; 2025 NABARD Hackathon. Powered by Tech-enabled Climate Action.
                </footer>
            </div>
        </div>

        <!-- Authentication Page (Visible initially) -->
        <div id="authPage" class="flex flex-col items-center justify-center min-h-screen bg-green-700 text-white">
            <div class="bg-white text-gray-800 p-8 rounded-lg shadow-lg w-full max-w-sm">
                <h1 class="text-3xl font-bold text-center mb-6 text-green-700" data-translate-key="appTitle">AgriConnect</h1>
                <h2 id="authTitle" class="text-2xl font-bold text-center mb-6 text-green-700" data-translate-key="signInTitle">Sign In</h2>
                <form id="authForm" class="flex flex-col gap-4">
                    <input type="text" id="username" data-translate-placeholder="usernamePlaceholder" placeholder="Username" required class="p-3 border border-gray-300 rounded-md">
                    <input type="password" id="password" data-translate-placeholder="passwordPlaceholder" placeholder="Password" required class="p-3 border border-gray-300 rounded-md">
                    <button type="submit" id="authBtn" class="px-4 py-3 bg-green-500 text-white rounded-md font-semibold hover:bg-green-600 transition-colors duration-300" data-translate-key="signInBtn">
                        Sign In
                    </button>
                </form>
                <div class="mt-4 text-center text-sm">
                    <span id="toggleText" data-translate-key="toggleSignInText">Don't have an account?</span>
                    <a href="#" id="toggleAuth" class="font-semibold text-green-700 hover:underline ml-1" data-translate-key="toggleSignInLink">Sign Up</a>
                </div>
                <div id="authMessage" class="mt-4 text-center text-sm text-red-500"></div>
            </div>
        </div>

        <!-- All existing modals are now inside the mainApp div to be hidden/shown with it -->
        <div id="modalsContainer">
            <!-- The Modal/Message Box for general messages -->
            <div id="modal" class="modal">
                <div class="modal-content">
                    <p id="modal-message" class="text-lg font-semibold text-gray-800"></p>
                    <button id="closeModalBtn" class="mt-4 px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors duration-300" data-translate-key="closeBtn">
                        Close
                    </button>
                </div>
            </div>

            <!-- The Modal for Data Entry -->
            <div id="dataEntryModal" class="modal">
                <div class="modal-content">
                    <h3 class="text-xl font-semibold text-green-700 mb-4" data-translate-key="addDataModalTitle">Add a New Data Entry</h3>
                    <form id="dataEntryForm" class="flex flex-col gap-4">
                        <input type="text" id="cropName" data-translate-placeholder="cropNamePlaceholder" placeholder="Crop Name" required class="p-2 border border-gray-300 rounded-md">
                        <input type="number" id="saplingCount" data-translate-placeholder="saplingCountPlaceholder" placeholder="Number of Saplings" required class="p-2 border border-gray-300 rounded-md">
                        <div class="flex justify-end gap-2 mt-4">
                            <button type="button" id="closeDataEntryBtn" class="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors duration-300" data-translate-key="cancelBtn">
                                Cancel
                            </button>
                            <button type="submit" class="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors duration-300" data-translate-key="submitEntryBtn">
                                Submit Entry
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <!-- The Modal for Real-time Reports -->
            <div id="reportsModal" class="modal">
                <div class="modal-content w-full md:w-2/3 lg:w-1/2">
                    <h3 class="text-2xl font-semibold text-green-700 mb-6" data-translate-key="reportsModalTitle">Real-time Reports</h3>
                    <div id="reportsList" class="flex flex-col gap-4">
                        <!-- Reports will be dynamically generated here -->
                    </div>
                    <button id="closeReportsBtn" class="mt-6 px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors duration-300" data-translate-key="closeBtn">
                        Close
                    </button>
                </div>
            </div>

            <!-- The Modal for Verification -->
            <div id="verificationModal" class="modal">
                <div class="modal-content">
                    <h3 class="text-2xl font-semibold text-green-700 mb-6" data-translate-key="verificationModalTitle">Verification Checklist</h3>
                    <ul class="text-left mb-6 space-y-2 text-gray-700">
                        <li class="flex items-center"><span class="w-5 h-5 inline-block mr-2 text-green-500">&#10003;</span> <span data-translate-key="verificationStep1">Review Geotagged Data</span></li>
                        <li class="flex items-center"><span class="w-5 h-5 inline-block mr-2 text-green-500">&#10003;</span> <span data-translate-key="verificationStep2">Cross-reference with Satellite Imagery</span></li>
                        <li class="flex items-center"><span class="w-5 h-5 inline-block mr-2 text-green-500">&#10003;</span> <span data-translate-key="verificationStep3">Confirm Farmer Identification</span></li>
                        <li class="flex items-center"><span class="w-5 h-5 inline-block mr-2 text-green-500">&#10003;</span> <span data-translate-key="verificationStep4">Validate Sustainability Practices</span></li>
                    </ul>
                    <button id="simulateVerificationBtn" class="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors duration-300" data-translate-key="simulateVerificationBtn">
                        Simulate Verification
                    </button>
                    <button id="closeVerificationBtn" class="mt-4 px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors duration-300" data-translate-key="cancelBtn">
                        Cancel
                    </button>
                </div>
            </div>

            <!-- The Modal for Verification Progress -->
            <div id="verificationProgressModal" class="modal">
                <div class="modal-content">
                    <h3 class="text-2xl font-semibold text-green-700 mb-6" data-translate-key="verificationProgressTitle">Verification in Progress...</h3>
                    <ul id="verificationSteps" class="text-left mb-6 space-y-4 text-gray-700">
                        <li id="step1"><span data-translate-key="verificationProgressStep1">Reviewing Geotagged Data...</span> <span class="status-icon">⏳</span></li>
                        <li id="step2"><span data-translate-key="verificationProgressStep2">Cross-referencing Satellite Imagery...</span> <span class="status-icon">⏳</span></li>
                        <li id="step3"><span data-translate-key="verificationProgressStep3">Confirming Farmer Identification...</span> <span class="status-icon">⏳</span></li>
                        <li id="step4"><span data-translate-key="verificationProgressStep4">Validating Sustainability Practices...</span> <span class="status-icon">⏳</span></li>
                    </ul>
                    <div id="finalMessage" class="hidden">
                        <p class="text-lg font-semibold text-green-600" data-translate-key="verificationCompleteMessage">Verification complete! Records are verified and secured on the blockchain.</p>
                        <button id="closeVerificationProgressBtn" class="mt-4 px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors duration-300" data-translate-key="closeBtn">
                            Close
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // --- Translations ---
            const translations = {
                en: {
                    appTitle: 'AgriConnect for Smallholder Agriculture',
                    appSubtitle: 'A NABARD Hackathon Solution',
                    logoutBtn: 'Logout',
                    dataCollectionTitle: '1. Data Collection',
                    dataCollectionText: 'Easily collect field data on a mobile device. Record crop type, planting dates, and climate-smart practices.',
                    addDataBtn: 'Add New Entry',
                    reportingTitle: '2. Real-time Reporting',
                    reportingText: 'Generate comprehensive reports on carbon sequestration and sustainability metrics automatically.',
                    viewReportsBtn: 'View Reports',
                    verificationTitle: '3. Efficient Verification',
                    verificationText: 'Streamline the verification process with geotagged data and a secure, transparent record-keeping system.',
                    startVerificationBtn: 'Start Verification',
                    signInTitle: 'Sign In',
                    signInBtn: 'Sign In',
                    toggleSignInText: "Don't have an account?",
                    toggleSignInLink: 'Sign Up',
                    signUpTitle: 'Sign Up',
                    signUpBtn: 'Sign Up',
                    toggleSignUpText: 'Already have an account?',
                    toggleSignUpLink: 'Sign In',
                    closeBtn: 'Close',
                    cancelBtn: 'Cancel',
                    addDataModalTitle: 'Add a New Data Entry',
                    submitEntryBtn: 'Submit Entry',
                    reportsModalTitle: 'Real-time Reports',
                    verificationModalTitle: 'Verification Checklist',
                    verificationStep1: 'Review Geotagged Data',
                    verificationStep2: 'Cross-reference with Satellite Imagery',
                    verificationStep3: 'Confirm Farmer Identification',
                    verificationStep4: 'Validate Sustainability Practices',
                    simulateVerificationBtn: 'Simulate Verification',
                    verificationProgressTitle: 'Verification in Progress...',
                    verificationProgressStep1: 'Reviewing Geotagged Data...',
                    verificationProgressStep2: 'Cross-referencing Satellite Imagery...',
                    verificationProgressStep3: 'Confirming Farmer Identification...',
                    verificationProgressStep4: 'Validating Sustainability Practices...',
                    verificationCompleteMessage: 'Verification complete! Records are verified and secured on the blockchain.',
                    modalSignUpSuccess: 'Sign up successful! Please sign in with your new credentials.',
                    modalDataSuccess: 'Data submitted successfully! Thanks for your contribution.',
                    modalFillFields: 'Please fill out all fields.',
                    usernamePlaceholder: 'Username',
                    passwordPlaceholder: 'Password',
                    cropNamePlaceholder: 'Crop Name',
                    saplingCountPlaceholder: 'Number of Saplings'
                },
                hi: {
                    appTitle: 'छोटे किसानों के लिए एग्रीकनेक्ट',
                    appSubtitle: 'नाबार्ड हैकाथॉन समाधान',
                    logoutBtn: 'लॉग आउट',
                    dataCollectionTitle: '1. डेटा संग्रह',
                    dataCollectionText: 'मोबाइल डिवाइस पर आसानी से फ़ील्ड डेटा एकत्र करें। फसल का प्रकार, रोपण की तारीखें, और जलवायु-स्मार्ट प्रथाओं को रिकॉर्ड करें।',
                    addDataBtn: 'नई प्रविष्टि जोड़ें',
                    reportingTitle: '2. रियल-टाइम रिपोर्टिंग',
                    reportingText: 'कार्बन पृथक्करण और स्थिरता मेट्रिक्स पर स्वचालित रूप से व्यापक रिपोर्ट तैयार करें।',
                    viewReportsBtn: 'रिपोर्ट देखें',
                    verificationTitle: '3. कुशल सत्यापन',
                    verificationText: 'जियोटैग किए गए डेटा और एक सुरक्षित, पारदर्शी रिकॉर्ड-कीपिंग प्रणाली के साथ सत्यापन प्रक्रिया को सुव्यवस्थित करें।',
                    startVerificationBtn: 'सत्यापन शुरू करें',
                    signInTitle: 'साइन इन करें',
                    signInBtn: 'साइन इन करें',
                    toggleSignInText: 'खाता नहीं है?',
                    toggleSignInLink: 'साइन अप करें',
                    signUpTitle: 'साइन अप करें',
                    signUpBtn: 'साइन अप करें',
                    toggleSignUpText: 'पहले से ही एक खाता है?',
                    toggleSignUpLink: 'साइन इन करें',
                    closeBtn: 'बंद करें',
                    cancelBtn: 'रद्द करें',
                    addDataModalTitle: 'एक नई डेटा प्रविष्टि जोड़ें',
                    submitEntryBtn: 'प्रविष्टि जमा करें',
                    reportsModalTitle: 'रियल-टाइम रिपोर्ट',
                    verificationModalTitle: 'सत्यापन चेकलिस्ट',
                    verificationStep1: 'जियोटैग किए गए डेटा की समीक्षा करें',
                    verificationStep2: 'उपग्रह इमेजरी के साथ क्रॉस-रेफरेंस करें',
                    verificationStep3: 'किसान की पहचान की पुष्टि करें',
                    verificationStep4: 'स्थिरता प्रथाओं को मान्य करें',
                    simulateVerificationBtn: 'सत्यापन का अनुकरण करें',
                    verificationProgressTitle: 'सत्यापन प्रगति पर है...',
                    verificationProgressStep1: 'जियोटैग किए गए डेटा की समीक्षा कर रहा है...',
                    verificationProgressStep2: 'उपग्रह इमेजरी के साथ क्रॉस-रेफरेंस कर रहा है...',
                    verificationProgressStep3: 'किसान की पहचान की पुष्टि कर रहा है...',
                    verificationProgressStep4: 'स्थिरता प्रथाओं को मान्य कर रहा है...',
                    verificationCompleteMessage: 'सत्यापन पूरा हुआ! रिकॉर्ड सत्यापित हैं और ब्लॉकचेन पर सुरक्षित हैं।',
                    modalSignUpSuccess: 'साइन अप सफल! कृपया अपने नए क्रेडेंशियल्स के साथ साइन इन करें।',
                    modalDataSuccess: 'डेटा सफलतापूर्वक जमा किया गया! आपके योगदान के लिए धन्यवाद।',
                    modalFillFields: 'कृपया सभी फ़ील्ड भरें।',
                    usernamePlaceholder: 'उपयोगकर्ता नाम',
                    passwordPlaceholder: 'पासवर्ड',
                    cropNamePlaceholder: 'फसल का नाम',
                    saplingCountPlaceholder: 'पौधों की संख्या'
                },
                ta: {
                    appTitle: 'சிறு விவசாயிகளுக்கான அக்ரிகனெக்ட்',
                    appSubtitle: 'ஒரு நபார்டு ஹேக்கத்தான் தீர்வு',
                    logoutBtn: 'வெளியேறு',
                    dataCollectionTitle: '1. தரவு சேகரிப்பு',
                    dataCollectionText: 'மொபைல் சாதனத்தில் புலம் சார்ந்த தரவுகளை எளிதாக சேகரிக்கவும். பயிர் வகை, நடவு தேதிகள் மற்றும் காலநிலை-திறன்மிக்க நடைமுறைகளை பதிவு செய்யவும்.',
                    addDataBtn: 'புதிய பதிவைச் சேர்',
                    reportingTitle: '2. நிகழ்நேர அறிக்கை',
                    reportingText: 'கார்பன் பிரித்தெடுத்தல் மற்றும் நிலைத்தன்மை அளவீடுகள் குறித்து விரிவான அறிக்கைகளை தானாக உருவாக்கவும்.',
                    viewReportsBtn: 'அறிக்கைகளைப் பார்க்கவும்',
                    verificationTitle: '3. திறமையான சரிபார்ப்பு',
                    verificationText: 'புவிக்குறியிடப்பட்ட தரவு மற்றும் பாதுகாப்பான, வெளிப்படையான பதிவேட்டு அமைப்புடன் சரிபார்ப்பு செயல்முறையை மேம்படுத்தவும்.',
                    startVerificationBtn: 'சரிபார்ப்பை தொடங்கு',
                    signInTitle: 'உள்நுழைக',
                    signInBtn: 'உள்நுழைக',
                    toggleSignInText: 'கணக்கு இல்லையா?',
                    toggleSignInLink: 'பதிவு செய்க',
                    signUpTitle: 'பதிவு செய்க',
                    signUpBtn: 'பதிவு செய்க',
                    toggleSignUpText: 'ஏற்கனவே ஒரு கணக்கு உள்ளதா?',
                    toggleSignUpLink: 'உள்நுழைக',
                    closeBtn: 'மூடு',
                    cancelBtn: 'ரத்து செய்',
                    addDataModalTitle: 'புதிய தரவு பதிவைச் சேர்க்கவும்',
                    submitEntryBtn: 'பதிவைச் சமர்ப்பி',
                    reportsModalTitle: 'நிகழ்நேர அறிக்கைகள்',
                    verificationModalTitle: 'சரிபார்ப்பு சரிபார்ப்புப் பட்டியல்',
                    verificationStep1: 'புவிக்குறியிடப்பட்ட தரவை மதிப்பாய்வு செய்யவும்',
                    verificationStep2: 'செயற்கைக்கோள் படத்துடன் குறுக்கு-சரிபார்ப்பு',
                    verificationStep3: 'விவசாயி அடையாளத்தை உறுதிப்படுத்தவும்',
                    verificationStep4: 'நிலைத்தன்மை நடைமுறைகளை சரிபார்க்கவும்',
                    simulateVerificationBtn: 'சரிபார்ப்பை உருவகப்படுத்து',
                    verificationProgressTitle: 'சரிபார்ப்பு முன்னேறி வருகிறது...',
                    verificationProgressStep1: 'புவிக்குறியிடப்பட்ட தரவை மதிப்பாய்வு செய்கிறது...',
                    verificationProgressStep2: 'செயற்கைக்கோள் படத்துடன் குறுக்கு-சரிபார்ப்பு செய்கிறது...',
                    verificationProgressStep3: 'விவசாயி அடையாளத்தை உறுதிப்படுத்துகிறது...',
                    verificationProgressStep4: 'நிலைத்தன்மை நடைமுறைகளை சரிபார்க்கிறது...',
                    verificationCompleteMessage: 'சரிபார்ப்பு முடிந்தது! பதிவுகள் சரிபார்க்கப்பட்டு பிளாக்செயினில் பாதுகாக்கப்பட்டுள்ளன.',
                    modalSignUpSuccess: 'பதிவு வெற்றிகரமாக முடிந்தது! உங்கள் புதிய சான்றுகளுடன் உள்நுழையவும்.',
                    modalDataSuccess: 'தரவு வெற்றிகரமாக சமர்ப்பிக்கப்பட்டது! உங்கள் பங்களிப்புக்கு நன்றி.',
                    modalFillFields: 'தயவுசெய்து அனைத்து புலங்களையும் நிரப்பவும்.',
                    usernamePlaceholder: 'பயனர் பெயர்',
                    passwordPlaceholder: 'கடவுச்சொல்',
                    cropNamePlaceholder: 'பயிர் பெயர்',
                    saplingCountPlaceholder: 'செடிகளின் எண்ணிக்கை'
                },
                te: {
                    appTitle: 'చిన్న కమతాల వ్యవసాయం కోసం అగ్రి కనెక్ట్',
                    appSubtitle: 'ఒక నాబార్డ్ హ్యాకథాన్ పరిష్కారం',
                    logoutBtn: 'నిష్క్రమించు',
                    dataCollectionTitle: '1. డేటా సేకరణ',
                    dataCollectionText: 'మొబైల్ పరికరంలో ఫీల్డ్ డేటాను సులభంగా సేకరించండి. పంట రకం, నాటడం తేదీలు మరియు వాతావరణ-స్మార్ట్ పద్ధతులను రికార్డ్ చేయండి.',
                    addDataBtn: 'కొత్త ఎంట్రీని జోడించు',
                    reportingTitle: '2. రియల్-టైమ్ రిపోర్టింగ్',
                    reportingText: 'కార్బన్ సీక్వెస్ట్రేషన్ మరియు సుస్థిరత కొలమానాలపై సమగ్ర నివేదికలను స్వయంచాలకంగా రూపొందించండి.',
                    viewReportsBtn: 'నివేదికలను వీక్షించు',
                    verificationTitle: '3. సమర్థవంతమైన ధృవీకరణ',
                    verificationText: 'జియోట్యాగ్ చేయబడిన డేటా మరియు సురక్షితమైన, పారదర్శక రికార్డ్-కీపింగ్ సిస్టమ్‌తో ధృవీకరణ ప్రక్రియను క్రమబద్ధీకరించండి.',
                    startVerificationBtn: 'ధృవీకరణ ప్రారంభించండి',
                    signInTitle: 'సైన్ ఇన్ చేయండి',
                    signInBtn: 'సైన్ ఇన్ చేయండి',
                    toggleSignInText: 'ఖాతా లేదా?',
                    toggleSignInLink: 'సైన్ అప్ చేయండి',
                    signUpTitle: 'సైన్ అప్ చేయండి',
                    signUpBtn: 'సైన్ అప్ చేయండి',
                    toggleSignUpText: 'ఖాతా ఇప్పటికే ఉందా?',
                    toggleSignUpLink: 'సైన్ ఇన్ చేయండి',
                    closeBtn: 'మూసివేయి',
                    cancelBtn: 'రద్దు చేయండి',
                    addDataModalTitle: 'కొత్త డేటా ఎంట్రీని జోడించండి',
                    submitEntryBtn: 'ఎంట్రీని సమర్పించండి',
                    reportsModalTitle: 'రియల్-టైమ్ నివేదికలు',
                    verificationModalTitle: 'ధృవీకరణ చెక్‌లిస్ట్',
                    verificationStep1: 'జియోట్యాగ్ చేయబడిన డేటాను సమీక్షించండి',
                    verificationStep2: 'ఉపగ్రహ చిత్రణతో క్రాస్-రిఫరెన్స్ చేయండి',
                    verificationStep3: 'రైతు గుర్తింపును నిర్ధారించండి',
                    verificationStep4: 'సుస్థిరత పద్ధతులను ధృవీకరించండి',
                    simulateVerificationBtn: 'ధృవీకరణను అనుకరించండి',
                    verificationProgressTitle: 'ధృవీకరణ పురోగతిలో ఉంది...',
                    verificationProgressStep1: 'జియోట్యాగ్ చేయబడిన డేటాను సమీక్షిస్తోంది...',
                    verificationProgressStep2: 'ఉపగ్రహ చిత్రణతో క్రాస్-రిఫరెన్స్ చేస్తోంది...',
                    verificationProgressStep3: 'రైతు గుర్తింపును నిర్ధారిస్తోంది...',
                    verificationProgressStep4: 'సుస్థిరత పద్ధతులను ధృవీకరిస్తోంది...',
                    verificationCompleteMessage: 'ధృవీకరణ పూర్తయింది! రికార్డులు ధృవీకరించబడ్డాయి మరియు బ్లాక్‌చెయిన్‌లో భద్రపరచబడ్డాయి.',
                    modalSignUpSuccess: 'సైన్ అప్ విజయవంతమైంది! దయచేసి మీ కొత్త ఆధారాలతో సైన్ ఇన్ చేయండి.',
                    modalDataSuccess: 'డేటా విజయవంతంగా సమర్పించబడింది! మీ సహకారానికి ధన్యవాదాలు.',
                    modalFillFields: 'దయచేసి అన్ని ఖాళీలను పూరించండి।',
                    usernamePlaceholder: 'వినియోగదారు పేరు',
                    passwordPlaceholder: 'పాస్వర్డ్',
                    cropNamePlaceholder: 'పంట పేరు',
                    saplingCountPlaceholder: 'మొక్కల సంఖ్య'
                },
                ml: {
                    appTitle: 'ചെറുകിട കർഷകർക്കായി അഗ്രികണക്റ്റ്',
                    appSubtitle: 'ഒരു നബാർഡ് ഹാക്കത്തൺ പരിഹാരം',
                    logoutBtn: 'ലോഗൗട്ട് ചെയ്യുക',
                    dataCollectionTitle: '1. ഡാറ്റ ശേഖരണം',
                    dataCollectionText: 'മൊബൈൽ ഉപകരണത്തിൽ ഫീൽഡ് ഡാറ്റ എളുപ്പത്തിൽ ശേഖരിക്കുക. വിള തരം, നടീൽ തീയതികൾ, കാലാവസ്ഥാ-സ്മാർട്ട് രീതികൾ എന്നിവ രേഖപ്പെടുത്തുക.',
                    addDataBtn: 'പുതിയ എൻട്രി ചേർക്കുക',
                    reportingTitle: '2. തത്സമയ റിപ്പോർട്ടിംഗ്',
                    reportingText: 'കാർബൺ സീക്വസ്ട്രേഷൻ, സുസ്ഥിരതാ അളവുകൾ എന്നിവയെക്കുറിച്ചുള്ള സമഗ്ര റിപ്പോർട്ടുകൾ സ്വയമേവ സൃഷ്ടിക്കുക.',
                    viewReportsBtn: 'റിപ്പോർട്ടുകൾ കാണുക',
                    verificationTitle: '3. കാര്യക്ഷമമായ പരിശോധന',
                    verificationText: 'ജിയോടാഗ് ചെയ്ത ഡാറ്റയും സുരക്ഷിതവും സുതാര്യവുമായ റെക്കോർഡ്-കീപ്പിംഗ് സംവിധാനവും ഉപയോഗിച്ച് പരിശോധന പ്രക്രിയ കാര്യക്ഷമമാക്കുക.',
                    startVerificationBtn: 'പരിശോധന ആരംഭിക്കുക',
                    signInTitle: 'സൈൻ ഇൻ ചെയ്യുക',
                    signInBtn: 'സൈൻ ഇൻ ചെയ്യുക',
                    toggleSignInText: 'അക്കൗണ്ട് ഇല്ലേ?',
                    toggleSignInLink: 'സൈൻ അപ്പ് ചെയ്യുക',
                    signUpTitle: 'സൈൻ അപ്പ് ചെയ്യുക',
                    signUpBtn: 'സൈൻ അപ്പ് ചെയ്യുക',
                    toggleSignUpText: 'നിങ്ങൾക്ക് ഇതിനകം ഒരു അക്കൗണ്ട് ഉണ്ടോ?',
                    toggleSignUpLink: 'സൈൻ ഇൻ ചെയ്യുക',
                    closeBtn: 'അടയ്ക്കുക',
                    cancelBtn: 'റദ്ദാക്കുക',
                    addDataModalTitle: 'ഒരു പുതിയ ഡാറ്റ എൻട്രി ചേർക്കുക',
                    submitEntryBtn: 'എൻട്രി സമർപ്പിക്കുക',
                    reportsModalTitle: 'തത്സമയ റിപ്പോർട്ടുകൾ',
                    verificationModalTitle: 'പരിശോധന ചെക്ക്‌ലിസ്റ്റ്',
                    verificationStep1: 'ജിയോടാഗ് ചെയ്ത ഡാറ്റ അവലോകനം ചെയ്യുക',
                    verificationStep2: 'സാറ്റലൈറ്റ് ചിത്രങ്ങളുമായി ക്രോസ്-റെഫറൻസ് ചെയ്യുക',
                    verificationStep3: 'കർഷകന്റെ തിരിച്ചറിയൽ സ്ഥിരീകരിക്കുക',
                        verificationStep4: 'സുസ്ഥിരതാ രീതികൾ സാധൂകരിക്കുക',
                    simulateVerificationBtn: 'പരിശോധന അനുകരിക്കുക',
                    verificationProgressTitle: 'പരിശോധന പുരോഗമിക്കുന്നു...',
                    verificationProgressStep1: 'ജിയോടാഗ് ചെയ്ത ഡാറ്റ അവലോകനം ചെയ്യുന്നു...',
                    verificationProgressStep2: 'സാറ്റലൈറ്റ് ചിത്രങ്ങളുമായി ക്രോസ്-റെഫറൻസ് ചെയ്യുന്നു...',
                    verificationProgressStep3: 'കർഷകന്റെ തിരിച്ചറിയൽ സ്ഥിരീകരിക്കുന്നു...',
                    verificationProgressStep4: 'സുസ്ഥിരതാ രീതികൾ സാധൂകരിക്കുന്നു...',
                    verificationCompleteMessage: 'പരിശോധന പൂർത്തിയായി! രേഖകൾ ബ്ലോക്ക്ചെയിനിൽ പരിശോധിച്ച് സുരക്ഷിതമാക്കിയിരിക്കുന്നു.',
                    modalSignUpSuccess: 'സൈൻ അപ്പ് വിജയകരമായി! നിങ്ങളുടെ പുതിയ ക്രെഡൻഷ്യലുകൾ ഉപയോഗിച്ച് സൈൻ ഇൻ ചെയ്യുക.',
                    modalDataSuccess: 'ഡാറ്റ വിജയകരമായി സമർപ്പിച്ചു! നിങ്ങളുടെ സംഭാവനയ്ക്ക് നന്ദി.',
                    modalFillFields: 'എല്ലാ ഫീൽഡുകളും പൂരിപ്പിക്കുക.',
                    usernamePlaceholder: 'ഉപയോക്തൃനാമം',
                    passwordPlaceholder: 'പാസ്‌വേഡ്',
                    cropNamePlaceholder: 'വിളയുടെ പേര്',
                    saplingCountPlaceholder: 'തൈകളുടെ എണ്ണം'
                }
            };

            const languageSelect = document.getElementById('languageSelect');
            const authPage = document.getElementById('authPage');
            const authTitle = document.getElementById('authTitle');
            const authForm = document.getElementById('authForm');
            const usernameInput = document.getElementById('username');
            const passwordInput = document.getElementById('password');
            const authBtn = document.getElementById('authBtn');
            const toggleAuth = document.getElementById('toggleAuth');
            const toggleText = document.getElementById('toggleText');
            const authMessage = document.getElementById('authMessage');
            const mainApp = document.getElementById('mainApp');
            const logoutBtn = document.getElementById('logoutBtn');
            const modal = document.getElementById('modal');
            const modalMessage = document.getElementById('modal-message');
            const closeModalBtn = document.getElementById('closeModalBtn');
            const addDataBtn = document.getElementById('addDataBtn');
            const viewReportsBtn = document.getElementById('viewReportsBtn');
            const startVerificationBtn = document.getElementById('startVerificationBtn');
            const dataEntryModal = document.getElementById('dataEntryModal');
            const closeDataEntryBtn = document.getElementById('closeDataEntryBtn');
            const dataEntryForm = document.getElementById('dataEntryForm');
            const cropNameInput = document.getElementById('cropName');
            const saplingCountInput = document.getElementById('saplingCount');
            const reportsModal = document.getElementById('reportsModal');
            const reportsList = document.getElementById('reportsList');
            const closeReportsBtn = document.getElementById('closeReportsBtn');
            const verificationModal = document.getElementById('verificationModal');
            const closeVerificationBtn = document.getElementById('closeVerificationBtn');
            const simulateVerificationBtn = document.getElementById('simulateVerificationBtn');
            const verificationProgressModal = document.getElementById('verificationProgressModal');
            const verificationSteps = document.getElementById('verificationSteps');
            const finalMessage = document.getElementById('finalMessage');
            const closeVerificationProgressBtn = document.getElementById('closeVerificationProgressBtn');

            let isSignUp = false;

            function translatePage(lang) {
                // Translate text content
                const elements = document.querySelectorAll('[data-translate-key]');
                elements.forEach(el => {
                    const key = el.getAttribute('data-translate-key');
                    if (translations[lang] && translations[lang][key]) {
                        el.textContent = translations[lang][key];
                    }
                });

                // Translate placeholder text
                const placeholders = document.querySelectorAll('[data-translate-placeholder]');
                placeholders.forEach(el => {
                    const key = el.getAttribute('data-translate-placeholder');
                    if (translations[lang] && translations[lang][key]) {
                        el.placeholder = translations[lang][key];
                    }
                });
            }

            function showModal(key, type = 'success') {
                const lang = languageSelect.value;
                let message = translations[lang][key];
                modalMessage.textContent = message;
                modal.style.display = 'flex';
            }

            function hideModal(targetModal) {
                targetModal.style.display = 'none';
            }

            languageSelect.addEventListener('change', (e) => {
                translatePage(e.target.value);
            });

            // Initial translation on page load
            window.addEventListener('load', () => {
                translatePage(languageSelect.value);
            });

            toggleAuth.addEventListener('click', (e) => {
                e.preventDefault();
                isSignUp = !isSignUp;
                const lang = languageSelect.value;
                if (isSignUp) {
                    authTitle.textContent = translations[lang].signUpTitle;
                    authBtn.textContent = translations[lang].signUpBtn;
                    toggleText.textContent = translations[lang].toggleSignUpText;
                    toggleAuth.textContent = translations[lang].toggleSignUpLink;
                } else {
                    authTitle.textContent = translations[lang].signInTitle;
                    authBtn.textContent = translations[lang].signInBtn;
                    toggleText.textContent = translations[lang].toggleSignInText;
                    toggleAuth.textContent = translations[lang].toggleSignInLink;
                }
                authMessage.textContent = '';
                passwordInput.value = '';
            });

            authForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const username = usernameInput.value;
                const password = passwordInput.value;
                authMessage.textContent = '';

                let url, message;
                if (isSignUp) {
                    url = '/signup';
                } else {
                    url = '/login';
                }

                try {
                    const response = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
                    });

                    const data = await response.json();
                    const lang = languageSelect.value;

                    if (data.success) {
                        if (isSignUp) {
                            showModal('modalSignUpSuccess');
                            isSignUp = false;
                            authTitle.textContent = translations[lang].signInTitle;
                            authBtn.textContent = translations[lang].signInBtn;
                            toggleText.textContent = translations[lang].toggleSignInText;
                            toggleAuth.textContent = translations[lang].toggleSignInLink;
                            usernameInput.value = '';
                            passwordInput.value = '';
                        } else {
                            authPage.classList.add('hidden');
                            mainApp.classList.remove('hidden');
                        }
                    } else {
                        authMessage.textContent = data.message;
                    }
                } catch (error) {
                    authMessage.textContent = 'An error occurred. Please try again.';
                }
            });

            // --- Logout Logic ---
            logoutBtn.addEventListener('click', () => {
                mainApp.classList.add('hidden');
                authPage.classList.remove('hidden');
                usernameInput.value = '';
                passwordInput.value = '';
                isSignUp = false;
                const lang = languageSelect.value;
                authTitle.textContent = translations[lang].signInTitle;
                authBtn.textContent = translations[lang].signInBtn;
                toggleText.textContent = translations[lang].toggleSignInText;
                toggleAuth.textContent = translations[lang].toggleSignInLink;
            });

            // --- Existing App Logic (Now called only after login) ---
            const sampleReports = [
                { crop: 'Wheat', carbonSequestration: 2.5, timestamp: '2025-09-01' },
                { crop: 'Rice', carbonSequestration: 3.1, timestamp: '2025-08-28' },
                { crop: 'Sugarcane', carbonSequestration: 5.8, timestamp: '2025-08-25' },
                { crop: 'Lentils', carbonSequestration: 1.2, timestamp: '2025-08-20' },
                { crop: 'Cotton', carbonSequestration: 4.0, timestamp: '2025-08-15' },
            ];

            function renderReports() {
                reportsList.innerHTML = '';
                sampleReports.forEach(report => {
                    const reportItem = document.createElement('div');
                    reportItem.className = 'bg-gray-50 p-4 rounded-lg shadow text-left';
                    reportItem.innerHTML = `
                        <p class="text-gray-800 font-semibold">Crop: ${report.crop}</p>
                        <p class="text-gray-600">Carbon Sequestration: <span class="text-green-600 font-medium">${report.carbonSequestration} tons</span></p>
                        <p class="text-gray-400 text-sm mt-1">Date: ${report.timestamp}</p>
                    `;
                    reportsList.appendChild(reportItem);
                });
            }

            addDataBtn.addEventListener('click', () => {
                dataEntryModal.style.display = 'flex';
            });

            viewReportsBtn.addEventListener('click', () => {
                renderReports();
                reportsModal.style.display = 'flex';
            });

            startVerificationBtn.addEventListener('click', () => {
                verificationModal.style.display = 'flex';
            });

            closeModalBtn.addEventListener('click', () => {
                hideModal(modal);
            });

            closeDataEntryBtn.addEventListener('click', () => {
                hideModal(dataEntryModal);
            });

            closeReportsBtn.addEventListener('click', () => {
                hideModal(reportsModal);
            });
            
            closeVerificationBtn.addEventListener('click', () => {
                hideModal(verificationModal);
            });
            
            simulateVerificationBtn.addEventListener('click', () => {
                hideModal(verificationModal);
                verificationProgressModal.style.display = 'flex';

                const steps = [
                    document.getElementById('step1'),
                    document.getElementById('step2'),
                    document.getElementById('step3'),
                    document.getElementById('step4'),
                ];

                const verificationLogic = (index) => {
                    if (index < steps.length) {
                        steps[index].innerHTML = steps[index].innerHTML.replace('⏳', '✅ Complete!');
                        if (index < steps.length - 1) {
                            setTimeout(() => verificationLogic(index + 1), 1000);
                        } else {
                            setTimeout(() => {
                                verificationSteps.classList.add('hidden');
                                finalMessage.classList.remove('hidden');
                            }, 1000);
                        }
                    }
                };
                verificationLogic(0);
            });

            closeVerificationProgressBtn.addEventListener('click', () => {
                hideModal(verificationProgressModal);
                verificationSteps.classList.remove('hidden');
                finalMessage.classList.add('hidden');
                document.querySelectorAll('.status-icon').forEach(icon => icon.textContent = '⏳');
            });

            dataEntryForm.addEventListener('submit', (event) => {
                event.preventDefault();
                const cropName = cropNameInput.value;
                const saplingCount = saplingCountInput.value;
                if (cropName && saplingCount) {
                    console.log('New data entry:', { cropName, saplingCount });
                    hideModal(dataEntryModal);
                    showModal('modalDataSuccess');
                    dataEntryForm.reset();
                } else {
                    showModal('modalFillFields');
                }
            });

            document.querySelectorAll('.modal').forEach(m => {
                m.addEventListener('click', (event) => {
                    if (event.target === m) {
                        hideModal(m);
                    }
                });
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/signup")
async def signup(username: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        hashed_password = hash_password(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return {"success": True, "message": "Sign up successful! You can now log in."}
    except sqlite3.IntegrityError:
        return {"success": False, "message": "Username already exists."}
    finally:
        conn.close()

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password(user[0], password):
        return {"success": True, "message": "Login successful!"}
    else:
        return {"success": False, "message": "Invalid username or password."}
