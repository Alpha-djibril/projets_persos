const idSession = Math.random().toString(36).substring(2, 15);
// 1. Scroll Animations (Intersection Observer)
const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
};

const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.remove('opacity-0', 'translate-y-8');
            entry.target.classList.add('opacity-100', 'translate-y-0');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.querySelectorAll('.animate-on-scroll').forEach((el) => {
    observer.observe(el);
});

// 2. Chat Logic
const chatBody = document.getElementById('live-chat-body');
const chatInput = document.getElementById('live-chat-input');
const sendBtn = document.getElementById('live-chat-send');
const suggestionBtns = document.querySelectorAll('.suggestion-btn');

// Simple mock responses


function addMessageToChat(text, isBot) {
    const wrapDiv = document.createElement('div');
    wrapDiv.className = `flex ${isBot ? 'justify-start' : 'justify-end'} opacity-0 translate-y-2 transition-all duration-300 ease-out`;

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = `text-sm py-3 px-5 rounded-2xl shadow-[0_2px_10px_rgb(0,0,0,0.02)] max-w-[85%] leading-relaxed ${
        isBot 
        ? 'bg-white border border-slate-100 text-slate-700 rounded-tl-sm' 
        : 'bg-[#1a3c34] text-white rounded-tr-sm'
    }`;
    bubbleDiv.innerHTML = text.replace(/\n/g, '<br>');

    wrapDiv.appendChild(bubbleDiv);
    
    // Insert before the empty space at bottom (to keep input visible)
    chatBody.appendChild(wrapDiv);
    
    // Trigger animation
    setTimeout(() => {
        wrapDiv.classList.remove('opacity-0', 'translate-y-2');
        wrapDiv.classList.add('opacity-100', 'translate-y-0');
    }, 10);

    // Scroll to bottom smoothly
    chatBody.scrollTo({
        top: chatBody.scrollHeight,
        behavior: 'smooth'
    });
}

function showTypingIndicator() {
    const wrapDiv = document.createElement('div');
    wrapDiv.id = 'typing-indicator';
    wrapDiv.className = `flex justify-start opacity-0 transition-opacity duration-300`;

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = `bg-white border border-slate-100 py-3 px-4 rounded-2xl rounded-tl-sm shadow-sm flex gap-1 items-center`;
    
    // 3 dots
    for(let i=0; i<3; i++) {
        const dot = document.createElement('div');
        dot.className = `w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce`;
        dot.style.animationDelay = `${i * 0.15}s`;
        bubbleDiv.appendChild(dot);
    }

    wrapDiv.appendChild(bubbleDiv);
    chatBody.appendChild(wrapDiv);
    
    setTimeout(() => wrapDiv.classList.add('opacity-100'), 10);
    chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: 'smooth' });
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if(indicator) indicator.remove();
}

async function handleUserMessage(text) {
    if (!text.trim()) return;

    // 1. Désactiver l'input pendant le chargement
    chatInput.disabled = true;
    sendBtn.disabled = true;

    // 2. Afficher le message de l'utilisateur
    addMessageToChat(text, false);
    chatInput.value = '';

    // 3. Afficher l'animation "... en train de taper"
    showTypingIndicator();

    try {
        // 4. Envoyer le message à ton backend Python (Flask)
        const reponse = await fetch("/api/message", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: text, id_session: idSession })
        });

        // 5. Retirer l'animation de frappe
        removeTypingIndicator();

        // 6. Lire la réponse et l'afficher
        if (reponse.ok) {
            const donnees = await reponse.json();
            addMessageToChat(donnees.texte, true);
        } else {
            addMessageToChat("Erreur de communication avec le serveur.", true);
        }

    } catch (erreur) {
        console.error("Erreur backend:", erreur);
        removeTypingIndicator();
        addMessageToChat("Désolé, le serveur IA est actuellement injoignable. 🌿", true);
    } finally {
        // 7. Réactiver l'input
        chatInput.disabled = false;
        sendBtn.disabled = false;
        chatInput.focus();
    }
}

// Event Listeners for Chat
sendBtn.addEventListener('click', () => {
    handleUserMessage(chatInput.value);
});

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleUserMessage(chatInput.value);
    }
});

suggestionBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        handleUserMessage(btn.getAttribute('data-text'));
        // Optional: hide suggestion buttons after use
        // btn.parentElement.style.display = 'none';
    });
});