// ============================================
// AssetFlow AI - Notifications JavaScript
// Notification Management
// ============================================

// ============================================
// Mark Notification as Read
// ============================================
function markRead(id) {
    fetch(`/notifications/mark-read/${id}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const item = document.querySelector(`.notification-item[data-id="${id}"]`);
                if (item) {
                    item.classList.remove('unread');
                    const btn = item.querySelector('button[onclick*="markRead"]');
                    if (btn) btn.remove();
                    updateUnreadCount();
                }
            }
        })
        .catch(() => showToast('error', 'Error marking notification as read'));
}

// ============================================
// Delete Notification
// ============================================
function deleteNotification(id) {
    if (!confirm('Delete this notification?')) return;
    
    fetch(`/notifications/delete/${id}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const item = document.querySelector(`.notification-item[data-id="${id}"]`);
                if (item) {
                    item.style.opacity = '0';
                    item.style.transition = 'opacity 0.3s ease';
                    setTimeout(() => {
                        item.remove();
                        updateUnreadCount();
                        checkEmpty();
                    }, 300);
                }
            }
        })
        .catch(() => showToast('error', 'Error deleting notification'));
}

// ============================================
// Mark All as Read
// ============================================
function markAllRead() {
    fetch('/notifications/mark-all-read', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelectorAll('.notification-item.unread').forEach(item => {
                    item.classList.remove('unread');
                    const btn = item.querySelector('button[onclick*="markRead"]');
                    if (btn) btn.remove();
                });
                updateUnreadCount();
                showToast('success', 'All notifications marked as read!');
            }
        })
        .catch(() => showToast('error', 'Error marking all as read'));
}

// ============================================
// Filter Notifications
// ============================================
function filterNotifications(filter) {
    document.querySelectorAll('.filters-section .filter-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent.trim().toLowerCase() === filter) {
            btn.classList.add('active');
        }
    });
    
    document.querySelectorAll('.notification-item').forEach(item => {
        if (filter === 'all') {
            item.style.display = 'flex';
        } else if (filter === 'unread') {
            item.style.display = item.classList.contains('unread') ? 'flex' : 'none';
        } else if (filter === 'read') {
            item.style.display = !item.classList.contains('unread') ? 'flex' : 'none';
        }
    });
}

// ============================================
// Filter by Type
// ============================================
function filterByType() {
    const type = document.getElementById('typeFilter')?.value || '';
    document.querySelectorAll('.notification-item').forEach(item => {
        if (!type || item.dataset.type === type) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

// ============================================
// Update Unread Count
// ============================================
function updateUnreadCount() {
    const unread = document.querySelectorAll('.notification-item.unread').length;
    const badge = document.querySelector('.badge');
    if (badge) badge.textContent = unread;
    
    const countDisplay = document.querySelector('.page-header strong');
    if (countDisplay) countDisplay.textContent = unread;
}

// ============================================
// Check Empty State
// ============================================
function checkEmpty() {
    const items = document.querySelectorAll('.notification-item');
    const noNotifications = document.querySelector('.no-notifications');
    const list = document.querySelector('.notification-list');
    
    if (items.length === 0 && noNotifications && list) {
        list.style.display = 'none';
        noNotifications.style.display = 'block';
    }
}

// ============================================
// Show Toast
// ============================================
function showToast(type, message) {
    const toast = document.createElement('div');
    toast.className = `flash-message ${type}`;
    toast.style.position = 'fixed';
    toast.style.top = '80px';
    toast.style.right = '20px';
    toast.style.maxWidth = '400px';
    toast.style.zIndex = '9999';
    toast.style.animation = 'slideDown 0.4s ease';
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

console.log('🔔 Notifications module loaded successfully!');