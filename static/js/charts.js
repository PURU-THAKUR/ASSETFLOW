// ============================================
// AssetFlow AI - Charts JavaScript
// Chart.js Configuration and Rendering
// ============================================

// Chart.js defaults
Chart.defaults.color = 'rgba(255,255,255,0.7)';
Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';
Chart.defaults.font.family = 'Inter, sans-serif';
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.pointStyle = 'circle';

// ============================================
// Department Chart
// ============================================
function initDepartmentChart(data) {
    const canvas = document.getElementById('departmentChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels || ['IT', 'HR', 'Finance', 'Marketing', 'Operations'],
            datasets: [{
                data: data.values || [45, 20, 30, 25, 15],
                backgroundColor: [
                    'rgba(108, 99, 255, 0.8)',
                    'rgba(0, 212, 255, 0.8)',
                    'rgba(255, 107, 107, 0.8)',
                    'rgba(0, 230, 118, 0.8)',
                    'rgba(255, 179, 0, 0.8)'
                ],
                borderColor: 'rgba(255,255,255,0.08)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        padding: 12,
                        usePointStyle: true,
                        pointStyle: 'circle',
                        color: 'rgba(255,255,255,0.7)'
                    }
                }
            },
            cutout: '70%'
        }
    });
}

// ============================================
// Health Chart
// ============================================
function initHealthChart(data) {
    const canvas = document.getElementById('healthChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels || ['Excellent', 'Good', 'Fair', 'Poor'],
            datasets: [{
                label: 'Assets',
                data: data.values || [120, 80, 30, 10],
                backgroundColor: [
                    'rgba(0, 230, 118, 0.7)',
                    'rgba(0, 212, 255, 0.7)',
                    'rgba(255, 179, 0, 0.7)',
                    'rgba(255, 23, 68, 0.7)'
                ],
                borderRadius: 8,
                barThickness: 40
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255,255,255,0.05)'
                    },
                    ticks: {
                        stepSize: 20,
                        color: 'rgba(255,255,255,0.5)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: 'rgba(255,255,255,0.5)'
                    }
                }
            }
        }
    });
}

// ============================================
// Report Chart
// ============================================
function initReportChart(type, data) {
    const canvas = document.getElementById('reportChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    let config = {
        type: type === 'pie' || type === 'doughnut' ? 'doughnut' : 'bar',
        data: {
            labels: data.labels || [],
            datasets: [{
                label: data.label || 'Count',
                data: data.values || [],
                backgroundColor: [
                    'rgba(108, 99, 255, 0.8)',
                    'rgba(0, 212, 255, 0.8)',
                    'rgba(255, 107, 107, 0.8)',
                    'rgba(0, 230, 118, 0.8)',
                    'rgba(255, 179, 0, 0.8)',
                    'rgba(156, 39, 176, 0.8)',
                    'rgba(255, 152, 0, 0.8)',
                    'rgba(76, 175, 80, 0.8)',
                    'rgba(33, 150, 243, 0.8)',
                    'rgba(244, 67, 54, 0.8)'
                ],
                borderColor: 'rgba(255,255,255,0.08)',
                borderWidth: 2,
                borderRadius: type === 'pie' ? 0 : 6,
                barThickness: type === 'pie' ? undefined : 35
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: type === 'pie' ? 'right' : 'top',
                    labels: {
                        padding: 12,
                        usePointStyle: true,
                        pointStyle: 'circle',
                        color: 'rgba(255,255,255,0.7)'
                    }
                }
            },
            scales: type === 'pie' ? {} : {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255,255,255,0.05)'
                    },
                    ticks: {
                        color: 'rgba(255,255,255,0.5)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: 'rgba(255,255,255,0.5)'
                    }
                }
            }
        }
    };
    
    new Chart(ctx, config);
}

// ============================================
// Initialize Charts on Page Load
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    // Department Chart
    fetch('/api/charts/department')
        .then(response => response.json())
        .then(data => initDepartmentChart(data))
        .catch(() => initDepartmentChart({}));
    
    // Health Chart
    fetch('/api/charts/health')
        .then(response => response.json())
        .then(data => initHealthChart(data))
        .catch(() => initHealthChart({}));
});

console.log('📊 Charts loaded successfully!');