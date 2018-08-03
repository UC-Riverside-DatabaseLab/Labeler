$(function() {
    $('input[name=post-format]').on('click init-post-format', function() {
        $('#gallery-box').toggle($('#post-format-gallery').prop('checked'));
    }).trigger('init-post-format');
});
