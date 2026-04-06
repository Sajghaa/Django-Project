// Comment System JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        document.querySelectorAll('.alert').forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            setTimeout(function() { bsAlert.close(); }, 5000);
        });
    }, 1000);
    
    // Like button functionality
    document.querySelectorAll('.like-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            var commentId = this.dataset.id;
            var likesSpan = this.querySelector('.likes-count');
            
            fetch('/comments/like/' + commentId + '/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                likesSpan.textContent = data.likes_count;
                if (data.liked) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });
        });
    });
    
    // Reply toggle functionality
    document.querySelectorAll('.reply-toggle').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            var commentId = this.dataset.id;
            var replyForm = document.getElementById('reply-form-' + commentId);
            replyForm.classList.toggle('d-none');
        });
    });
    
    // Cancel reply functionality
    document.querySelectorAll('.cancel-reply').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            var commentId = this.dataset.id;
            var replyForm = document.getElementById('reply-form-' + commentId);
            replyForm.classList.add('d-none');
        });
    });
    
    // Smooth scroll to comment
    if (window.location.hash && window.location.hash.startsWith('#comment-')) {
        var commentElement = document.querySelector(window.location.hash);
        if (commentElement) {
            setTimeout(function() {
                commentElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                commentElement.classList.add('bg-warning');
                setTimeout(function() {
                    commentElement.classList.remove('bg-warning');
                }, 2000);
            }, 500);
        }
    }
});

// Helper function to get CSRF token
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Copy to clipboard function
function copyToClipboard(text) {
    navigator.clipboard.writeText(text);
    showToast('Link copied to clipboard!', 'success');
}

// Show toast notification
function showToast(message, type) {
    var toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    var toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-' + (type === 'success' ? 'success' : 'danger') + ' border-0 show';
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    var bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    setTimeout(function() {
        toast.remove();
    }, 3000);
}