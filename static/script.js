document.addEventListener('DOMContentLoaded', function () {

    var bodyId = document.body.id;

    if (bodyId === 'home') {
        document.getElementsByClassName('nav-container')[0].style.background = 'transparent';
        window.addEventListener('scroll', function() {
            const scrollPosition = window.scrollY || window.pageYOffset;
            console.log('Current scroll position:', scrollPosition);

            const navbar = document.querySelector('.nav-container');
            if (scrollPosition > 530) {
                navbar.style.background = 'rgb(10,66,93)';
            } else{
                navbar.style.background = 'transparent';
            }
        });
        
    }
});

document.addEventListener("DOMContentLoaded", function() {
    const lazyElements = document.querySelectorAll('.lazy-load');

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target); // Ha már betöltődött, nem kell tovább figyelni
            }
        });
    });

    lazyElements.forEach(element => {
        observer.observe(element);
    });
});


