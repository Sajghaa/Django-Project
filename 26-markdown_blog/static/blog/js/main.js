let autoSaveTimer;

function autoSave() {
    clearTimeout(autoSaveTimer);
    autoSaveTimer = setTimeout(() => {
        const form = document.querySelector('form');
        if (form && form.querySelector('textarea[name="content"]')) {
            const formData = new FormData(form);
            fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            }).catch(error => console.log('Auto-save error:', error));
        }
    }, 30000); // Auto-save every 30 seconds
}

// Add event listeners for markdown preview
if (document.querySelector('textarea[name="content"]')) {
    const textarea = document.querySelector('textarea[name="content"]');
    textarea.addEventListener('input', autoSave);
    
    // Add preview functionality
    const previewButton = document.createElement('button');
    previewButton.textContent = 'Preview';
    previewButton.className = 'btn btn-info btn-sm mb-2';
    previewButton.type = 'button';
    textarea.parentNode.insertBefore(previewButton, textarea);
    
    previewButton.addEventListener('click', () => {
        const content = textarea.value;
        const previewDiv = document.createElement('div');
        previewDiv.className = 'markdown-preview mt-3';
        
        fetch('/preview-markdown/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ content: content })
        })
        .then(response => response.json())
        .then(data => {
            previewDiv.innerHTML = data.html;
            if (document.querySelector('.markdown-preview')) {
                document.querySelector('.markdown-preview').remove();
            }
            textarea.parentNode.insertBefore(previewDiv, textarea.nextSibling);
        });
    });
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}