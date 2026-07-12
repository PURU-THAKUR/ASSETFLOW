// ============================================
// AssetFlow AI - Dashboard JavaScript
// Premium Interactions
// ============================================

// Update date/time
function updateDateTime() {
    const now = new Date();
    const options = { 
        weekday: 'short', 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    const el = document.getElementById('currentDateTime');
    if (el) el.textContent = now.toLocaleDateString('en-US', options);
}
updateDateTime();
setInterval(updateDateTime, 60000);

// ============================================
// Command Palette (Ctrl+K)
// ============================================
document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        toggleCommandPalette();
    }
    if (e.key === 'Escape') {
        closeCommandPalette();
    }
});

function toggleCommandPalette() {
    const palette = document.getElementById('commandPalette');
    if (palette) {
        palette.classList.toggle('show');
        if (palette.classList.contains('show')) {
            setTimeout(() => {
                const input = document.getElementById('commandSearch');
                if (input) input.focus();
            }, 100);
        }
    }
}

function closeCommandPalette() {
    const palette = document.getElementById('commandPalette');
    if (palette) palette.classList.remove('show');
}

// Command search
const commandSearch = document.getElementById('commandSearch');
const commandResults = document.getElementById('commandResults');

if (commandSearch) {
    commandSearch.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        if (query.length === 0) {
            commandResults.innerHTML = '';
            return;
        }
        
        // Fetch from backend
        fetch(`/ai/api/search?q=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(results => {
                if (results.length === 0) {
                    commandResults.innerHTML = `
                        <div class="command-result-item" style="color: var(--text-muted); padding: 12px 16px;">
                            No results found for "${query}"
                        </div>
                    `;
                    return;
                }
                
                commandResults.innerHTML = results.map(cmd => `
                    <a href="${cmd.url}" class="command-result-item">
                        <span class="result-icon">${cmd.icon}</span>
                        <div class="result-info">
                            <h4>${cmd.title}</h4>
                            <p>${cmd.description}</p>
                        </div>
                    </a>
                `).join('');
            })
            .catch(() => {
                // Fallback local search
                const commands = [
                    { icon: '📊', title: 'Dashboard', description: 'View dashboard', url: '/dashboard' },
                    { icon: '💻', title: 'Assets', description: 'Manage assets', url: '/assets' },
                    { icon: '📋', title: 'Allocation', description: 'Asset allocation', url: '/allocation' },
                    { icon: '📅', title: 'Bookings', description: 'Resource bookings', url: '/booking' },
                    { icon: '🔧', title: 'Maintenance', description: 'Maintenance requests', url: '/maintenance' },
                    { icon: '📈', title: 'Reports', description: 'View reports', url: '/reports' },
                    { icon: '📊', title: 'Analytics', description: 'Advanced analytics', url: '/analytics' },
                    { icon: '🌌', title: 'Digital Twin', description: '3D asset visualization', url: '/digital-twin' },
                    { icon: '🧠', title: 'AI Assistant', description: 'AI chat assistant', url: '/ai/assistant' },
                    { icon: '⚙️', title: 'Settings', description: 'Application settings', url: '/settings' },
                    { icon: '👤', title: 'Profile', description: 'User profile', url: '/profile' }
                ];
                
                const results = commands.filter(cmd => 
                    cmd.title.toLowerCase().includes(query) || 
                    cmd.description.toLowerCase().includes(query)
                );
                
                if (results.length === 0) {
                    commandResults.innerHTML = `
                        <div class="command-result-item" style="color: var(--text-muted); padding: 12px 16px;">
                            No results found for "${query}"
                        </div>
                    `;
                    return;
                }
                
                commandResults.innerHTML = results.map(cmd => `
                    <a href="${cmd.url}" class="command-result-item">
                        <span class="result-icon">${cmd.icon}</span>
                        <div class="result-info">
                            <h4>${cmd.title}</h4>
                            <p>${cmd.description}</p>
                        </div>
                    </a>
                `).join('');
            });
    });
}

// ============================================
// Profile Dropdown
// ============================================
const userProfile = document.querySelector('.user-profile');
if (userProfile) {
    userProfile.addEventListener('click', function(e) {
        const dropdown = this.querySelector('.dropdown-menu');
        if (dropdown) {
            dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
        }
    });
}

document.addEventListener('click', function(e) {
    const profile = document.querySelector('.user-profile');
    if (profile && !profile.contains(e.target)) {
        const dropdown = profile.querySelector('.dropdown-menu');
        if (dropdown) dropdown.style.display = 'none';
    }
});

// ============================================
// Notification Badge Update
// ============================================
function updateNotificationBadge() {
    fetch('/notifications/api/unread-count')
        .then(res => res.json())
        .then(data => {
            const badges = document.querySelectorAll('.badge');
            badges.forEach(badge => {
                if (data.count > 0) {
                    badge.textContent = data.count;
                    badge.style.display = 'inline';
                } else {
                    badge.style.display = 'none';
                }
            });
        })
        .catch(() => {});
}

// Update every 30 seconds
setInterval(updateNotificationBadge, 30000);
updateNotificationBadge();

// ============================================
// Global Search
// ============================================
const globalSearch = document.getElementById('globalSearch');
if (globalSearch) {
    globalSearch.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const query = this.value.trim();
            if (query) {
                window.location.href = `/assets?search=${encodeURIComponent(query)}`;
            }
        }
    });
}

// ============================================
// AI Insights Loader
// ============================================
function loadAIInsights() {
    const container = document.getElementById('aiInsights');
    if (!container) return;
    
    fetch('/ai/api/insights')
        .then(res => res.json())
        .then(insights => {
            if (insights.length === 0) {
                container.innerHTML = `
                    <div class="insight-card success">
                        <div class="insight-icon">✅</div>
                        <div class="insight-content">
                            <h4>All Systems Healthy</h4>
                            <p>No issues detected. Keep up the good work!</p>
                        </div>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = insights.map(insight => `
                <div class="insight-card ${insight.type}">
                    <div class="insight-icon">${insight.icon}</div>
                    <div class="insight-content">
                        <h4>${insight.title}</h4>
                        <p>${insight.message}</p>
                    </div>
                </div>
            `).join('');
        })
        .catch(() => {});
}

loadAIInsights();

// ============================================
// AI Assistant Toggle (Floating)
// ============================================
function toggleAI() {
    const chat = document.getElementById('aiChatWindow');
    if (chat) chat.classList.toggle('open');
}

function toggleAIAssistant() {
    const chat = document.getElementById('aiChatWindow');
    if (chat) chat.classList.toggle('open');
}

// ============================================
// Notification Page Redirect
// ============================================
function showNotifications() {
    window.location.href = '/notifications';
}

// ============================================
// Milky Way Stars (Dynamic)
// ============================================
function createStars() {
    const container = document.getElementById('milky-way');
    if (!container) return;
    
    // Clear existing stars
    container.innerHTML = '';
    
    // Create stars
    for (let i = 0; i < 200; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        star.style.left = Math.random() * 100 + '%';
        star.style.top = Math.random() * 100 + '%';
        star.style.width = Math.random() * 3 + 1 + 'px';
        star.style.height = star.style.width;
        star.style.setProperty('--duration', (Math.random() * 3 + 2) + 's');
        star.style.animationDelay = Math.random() * 5 + 's';
        container.appendChild(star);
    }
    
    // Create shooting stars
    for (let i = 0; i < 3; i++) {
        const shooting = document.createElement('div');
        shooting.className = 'shooting-star';
        shooting.style.top = Math.random() * 50 + '%';
        shooting.style.left = Math.random() * 70 + '%';
        shooting.style.animationDelay = (Math.random() * 10 + 5) + 's';
        shooting.style.animationDuration = (Math.random() * 3 + 3) + 's';
        container.appendChild(shooting);
    }
}

createStars();

console.log('🚀 AssetFlow AI Dashboard loaded successfully!');