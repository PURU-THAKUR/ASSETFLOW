// ============================================
// AssetFlow AI - Signup JavaScript
// Signup Form Interactions
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // ============================================
    // Password Strength
    // ============================================
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
    // Password Match Check
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
    // Mobile Number Validation
    // ============================================
    const mobileInput = document.getElementById('mobile');
    if (mobileInput) {
        mobileInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9+ ]/g, '');
        });
    }
    
    // ============================================
    // Form Validation
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
    // Create Stars Background
    // ============================================
    function createStars() {
        const container = document.getElementById('milky-way');
        if (!container) return;
        
        container.innerHTML = '';
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
    
    createStars();
});

console.log('📝 Signup module loaded successfully!');