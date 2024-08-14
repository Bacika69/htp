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
