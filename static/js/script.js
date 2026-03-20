import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
import { getAuth, signInWithPopup, signOut, GoogleAuthProvider, onAuthStateChanged, browserLocalPersistence, setPersistence } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";
import { getFirestore, doc, getDoc, setDoc, collection, addDoc, query, orderBy, getDocs } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyDT-5DXoAHHhZDZEjk2V1Iz20sM62JD6so",
  authDomain: "shaurya-noob.firebaseapp.com",
  projectId: "shaurya-noob",
  storageBucket: "shaurya-noob.firebasestorage.app",
  messagingSenderId: "711818029705",
  appId: "1:711818029705:web:026c440c7b17b021f63458",
  measurementId: "G-FRXXKEPHNK"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const provider = new GoogleAuthProvider();

let currentUser = null;

// Set persistence to LOCAL so the user stays signed in across browser restarts
setPersistence(auth, browserLocalPersistence);

// Firestore helpers
async function saveProfile(uid, metrics, planText) {
    await setDoc(doc(db, "users", uid), {
        ...metrics,
        plan_text: planText,
        updated_at: new Date().toISOString()
    }, { merge: true });
}

async function loadProfile(uid) {
    const snap = await getDoc(doc(db, "users", uid));
    return snap.exists() ? snap.data() : null;
}

async function saveChatMessage(uid, sender, text) {
    await addDoc(collection(db, "users", uid, "chats"), {
        sender: sender,
        text: text,
        timestamp: new Date().toISOString()
    });
}

async function loadChatHistory(uid) {
    const q = query(collection(db, "users", uid, "chats"), orderBy("timestamp", "asc"));
    const snap = await getDocs(q);
    const messages = [];
    snap.forEach(doc => messages.push(doc.data()));
    return messages;
}

document.addEventListener('DOMContentLoaded', () => {
    const formMetrics = document.getElementById('metrics-form');
    const inputChat = document.getElementById('chat-input');
    const btnSend = document.getElementById('btn-send');
    const chatBox = document.getElementById('chat-box');

    // Auto-login check — fires if browser remembers the session
    onAuthStateChanged(auth, async (user) => {
        if (user) {
            currentUser = user;
            const profile = await loadProfile(user.uid);
            if (profile && profile.plan_text) {
                showScreen('chat');
                // Load all previous chat messages
                const history = await loadChatHistory(user.uid);
                if (history.length > 0) {
                    history.forEach(msg => addMessage(msg.sender, msg.text, false));
                } else {
                    addMessage('ai', `Welcome back, ${user.displayName}!\n\nHere is your saved plan:\n\n${profile.plan_text}`, false);
                }
            } else {
                showScreen('questionnaire');
            }
        }
    });

    document.getElementById('btn-google-login').addEventListener('click', async () => {
        try {
            const result = await signInWithPopup(auth, provider);
            currentUser = result.user;
            const profile = await loadProfile(currentUser.uid);
            if (profile && profile.plan_text) {
                showScreen('chat');
                const history = await loadChatHistory(currentUser.uid);
                if (history.length > 0) {
                    history.forEach(msg => addMessage(msg.sender, msg.text, false));
                } else {
                    addMessage('ai', `Welcome back, ${currentUser.displayName}!\n\nHere is your saved plan:\n\n${profile.plan_text}`, false);
                }
            } else {
                showScreen('questionnaire');
            }
        } catch (error) {
            console.error("Sign in error", error);
            alert("Sign in failed: " + error.message);
        }
    });

    // Sign Out
    document.getElementById('btn-signout').addEventListener('click', async () => {
        await signOut(auth);
        currentUser = null;
        chatBox.innerHTML = '';
        showScreen('welcome');
    });

    function showScreen(screenName) {
        const screens = {
            welcome: document.getElementById('welcome-screen'),
            questionnaire: document.getElementById('questionnaire-screen'),
            loading: document.getElementById('loading-screen'),
            chat: document.getElementById('chat-screen')
        };
        Object.keys(screens).forEach(key => {
            if (key === screenName) {
                screens[key].className = 'screen active';
            } else if (screens[key].classList.contains('active')) {
                screens[key].className = 'screen prev';
            } else {
                screens[key].className = 'screen';
            }
        });
    }

    window.showScreen = showScreen;

    formMetrics.addEventListener('submit', async (e) => {
        e.preventDefault();
        showScreen('loading');

        const metrics = {
            basic: document.getElementById('input-basic').value,
            goal: document.getElementById('input-goal').value,
            diet: document.getElementById('input-diet').value,
            activity: document.getElementById('input-activity').value,
            experience: document.getElementById('input-experience').value,
            days: document.getElementById('input-days').value,
            health: document.getElementById('input-health').value
        };

        try {
            const response = await fetch('/api/generate_plan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ metrics, uid: currentUser ? currentUser.uid : 'anonymous' })
            });
            const data = await response.json();
            
            if (response.ok) {
                if (currentUser) {
                    await saveProfile(currentUser.uid, metrics, data.plan);
                    await saveChatMessage(currentUser.uid, 'ai', data.plan);
                }
                showScreen('chat');
                addMessage('ai', data.plan, false);
            } else {
                showScreen('chat');
                addMessage('ai', "Error connecting to AI: " + (data.error || "Unknown"), false);
            }
        } catch (error) {
            showScreen('chat');
            addMessage('ai', "Error connecting to AI: " + error.message, false);
        }
    });

    function parseMarkdown(text) {
        let html = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        // Headers: any line starting with one or more # (with or without space after)
        html = html.replace(/^#{1,6}\s*(.+)$/gm, '<strong class="section-header">$1</strong>');
        // Bold: **text**
        html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        // Italic: *text*
        html = html.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');
        // Bullet points: - at start of line
        html = html.replace(/^- (.+)$/gm, '• $1');
        // Horizontal rule: --- on its own line
        html = html.replace(/^-{3,}$/gm, '<hr class="chat-divider">');
        return html;
    }

    // save=true means save to Firestore, false means just render (for loading history)
    function addMessage(sender, text, save = true) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;
        if (sender === 'ai') {
            msgDiv.innerHTML = parseMarkdown(text);
        } else {
            msgDiv.textContent = text;
        }
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;

        if (save && currentUser) {
            saveChatMessage(currentUser.uid, sender, text);
        }
    }

    window.addMessage = addMessage;

    async function sendMessage() {
        const text = inputChat.value.trim();
        if (!text) return;

        addMessage('user', text, true);
        inputChat.value = '';
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai typing';
        typingDiv.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
        chatBox.appendChild(typingDiv);
        chatBox.scrollTop = chatBox.scrollHeight;

        let planText = '';
        if (currentUser) {
            const profile = await loadProfile(currentUser.uid);
            if (profile) planText = profile.plan_text || '';
        }

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message: text, 
                    uid: currentUser ? currentUser.uid : 'anonymous',
                    plan_text: planText
                })
            });
            const data = await response.json();
            
            chatBox.removeChild(typingDiv);
            if (response.ok) {
                addMessage('ai', data.response, true);
            } else {
                addMessage('ai', "Error connecting to AI: " + (data.error || "Unknown"), false);
            }
        } catch (error) {
            chatBox.removeChild(typingDiv);
            addMessage('ai', "Error connecting to AI: " + error.message, false);
        }
    }

    btnSend.addEventListener('click', sendMessage);
    inputChat.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});
