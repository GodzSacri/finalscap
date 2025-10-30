// ==================== CONSTANTS AND CONFIGURATION ====================
const CONFIG = {
    API_URL: "https://finalscap.onrender.com",
    TOKEN_KEY: "token",
    EMAIL_KEY: "email",
    ALLOWED_PATHS: ['/', '/login', '/register'],
    REQUEST_TIMEOUT: 45000, // 45 seconds
    NOTIFICATION_DURATION: 3000 // 3 seconds
};

const Auth = {
    getToken: () => localStorage.getItem(CONFIG.TOKEN_KEY),
    setToken: (token) => localStorage.setItem(CONFIG.TOKEN_KEY, token),
    clearToken: () => localStorage.removeItem(CONFIG.TOKEN_KEY),
    getEmail: () => localStorage.getItem(CONFIG.EMAIL_KEY),
    setEmail: (email) => localStorage.setItem(CONFIG.EMAIL_KEY, email),
    clearEmail: () => localStorage.removeItem(CONFIG.EMAIL_KEY),
    clearAll: () => localStorage.clear(),
    
    isTokenValid: () => {
        const token = Auth.getToken();
        if (!token) return false;
        
        try {
            const tokenData = JSON.parse(atob(token.split('.')[1]));
            return tokenData.exp * 1000 > Date.now();
        } catch (e) {
            return false;
        }
    },
    
    checkAuth: () => {
        const currentPath = window.location.pathname;
        const isAllowedPath = CONFIG.ALLOWED_PATHS.some(
            path => currentPath === path || currentPath.startsWith(path + '/')
        );
        
        if (!Auth.isTokenValid() && !isAllowedPath) {
            Auth.clearAll();
            window.location.href = '/';
            return false;
        }
        return true;
    }
};

/**
 * API Communication
 */
const API = {
    fetch: async (url, options = {}) => {
        const fullUrl = url.startsWith('http') ? url : `${CONFIG.API_URL}${url.startsWith('/') ? '' : '/'}${url}`;
        
        const headers = {
            'Authorization': `Bearer ${Auth.getToken()}`,
            'Content-Type': 'application/json',
            ...options.headers
        };

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), CONFIG.REQUEST_TIMEOUT);

            const response = await fetch(fullUrl, { 
                ...options, 
                headers,
                signal: controller.signal,
                credentials: 'include'
            });

            clearTimeout(timeoutId);

            if (response.status === 401) {
                Auth.clearAll();
                window.location.href = '/';
                throw new Error("Session expired. Please login again.");
            }

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.msg || `Request failed with status ${response.status}`);
            }

            return response;
        } catch (error) {
            console.error("API Error:", error);
            let errorMessage = "An error occurred";
            
            if (error.name === 'AbortError') {
                errorMessage = "Request timed out. Please try again.";
            } else if (error.name === 'TypeError') {
                errorMessage = "Network error. Please check your connection.";
            } else {
                errorMessage = error.message || errorMessage;
            }
            
            throw new Error(errorMessage);
        }
    },

    loadInbox: async () => {
        try {
            const response = await API.fetch("/api/inbox");
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.msg || "Failed to load inbox");
            }
            
            return data.messages || [];
        } catch (error) {
            console.error("Failed to load inbox:", error);
            throw error;
        }
    },

    loadSent: async () => {
        try {
            const response = await API.fetch("/api/sent");
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.msg || "Failed to load sent messages");
            }
            
            return data.messages || [];
        } catch (error) {
            console.error("Failed to load sent messages:", error);
            throw error;
        }
    },

    sendMessage: async (messageData) => {
        try {
            const response = await API.fetch("/api/send", {
                method: "POST",
                body: JSON.stringify(messageData)
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.msg || "Failed to send message");
            }
            
            return data;
        } catch (error) {
            console.error("Failed to send message:", error);
            throw error;
        }
    },

    getEncryptionStatus: async () => {
        try {
            const response = await API.fetch("/api/encryption-status");
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.msg || "Failed to get encryption status");
            }
            
            return data;
        } catch (error) {
            console.error("Failed to get encryption status:", error);
            return { encryption_available: false, default_encrypt: false };
        }
    }
};

/**
 * UI Components and Helpers
 */
const UI = {
    elements: {
        userEmail: document.getElementById("userEmail"),
        btnLogout: document.getElementById("btnLogout"),
        btnCompose: document.getElementById("btnCompose"),
        btnInbox: document.getElementById("btnInbox"),
        btnSent: document.getElementById("btnSent"),
        messageList: document.getElementById("messageList"),
        sentList: document.getElementById("sentList"),
        sendBtn: document.getElementById("sendBtn"),
        emailInput: document.getElementById("to"),
        subjectInput: document.getElementById("subject"),
        bodyInput: document.getElementById("body"),
        encryptToggle: document.getElementById("encryptToggle"),
        encryptionStatus: document.getElementById("encryptionStatus"),
        refreshInbox: document.getElementById("refreshInbox"),
        refreshSent: document.getElementById("refreshSent"),
        notification: document.getElementById("notification"),
        emailValidationMsg: document.getElementById("emailValidationMsg"),

        attachmentInput: document.getElementById("attachment")
    },

    showNotification: (message, isError = false) => {
        const { notification } = UI.elements;
        if (!notification) return;
        
        notification.textContent = message;
        notification.className = `notification ${isError ? "error" : ""} show`;
        
        setTimeout(() => {
            notification.classList.remove("show");
        }, CONFIG.NOTIFICATION_DURATION);
    },

    renderMessages: (messages, container) => {
        if (!container) return;
        
        container.innerHTML = messages.length ? 
            messages.map(msg => `
                <div class="message-item ${msg.is_encrypted ? 'encrypted-message' : ''}" data-id="${msg.id}">
                    <div class="message-header">
                        <span class="from">
                            <i class="fas fa-user"></i> 
                            From: ${msg.sender_email || 'Unknown sender'}
                        </span>
                        <span class="to">
                            <i class="fas fa-arrow-right"></i> 
                           To: ${msg.recipient_email || 'Unknown recipient'}
                        </span>
                        <span class="date">${new Date(msg.timestamp).toLocaleString()}</span>
                        ${msg.is_encrypted ? '<span class="encryption-badge"><i class="fas fa-lock"></i> Encrypted</span>' : ''}
                    </div>
                </div>
            `).join('') :
            '<div class="no-messages">No messages found</div>';
    },

    showLoading: (container, message = "Loading...") => {
        if (container) {
            container.innerHTML = `
                <div class="loading-msg">
                    <i class="fas fa-spinner fa-spin"></i> ${message}
                </div>
            `;
        }
    },

    showError: (container, message = "An error occurred") => {
        if (container) {
            container.innerHTML = `
                <div class="error-msg">
                    <i class="fas fa-exclamation-triangle"></i> ${message}
                </div>
            `;
        }
    },

    validateEmail: (email) => {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    },

    showEmailValidation: (message, isError = false) => {
        const { emailValidationMsg } = UI.elements;
        if (!emailValidationMsg) return;
        
        emailValidationMsg.textContent = message;
        emailValidationMsg.className = `validation-msg ${isError ? 'error' : 'success'}`;
        emailValidationMsg.style.display = message ? 'block' : 'none';
    },

    clearForm: () => {
        const { emailInput, subjectInput, bodyInput, encryptToggle } = UI.elements;
        if (emailInput) emailInput.value = '';
        if (subjectInput) subjectInput.value = '';
        if (bodyInput) bodyInput.value = '';
        if (encryptToggle) encryptToggle.checked = true; // Default to encrypted
        UI.showEmailValidation('');
        UI.updateEncryptionStatus();
    },

    updateEncryptionStatus: () => {
        const { encryptToggle, encryptionStatus } = UI.elements;
        if (!encryptionStatus) return;
        
        const isEncrypted = encryptToggle?.checked ?? true;
        encryptionStatus.innerHTML = isEncrypted ? 
            '<i class="fas fa-lock"></i> Message will be encrypted' :
            '<i class="fas fa-unlock"></i> Message will be sent as plain text';
        encryptionStatus.className = `encryption-status ${isEncrypted ? 'encrypted' : 'plain'}`;
    },

    setupEncryptionToggle: () => {
        const { encryptToggle } = UI.elements;
        
        if (encryptToggle) {
            encryptToggle.addEventListener('change', () => {
                UI.updateEncryptionStatus();
                const isEncrypted = encryptToggle.checked;
                UI.showNotification(
                    isEncrypted ? "Encryption enabled" : "Encryption disabled", 
                    !isEncrypted
                );
            });
        }
    }
};

// ==================== EVENT HANDLERS ====================

const EventHandlers = {
    setupNavigation: () => {
        const { btnLogout, btnInbox, btnCompose, btnSent } = UI.elements;
        
        btnLogout?.addEventListener("click", () => {
            Auth.clearAll();
            window.location.href = "/";
        });

        btnInbox?.addEventListener("click", () => {
            window.location.href = "/inbox";
        });

        btnCompose?.addEventListener("click", () => {
            window.location.href = "/compose";
        });

        btnSent?.addEventListener("click", () => {
            window.location.href = "/sent";
        });
    },

    setupRefresh: () => {
        const { refreshInbox, refreshSent } = UI.elements;
        
        refreshInbox?.addEventListener("click", async () => {
            UI.showNotification("Refreshing inbox...");
            await loadAndRenderInbox();
        });

        refreshSent?.addEventListener("click", async () => {
            UI.showNotification("Refreshing sent messages...");
            await loadAndRenderSent();
        });
    },

    setupCompose: () => {
        const { sendBtn, emailInput, subjectInput, bodyInput } = UI.elements;
        
        // Setup encryption toggle
        UI.setupEncryptionToggle();
        
        // Email validation on input
        emailInput?.addEventListener("input", () => {
            const email = emailInput.value.trim();
            if (email) {
                if (UI.validateEmail(email)) {
                    UI.showEmailValidation("Valid email address", false);
                } else {
                    UI.showEmailValidation("Please enter a valid email address", true);
                }
            } else {
                UI.showEmailValidation("");
            }
        });

        // Send message
        sendBtn?.addEventListener("click", async () => {
            await handleSendMessage();
        });

        // Handle Enter key in form fields
        [emailInput, subjectInput].forEach(element => {
            element?.addEventListener("keypress", (e) => {
                if (e.key === "Enter") {
                    e.preventDefault();
                    if (element === emailInput && subjectInput) {
                        subjectInput.focus();
                    } else if (element === subjectInput && bodyInput) {
                        bodyInput.focus();
                    }
                }
            });
        });

        // Handle Ctrl+Enter in body to send
        bodyInput?.addEventListener("keydown", (e) => {
            if (e.ctrlKey && e.key === "Enter") {
                e.preventDefault();
                handleSendMessage();
            }
        });
    }
};

// ==================== APPLICATION LOGIC ====================

async function loadAndRenderInbox() {
    const { messageList } = UI.elements;
    
    try {
        UI.showLoading(messageList, "Loading inbox...");
        const messages = await API.loadInbox();
        UI.renderMessages(messages, messageList);
        
        if (messages.length === 0) {
            UI.showNotification("No messages in inbox");
        } else {
            const encryptedCount = messages.filter(msg => msg.is_encrypted).length;
            if (encryptedCount > 0) {
                UI.showNotification(`Loaded ${messages.length} messages (${encryptedCount} encrypted)`);
            }
        }
    } catch (error) {
        console.error("Failed to load inbox:", error);
        UI.showError(messageList, error.message);
        UI.showNotification(error.message || "Error loading inbox", true);
    }
}

async function loadAndRenderSent() {
    const { sentList } = UI.elements;
    
    try {
        UI.showLoading(sentList, "Loading sent messages...");
        const messages = await API.loadSent();
        UI.renderMessages(messages, sentList);
        
        if (messages.length === 0) {
            UI.showNotification("No sent messages");
        } else {
            const encryptedCount = messages.filter(msg => msg.is_encrypted).length;
            if (encryptedCount > 0) {
                UI.showNotification(`Loaded ${messages.length} messages (${encryptedCount} encrypted)`);
            }
        }
    } catch (error) {
        console.error("Failed to load sent messages:", error);
        UI.showError(sentList, error.message);
        UI.showNotification(error.message || "Error loading sent messages", true);
    }
}

async function handleSendMessage() {
    const { emailInput, subjectInput, bodyInput, encryptToggle, sendBtn, attachmentInput } = UI.elements;
    const recipient = emailInput.value.trim();
    const subject = subjectInput.value.trim();
    const body = bodyInput.value.trim();
    const shouldEncrypt = encryptToggle?.checked ?? true;

    if (!recipient || !UI.validateEmail(recipient)) {
        UI.showNotification("Please enter a valid recipient email", true);
        return;
    }
    if (!subject || !body) {
        UI.showNotification("Subject and body are required", true);
        return;
    }

    try {
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';

        const formData = new FormData();
        formData.append('recipient_email', recipient);
        formData.append('subject', subject);
        formData.append('body', body);
        formData.append('encrypt_message', shouldEncrypt);

        if (attachmentInput && attachmentInput.files.length > 0) {
            for (let i = 0; i < attachmentInput.files.length; i++) {
                formData.append('attachments', attachmentInput.files[i]); // match backend key
            }
        }

        const response = await fetch(`${CONFIG.API_URL}/api/send`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${Auth.getToken()}`
                // Do not set 'Content-Type' when using FormData
            },
            body: formData
        });

        const result = await response.json();
        if (!result.success) throw new Error(result.msg);

        UI.showNotification("Message sent successfully!");
        UI.clearForm();
        document.getElementById("fileNames").textContent = ""; // Clear preview
        setTimeout(() => window.location.href = "/sent", 1500);
    } catch (err) {
        UI.showNotification(err.message || "Failed to send message", true);
    } finally {
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Message';
    }
}

const { attachmentInput } = UI.elements;
const fileNamesDisplay = document.getElementById("fileNames");

attachmentInput?.addEventListener("change", () => {
    if (!fileNamesDisplay) return;
    const files = Array.from(attachmentInput.files).map(file => file.name);
    fileNamesDisplay.textContent = files.length
        ? `Selected: ${files.join(', ')}`
        : "";
});

async function initializeEncryption() {
    try {
        const encryptionStatus = await API.getEncryptionStatus();
        const { encryptToggle } = UI.elements;
        
        if (encryptToggle && encryptionStatus.encryption_available) {
            encryptToggle.checked = encryptionStatus.default_encrypt;
            UI.updateEncryptionStatus();
        }
    } catch (error) {
        console.warn("Could not initialize encryption status:", error);
    }
}

function initializeUserInfo() {
    const { userEmail } = UI.elements;
    const email = Auth.getEmail();
    
    if (userEmail && email) {
        userEmail.innerHTML = `<i class="fas fa-user-circle"></i> ${email}`;
    }
}

// ==================== INITIALIZATION ====================

async function initializeApp() {
    // Check authentication first
    if (!Auth.checkAuth()) return;
    
    // Initialize user info
    initializeUserInfo();
    
    // Initialize encryption settings
    await initializeEncryption();
    
    // Setup event listeners
    EventHandlers.setupNavigation();
    EventHandlers.setupRefresh();
    EventHandlers.setupCompose();
    
    // Load appropriate content based on current page
    const currentPath = window.location.pathname;
    
    switch (currentPath) {
        case "/inbox":
            loadAndRenderInbox();
            break;
        case "/sent":
            loadAndRenderSent();
            break;

            
        case "/compose":
            // Focus on first input field
            const { emailInput } = UI.elements;
            if (emailInput) {
                setTimeout(() => emailInput.focus(), 100);
            }
            break;
    }
    
    // Debug info
    console.debug("App initialized for path:", currentPath);
    console.debug("Current token:", Auth.getToken() ? "Present" : "Missing");
    console.debug("User email:", Auth.getEmail());
}

// Start the application when DOM is loaded
document.addEventListener("DOMContentLoaded", initializeApp);
