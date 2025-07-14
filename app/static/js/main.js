document.addEventListener('DOMContentLoaded', function() {
    // GSAP animations for tab transitions
    const tabs = document.querySelectorAll('.nav-link');
    tabs.forEach(tab => {
        tab.addEventListener('show.bs.tab', function(event) {
            gsap.fromTo(event.target, { opacity: 0 }, { opacity: 1, duration: 0.5 });
        });
    });

    // Swipe gestures for mobile devices
    let touchstartX = 0;
    let touchendX = 0;
    const tabsElement = document.getElementById('weekdaysTabs');

 function handleGesture() {
     const swipeThreshold = 50; // Minimum pixels for a swipe
     if (touchendX < touchstartX - swipeThreshold) {
         const activeTab = document.querySelector('.nav-link.active');
         const nextTab = activeTab?.parentElement?.nextElementSibling;
         nextTab?.querySelector('.nav-link')?.click();
     }
     if (touchendX > touchstartX + swipeThreshold) {
         const activeTab = document.querySelector('.nav-link.active');
         const prevTab = activeTab?.parentElement?.previousElementSibling;
         prevTab?.querySelector('.nav-link')?.click();
     }
 }

    if (tabsElement) {
        tabsElement.addEventListener('touchstart', e => {
            touchstartX = e.changedTouches[0].screenX;
        });

        tabsElement.addEventListener('touchend', e => {
            touchendX = e.changedTouches[0].screenX;
            handleGesture();
        });
    }

    // Dark mode toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            // Save preference in local storage
            if (document.body.classList.contains('dark-mode')) {
                localStorage.setItem('darkMode', 'enabled');
            } else {
                localStorage.setItem('darkMode', 'disabled');
            }
        });
    }

    // Check for saved dark mode preference
    if (localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark-mode');
    }

    // Search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            let filter = this.value.toLowerCase();
            document.querySelectorAll('.search-item').forEach(function(item) {
                let text = item.textContent.toLowerCase();
                item.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    }
});
