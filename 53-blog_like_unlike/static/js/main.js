// Like/Unlike post via AJAX
$(document).on('click', '.like-post-btn', function(e) {
    e.preventDefault();
    const slug = $(this).data('slug');
    const btn = $(this);
    $.ajax({
        url: `/post/${slug}/like/`,
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        success: function(data) {
            const icon = btn.find('i');
            const count = btn.find('.like-count');
            count.text(data.likes_count);
            if (data.liked) {
                icon.removeClass('far').addClass('fas text-red-500');
            } else {
                icon.removeClass('fas text-red-500').addClass('far');
            }
        }
    });
});

// Like/Unlike comment
$(document).on('click', '.like-comment-btn', function(e) {
    e.preventDefault();
    const commentId = $(this).data('comment-id');
    const btn = $(this);
    $.ajax({
        url: `/comment/${commentId}/like/`,
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        success: function(data) {
            const icon = btn.find('i');
            const count = btn.find('.comment-like-count');
            count.text(data.likes_count);
            if (data.liked) {
                icon.removeClass('far').addClass('fas text-red-500');
            } else {
                icon.removeClass('fas text-red-500').addClass('far');
            }
        }
    });
});

// CKEditor for rich text
if (document.querySelector('.rich-text-editor')) {
    ClassicEditor
        .create(document.querySelector('.rich-text-editor'))
        .catch(error => console.error(error));
}

// Select2 for tags
if (document.querySelector('.tag-select')) {
    $('.tag-select').select2({
        tags: true,
        tokenSeparators: [',', ' '],
        placeholder: 'Add tags'
    });
}