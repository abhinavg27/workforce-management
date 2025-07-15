// Global JavaScript for Confluence AI Application

// Global variables
let currentUser = 'default';
let appConfig = {
    apiBaseUrl: '',
    enableNotifications: true,
    enableAnalytics: true
};

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupGlobalEventListeners();
    checkSystemStatus();
});

function initializeApp() {
    console.log('🚀 Initializing Confluence AI Application');

    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    console.log('✅ Application initialized successfully');
}

function setupGlobalEventListeners() {
    // Global error handler
    window.addEventListener('error', function(e) {
        console.error('Global error:', e.error);
        showNotification('An unexpected error occurred', 'error');
    });

    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', function(e) {
        console.error('Unhandled promise rejection:', e.reason);
        showNotification('A network error occurred', 'error');
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(alert => {
            if (alert.querySelector('.btn-close')) {
                setTimeout(() => {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }, 5000);
            }
        });
    }, 100);
}

function checkSystemStatus() {
    fetch('/agent_status')
        .then(response => response.json())
        .then(data => {
            console.log('✅ System status check passed');
            updateSystemStatusIndicator(true);
        })
        .catch(error => {
            console.warn('⚠️ System status check failed:', error);
            updateSystemStatusIndicator(false);
        });
}

function updateSystemStatusIndicator(isOnline) {
    const indicator = document.getElementById('system-status-indicator');
    if (indicator) {
        indicator.className = isOnline ? 'badge bg-success' : 'badge bg-danger';
        indicator.textContent = isOnline ? 'Online' : 'Offline';
    }
}

// Utility Functions
function showNotification(message, type = 'info', duration = 5000) {
    if (!appConfig.enableNotifications) return;

    // Browser notification
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('Confluence AI', {
            body: message,
            icon: '/static/images/favicon.ico'
        });
    }

    // In-app notification
    showToast(message, type, duration);
}

function showToast(message, type = 'info', duration = 5000) {
    const toastContainer = getOrCreateToastContainer();

    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${getBootstrapColorClass(type)} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas ${getIconClass(type)}"></i> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHtml);

    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: duration });
    toast.show();

    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

function getOrCreateToastContainer() {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    return container;
}

function getBootstrapColorClass(type) {
    const colorMap = {
        'success': 'success',
        'error': 'danger',
        'warning': 'warning',
        'info': 'info'
    };
    return colorMap[type] || 'info';
}

function getIconClass(type) {
    const iconMap = {
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-circle',
        'warning': 'fa-exclamation-triangle',
        'info': 'fa-info-circle'
    };
    return iconMap[type] || 'fa-info-circle';
}

// API Helper Functions
function makeApiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        }
    };

    const mergedOptions = { ...defaultOptions, ...options };

    return fetch(url, mergedOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

function handleApiError(error, context = '') {
    console.error(`API Error ${context}:`, error);

    let message = 'An error occurred';
    if (error.message.includes('Failed to fetch')) {
        message = 'Network connection error. Please check your internet connection.';
    } else if (error.message.includes('HTTP error')) {
        message = 'Server error. Please try again later.';
    } else {
        message = error.message || 'Unknown error occurred';
    }

    showNotification(message, 'error');
    return { success: false, error: message };
}

// Form Utilities
function serializeForm(form) {
    const formData = new FormData(form);
    const data = {};

    for (let [key, value] of formData.entries()) {
        if (data[key]) {
            // Handle multiple values (checkboxes, etc.)
            if (Array.isArray(data[key])) {
                data[key].push(value);
            } else {
                data[key] = [data[key], value];
            }
        } else {
            data[key] = value;
        }
    }

    return data;
}

function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Loading States
function showLoadingState(element, text = 'Loading...') {
    const originalContent = element.innerHTML;
    element.dataset.originalContent = originalContent;

    element.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2" role="status"></span>
        ${text}
    `;
    element.disabled = true;
}

function hideLoadingState(element) {
    if (element.dataset.originalContent) {
        element.innerHTML = element.dataset.originalContent;
        delete element.dataset.originalContent;
    }
    element.disabled = false;
}

// Local Storage Utilities
function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
        return true;
    } catch (error) {
        console.error('Failed to save to localStorage:', error);
        return false;
    }
}

function loadFromLocalStorage(key, defaultValue = null) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : defaultValue;
    } catch (error) {
        console.error('Failed to load from localStorage:', error);
        return defaultValue;
    }
}

// Analytics (if enabled)
function trackEvent(eventName, properties = {}) {
    if (!appConfig.enableAnalytics) return;

    console.log('📊 Analytics Event:', eventName, properties);

    // Here you could integrate with analytics services like Google Analytics, Mixpanel, etc.
    // Example:
    // gtag('event', eventName, properties);
}

// Copy to Clipboard
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(text).then(() => {
            showNotification('Copied to clipboard!', 'success', 2000);
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        try {
            document.execCommand('copy');
            showNotification('Copied to clipboard!', 'success', 2000);
        } catch (error) {
            console.error('Failed to copy:', error);
            showNotification('Failed to copy to clipboard', 'error');
        } finally {
            textArea.remove();
        }
    }
}

// Format utilities
function formatDate(date, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };

    const mergedOptions = { ...defaultOptions, ...options };
    return new Intl.DateTimeFormat('en-US', mergedOptions).format(new Date(date));
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Export global functions
window.ConfluenceAI = {
    showNotification,
    showToast,
    makeApiRequest,
    handleApiError,
    serializeForm,
    validateForm,
    showLoadingState,
    hideLoadingState,
    saveToLocalStorage,
    loadFromLocalStorage,
    trackEvent,
    copyToClipboard,
    formatDate,
    formatFileSize
};

console.log('📚 Confluence AI JavaScript library loaded');
