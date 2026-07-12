// ============================================
// AssetFlow AI - Login JavaScript
// Login and Signup Interactions
// ============================================

// ============================================
// Toggle Password Visibility
// ============================================
function togglePassword() {
    const password = document.getElementById('password');
    if (password) {
        password.type = password.type === 'password' ? 'text' : 'password';
    }
}

// ============================================
// Password Strength (Signup)
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('password');
    const strengthBar = document.querySelector('.strength-bar');
    
    if (passwordInput && strengthBar) {
        passwordInput.addEventListener('input', function() {
            const strength = this.value.length;
            if (strength === 0) {
                strengthBar.style.width = '0%';
                strengthBar.style.background = 'transparent';
            } else if (strength < 6) {
                strengthBar.style.width = '33%';
                strengthBar.style.background = '#ff4444';
            } else if (strength < 10) {
                strengthBar.style.width = '66%';
                strengthBar.style.background = '#ffaa44';
            } else {
                strengthBar.style.width = '100%';
                strengthBar.style.background = '#44ff88';
            }
        });
    }
    
    // ============================================
    // Password Match Check (Signup)
    // ============================================
    const confirmPassword = document.getElementById('confirm_password');
    const passwordMatchHint = document.getElementById('password-match-hint');
    
    if (passwordInput && confirmPassword && passwordMatchHint) {
        confirmPassword.addEventListener('input', function() {
            if (this.value.length === 0) {
                passwordMatchHint.textContent = '';
                passwordMatchHint.style.color = 'var(--text-muted)';
                return;
            }
            
            if (passwordInput.value === this.value) {
                passwordMatchHint.textContent = '✅ Passwords match!';
                passwordMatchHint.style.color = '#44ff88';
            } else {
                passwordMatchHint.textContent = '❌ Passwords do not match';
                passwordMatchHint.style.color = '#ff4444';
            }
        });
    }
    
    // ============================================
    // Mobile Number Validation (Signup)
    // ============================================
    const mobileInput = document.getElementById('mobile');
    if (mobileInput) {
        mobileInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9+ ]/g, '');
        });
    }
    
    // ============================================
    // Form Validation (Signup)
    // ============================================
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password')?.value || '';
            const confirm = document.getElementById('confirm_password')?.value || '';
            
            if (password !== confirm) {
                e.preventDefault();
                alert('Passwords do not match!');
                return false;
            }
            
            if (password.length < 6) {
                e.preventDefault();
                alert('Password must be at least 6 characters!');
                return false;
            }
        });
    }
    
    // ============================================
    // Auto-fill Demo Credentials (Login)
    // ============================================
    const loginInput = document.getElementById('login_id');
    const passwordInput2 = document.getElementById('password');
    
    if (loginInput && passwordInput2) {
        const urlParams = new URLSearchParams(window.location.search);
        const demo = urlParams.get('demo');
        if (demo === 'admin') {
            loginInput.value = 'admin@assetflow.com';
            passwordInput2.value = 'admin123';
        } else if (demo === 'employee') {
            loginInput.value = 'EMP001';
            passwordInput2.value = 'password123';
        }
    }
});

// ============================================
// Milky Way Background (Login)
// ============================================
function createStars() {
    const container = document.getElementById('milky-way');
    if (!container) return;
    
    // Clear existing
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
}

document.addEventListener('DOMContentLoaded', function() {
    createStars();
});

console.log('🔐 Login module loaded successfully!');