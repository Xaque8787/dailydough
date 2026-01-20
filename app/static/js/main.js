console.log('Management System loaded');

document.addEventListener('DOMContentLoaded', function() {
    const navbarToggle = document.getElementById('navbarToggle');
    const navLinks = document.getElementById('navLinks');

    if (navbarToggle && navLinks) {
        navbarToggle.addEventListener('click', function() {
            navbarToggle.classList.toggle('active');
            navLinks.classList.toggle('active');
        });

        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    navbarToggle.classList.remove('active');
                    navLinks.classList.remove('active');
                }
            });
        });
    }
});
