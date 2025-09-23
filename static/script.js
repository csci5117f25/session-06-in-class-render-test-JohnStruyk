addEventListener('DOMContentLoaded', function() {
    const button = document.getElementById('myButton');
    const message = document.getElementById('myMessage');

    button.addEventListener('click', function() {
        message.style.display = 'block';
    });
});
