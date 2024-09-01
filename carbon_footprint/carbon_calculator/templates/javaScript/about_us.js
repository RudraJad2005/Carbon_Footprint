document.addEventListener("DOMContentLoaded", function() {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('show');
                observer.unobserve(entry.target); // Optional: Remove observer after animation
            }
        });
    }, observerOptions);

    const fadeElements = document.querySelectorAll('.fade-on-scroll');
    fadeElements.forEach(el => observer.observe(el));

    // Add scroll effects for other elements
    const scrollElements = document.querySelectorAll('.scroll-effect');
    const handleScroll = () => {
        scrollElements.forEach(el => {
            const scrollPosition = window.scrollY;
            const elementPosition = el.offsetTop;
            const elementHeight = el.offsetHeight;

            if (scrollPosition >= elementPosition - window.innerHeight && scrollPosition <= elementPosition + elementHeight) {
                el.classList.add('scroll-effect-active');
            } else {
                el.classList.remove('scroll-effect-active');
            }
        });
    };

    window.addEventListener('scroll', handleScroll);
});