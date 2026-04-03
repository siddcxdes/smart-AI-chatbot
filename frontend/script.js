const API_BASE = "https://smart-ai-chatbot-eruy.onrender.com";
let token = localStorage.getItem("token") || "";
let currentUserEmail = "";

function toggleAuth() {
    const lg = document.getElementById('loginForm');
    const rg = document.getElementById('regForm');
    if (lg.classList.contains('hidden')) {
        lg.classList.remove('hidden');
        rg.classList.add('hidden');
    } else {
        lg.classList.add('hidden');
        rg.classList.remove('hidden');
    }
}

function checkAuthPage(type) {
    const authWrapper = document.getElementById('authWrapper');
    const mainWrapper = type === 'user' ? document.getElementById('chatWrapper') : document.getElementById('adminWrapper');

    if (!token) {
        authWrapper.classList.remove('hidden');
        mainWrapper.classList.add('hidden');
        return;
    }

    fetch(API_BASE + "/api/users/me", { headers: { "Authorization": "Bearer " + token } })
    .then(res => {
        if (!res.ok) throw new Error("Unauthorized");
        return res.json();
    })
    .then(data => {
        currentUserEmail = data.email;
        let navEmail = document.getElementById('navUserEmail');
        if(navEmail) navEmail.innerText = currentUserEmail;
        
        document.getElementById('navUserArea').classList.remove('hidden');
        authWrapper.classList.add('hidden');

        if (type === 'admin') {
            if (data.role !== 'admin') {
                alert("Unauthorized. You are not an admin.");
                logout('/admin');
            } else {
                mainWrapper.classList.remove('hidden');
                loadTickets();
            }
        } else {
            mainWrapper.classList.remove('hidden');
            loadChatHistory();
        }
    })
    .catch(() => { logout(type === 'admin' ? '/admin' : '/chat'); });
}

function loginUser() {
    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value;
    if(!email || !password) return alert("Please enter email and password");

    const btn = document.getElementById("loginBtn");
    btn.disabled = true; btn.innerText = "Signing in...";

    fetch(API_BASE + "/api/users/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username: email, password: password })
    })
    .then(res => {
        if (!res.ok) throw new Error("Invalid credentials");
        return res.json();
    })
    .then(data => {
        localStorage.setItem("token", data.access_token);
        window.location.reload();
    })
    .catch(err => {
        alert(err.message);
        btn.disabled = false; btn.innerText = "Sign In";
    });
}

function registerUser() {
    const email = document.getElementById("regEmail").value.trim();
    const password = document.getElementById("regPassword").value;
    if(!email || !password) return alert("Please enter email and password");

    const btn = document.getElementById("regBtn");
    btn.disabled = true; btn.innerText = "Registering...";

    fetch(API_BASE + "/api/users/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email, password: password, name: email.split('@')[0] })
    })
    .then(res => {
        if (!res.ok) throw new Error("Registration failed. Email might exist.");
        return res.json();
    })
    .then(data => {
        alert("Registration successful! Please sign in.");
        toggleAuth();
        btn.disabled = false; btn.innerText = "Register";
    })
    .catch(err => {
        alert(err.message);
        btn.disabled = false; btn.innerText = "Register";
    });
}

function loginAdmin() {
    let secret = document.getElementById("secretCodeInput").value.trim();
    if (!secret) return;

    fetch(API_BASE + "/api/users/admin-secret-login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ secret_code: secret })
    })
    .then(res => {
        if (!res.ok) throw new Error("Invalid Master Key");
        return res.json();
    })
    .then(data => {
        localStorage.setItem("token", data.access_token);
        window.location.reload();
    })
    .catch(err => alert(err.message));
}

function logout(redirectPath = '/') {
    localStorage.removeItem("token");
    window.location.href = redirectPath;
}

function loadChatHistory() {
    const messages = document.getElementById("chatMessages");
    if(!messages) return;
    
    messages.innerHTML = `
        <div class="msg bot">
            <div class="msg-avatar">AI</div>
            <div class="msg-bubble">Hello! How can I assist you today?</div>
        </div>
    `;

    fetch(API_BASE + "/api/chat/history/" + encodeURIComponent(currentUserEmail), {
        headers: { "Authorization": "Bearer " + token }
    })
    .then(res => res.json())
    .then(data => {
        if(data && data.length > 0) {
            data.reverse().forEach(c => {
                appendMessage(c.question, "user");
                appendMessage(c.answer, "bot");
            });
        }
    })
    .catch(e => console.error(e));
}

function sendMessage() {
    const input = document.getElementById("chatInput");
    const text = input.value.trim();
    if (!text) return;

    input.value = "";
    appendMessage(text, "user");

    const btn = document.getElementById("sendBtn");
    btn.disabled = true;

    fetch(API_BASE + "/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token },
        body: JSON.stringify({ user_email: currentUserEmail, question: text })
    })
    .then(res => {
        if (!res.ok) throw new Error("Failed response");
        return res.json();
    })
    .then(data => { appendMessage(data.answer, "bot"); })
    .catch(err => { appendMessage("System Error: Could not connect to AI Engine.", "bot"); })
    .finally(() => { btn.disabled = false; input.focus(); });
}

function appendMessage(text, sender) {
    const messages = document.getElementById("chatMessages");
    if(!messages) return;

    const wrapper = document.createElement("div");
    wrapper.className = `msg ${sender} animate-fade-up`;
    
    const avatar = document.createElement("div");
    avatar.className = `msg-avatar`;
    avatar.textContent = sender === 'bot' ? 'AI' : 'U';
    
    const bubble = document.createElement("div");
    bubble.className = "msg-bubble";
    bubble.innerText = text;
    
    wrapper.appendChild(avatar);
    wrapper.appendChild(bubble);
    messages.appendChild(wrapper);
    messages.scrollTop = messages.scrollHeight;
}

function loadTickets() {
    fetch(API_BASE + "/api/tickets", { headers: { "Authorization": "Bearer " + token } })
    .then(res => res.json())
    .then(data => {
        let body = document.getElementById("ticketsBody");
        if(!body) return;
        body.innerHTML = "";

        if (data.length === 0) {
            body.innerHTML = `<tr><td colspan="5" style="text-align:center; color: var(--text-muted); padding:3rem;">No tickets found</td></tr>`;
            return;
        }

        let openCount = 0; let closedCount = 0;

        data.forEach(t => {
            let isClosed = t.status === "closed";
            if(isClosed) closedCount++; else openCount++;

            let actionHtml = !isClosed ? 
                `<button class="btn btn-primary" style="padding: 0.4rem 1rem; font-size: 0.75rem;" onclick="resolveTicket(${t.id}, this)">Resolve</button>` : 
                `<span style="color: var(--text-muted); font-size: 0.85rem; font-weight:600;">Resolved</span>`;

            let qLines = t.question.split('\n');
            let lastLine = qLines[qLines.length - 1] || "";
            if(lastLine.startsWith("Customer: ")) lastLine = lastLine.replace("Customer: ", "");

            body.innerHTML += `
                <tr>
                    <td>#${t.id}</td>
                    <td>${t.user_email}</td>
                    <td style="max-width: 250px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${t.question}">${lastLine}</td>
                    <td><span class="badge ${isClosed?'closed':'open'}">${t.status}</span></td>
                    <td>${actionHtml}</td>
                </tr>
            `;
        });
        
        document.getElementById("totalTickets").innerText = data.length;
        document.getElementById("openTickets").innerText = openCount;
        document.getElementById("closedTickets").innerText = closedCount;
    });
}

function resolveTicket(id, element) {
    element.innerText = "Wait...";
    fetch(API_BASE + "/api/tickets/" + id, {
        method: "PUT",
        headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token },
        body: JSON.stringify({ status: "closed" })
    })
    .then(res => {
        if (res.ok) loadTickets();
        else { alert("Updating ticket failed."); element.innerText = "Resolve"; }
    });
}

function setupFileInput() {
    const docsInput = document.getElementById('docsInput');
    if (docsInput) {
        docsInput.addEventListener('change', function(e) {
            const countStr = this.files.length > 0 ? `${this.files.length} document(s) ready for upload` : "Click to browse files or drag and drop";
            document.getElementById('fileCount').innerText = countStr;
            const btn = document.getElementById('btnUpload');
            btn.disabled = this.files.length === 0;
            if(this.files.length > 0) btn.classList.remove('hidden');
            else btn.classList.add('hidden');
        });
    }
}

function uploadDocs() {
    const docsInput = document.getElementById('docsInput');
    if(!docsInput || docsInput.files.length === 0) return;

    const formData = new FormData();
    formData.append("wipe_existing", "false");
    for(let i=0; i<docsInput.files.length; i++) formData.append("files", docsInput.files[i]);

    const btn = document.getElementById('btnUpload');
    btn.innerText = "Uploading...";
    btn.disabled = true;

    fetch(API_BASE + "/api/admin/upload-docs", {
        method: "POST",
        headers: { "Authorization": "Bearer " + token },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message || "Uploaded successfully");
        docsInput.value = "";
        document.getElementById('fileCount').innerText = "Click to browse files or drag and drop";
        btn.classList.add('hidden');
        btn.innerText = "Upload to Server";
    })
    .catch(err => {
        alert("Upload failed: " + err.message);
        btn.innerText = "Upload to Server";
        btn.disabled = false;
    });
}

function retrainAI() {
    const btn = document.getElementById('btnRetrain');
    btn.innerText = "Retraining... Please Wait";
    btn.disabled = true;

    fetch(API_BASE + "/api/admin/retrain", {
        method: "POST",
        headers: { "Authorization": "Bearer " + token }
    })
    .then(res => res.json())
    .then(data => { alert(data.message || "Retrained successfully"); })
    .catch(err => alert("Retrain failed: " + err.message))
    .finally(() => {
        btn.innerText = "Refresh Knowledge Base";
        btn.disabled = false;
    });
}
