// ============================================
// AssetFlow AI - Assets JavaScript
// CRUD Operations and Interactions
// ============================================

// ============================================
// Asset CRUD Operations
// ============================================

function openAddAssetModal() {
    const modal = document.getElementById('addAssetModal');
    if (modal) modal.classList.add('show');
}

function closeAddAssetModal() {
    const modal = document.getElementById('addAssetModal');
    if (modal) modal.classList.remove('show');
}

function viewAsset(id) {
    window.location.href = `/assets/view/${id}`;
}

function editAsset(id) {
    window.location.href = `/assets/edit/${id}`;
}

function deleteAsset(id) {
    if (!confirm('Are you sure you want to delete this asset?')) return;
    
    fetch(`/assets/delete/${id}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('success', 'Asset deleted successfully!');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showToast('error', data.error || 'Error deleting asset');
            }
        })
        .catch(() => showToast('error', 'Error deleting asset'));
}

// ============================================
// Allocation Functions
// ============================================

function openAllocateModal() {
    const modal = document.getElementById('allocateModal');
    if (modal) modal.classList.add('show');
}

function closeAllocateModal() {
    const modal = document.getElementById('allocateModal');
    if (modal) modal.classList.remove('show');
}

function transferAsset(id) {
    window.location.href = `/allocation/transfer/${id}`;
}

function returnAsset(id) {
    if (!confirm('Confirm return of this asset?')) return;
    
    fetch(`/allocation/return/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'condition=Good'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('success', 'Asset returned successfully!');
            setTimeout(() => window.location.reload(), 1000);
        } else {
            showToast('error', data.error || 'Error returning asset');
        }
    })
    .catch(() => showToast('error', 'Error returning asset'));
}

// ============================================
// Booking Functions
// ============================================

function openBookingModal() {
    const modal = document.getElementById('bookingModal');
    if (modal) modal.classList.add('show');
}

function closeBookingModal() {
    const modal = document.getElementById('bookingModal');
    if (modal) modal.classList.remove('show');
}

function cancelBooking(id) {
    if (!confirm('Cancel this booking?')) return;
    
    fetch(`/booking/cancel/${id}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('success', 'Booking cancelled successfully!');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showToast('error', data.error || 'Error cancelling booking');
            }
        })
        .catch(() => showToast('error', 'Error cancelling booking'));
}

// ============================================
// Maintenance Functions
// ============================================

function openMaintenanceModal() {
    const modal = document.getElementById('maintenanceModal');
    if (modal) modal.classList.add('show');
}

function closeMaintenanceModal() {
    const modal = document.getElementById('maintenanceModal');
    if (modal) modal.classList.remove('show');
}

function approveMaintenance(id) {
    fetch(`/maintenance/approve/${id}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('success', 'Maintenance approved!');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showToast('error', data.error || 'Error approving maintenance');
            }
        })
        .catch(() => showToast('error', 'Error approving maintenance'));
}

function completeMaintenance(id) {
    const resolution = prompt('Enter resolution details:');
    if (resolution === null) return;
    
    fetch(`/maintenance/complete/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'resolution=' + encodeURIComponent(resolution)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('success', 'Maintenance completed!');
            setTimeout(() => window.location.reload(), 1000);
        } else {
            showToast('error', data.error || 'Error completing maintenance');
        }
    })
    .catch(() => showToast('error', 'Error completing maintenance'));
}

function deleteMaintenance(id) {
    if (!confirm('Delete this maintenance request?')) return;
    
    fetch(`/maintenance/delete/${id}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('success', 'Maintenance request deleted!');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showToast('error', data.error || 'Error deleting maintenance');
            }
        })
        .catch(() => showToast('error', 'Error deleting maintenance'));
}

// ============================================
// QR Code Generation
// ============================================

function generateQR(id) {
    fetch(`/qr/generate/${id}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('success', 'QR Code generated successfully! 📱');
                // Show QR code in a modal
                const modal = document.createElement('div');
                modal.className = 'modal show';
                modal.innerHTML = `
                    <div class="modal-content glass" style="max-width: 400px;">
                        <div class="modal-header">
                            <h2>QR Code</h2>
                            <button onclick="this.closest('.modal').remove()">✕</button>
                        </div>
                        <div style="text-align: center;">
                            <img src="${data.qr_code}" alt="QR Code" style="max-width: 100%; border-radius: 12px;">
                            <p style="margin-top: 12px; color: var(--text-secondary);">
                                Scan to view asset details
                            </p>
                            <a href="${data.qr_path}" download class="btn-primary" style="margin-top: 12px;">
                                📥 Download QR
                            </a>
                        </div>
                    </div>
                `;
                document.body.appendChild(modal);
            } else {
                showToast('error', data.error || 'Error generating QR code');
            }
        })
        .catch(() => showToast('error', 'Error generating QR code'));
}

// ============================================
// View Toggle (Grid/List)
// ============================================

function setView(view) {
    const grid = document.getElementById('assetsGrid');
    const btns = document.querySelectorAll('.view-btn');
    
    btns.forEach(btn => btn.classList.remove('active'));
    
    if (view === 'grid') {
        grid.style.display = 'grid';
        grid.style.flexDirection = '';
        document.querySelector('.view-btn:first-child')?.classList.add('active');
    } else {
        grid.style.display = 'flex';
        grid.style.flexDirection = 'column';
        document.querySelector('.view-btn:last-child')?.classList.add('active');
    }
}

// ============================================
// Filter Assets
// ============================================

function filterAssets() {
    const category = document.getElementById('categoryFilter')?.value || '';
    const status = document.getElementById('statusFilter')?.value || '';
    const department = document.getElementById('departmentFilter')?.value || '';
    
    document.querySelectorAll('.asset-card').forEach(card => {
        let show = true;
        if (category && card.dataset.category !== category) show = false;
        if (status && card.dataset.status !== status) show = false;
        if (department && card.dataset.department !== department) show = false;
        card.style.display = show ? 'block' : 'none';
    });
}

// ============================================
// Search Assets
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchAssets');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            document.querySelectorAll('.asset-card').forEach(card => {
                const name = card.querySelector('h3')?.textContent?.toLowerCase() || '';
                const tag = card.querySelector('.asset-tag')?.textContent?.toLowerCase() || '';
                const visible = name.includes(query) || tag.includes(query);
                card.style.display = visible ? 'block' : 'none';
            });
        });
    }
    
    // Filter change listeners
    ['categoryFilter', 'statusFilter', 'departmentFilter'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('change', filterAssets);
        }
    });
});

// ============================================
// Settings Functions
// ============================================

function showTab(tabId) {
    document.querySelectorAll('.settings-content').forEach(el => {
        el.style.display = 'none';
    });
    document.querySelectorAll('.tab-btn').forEach(el => {
        el.classList.remove('active');
    });
    
    const content = document.getElementById(`tab-${tabId}`);
    if (content) content.style.display = 'block';
    
    document.querySelector(`.tab-btn[onclick*="${tabId}"]`)?.classList.add('active');
}

function deleteDepartment(id) {
    if (!confirm('Delete this department?')) return;
    
    fetch(`/settings/department/delete/${id}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('success', 'Department deleted!');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showToast('error', data.error || 'Error deleting department');
            }
        })
        .catch(() => showToast('error', 'Error deleting department'));
}

function deleteCategory(id) {
    if (!confirm('Delete this category?')) return;
    
    fetch(`/settings/category/delete/${id}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('success', 'Category deleted!');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showToast('error', data.error || 'Error deleting category');
            }
        })
        .catch(() => showToast('error', 'Error deleting category'));
}

// ============================================
// Toast Notifications
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

console.log('💻 Assets module loaded successfully!');