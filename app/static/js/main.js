document.addEventListener('DOMContentLoaded', function() {
    // GSAP animations for tab transitions
    const tabs = document.querySelectorAll('.nav-link');
    tabs.forEach(tab => {
        tab.addEventListener('show.bs.tab', function(event) {
            const targetId = event.target.getAttribute('data-bs-target');
            const targetPane = document.querySelector(targetId);
            if (targetPane) {
                gsap.fromTo(targetPane, { opacity: 0 }, { opacity: 1, duration: 0.5 });
            }
        });
    });

    // Swipe gestures for mobile devices
    let touchstartX = 0;
    let touchendX = 0;
    const tabsElement = document.getElementById('weekdaysTabs');

 /**
  * Erkennt horizontale Wischgesten und aktiviert entsprechend den nächsten oder vorherigen Tab.
  *
  * Erkennt einen Wisch nach links oder rechts anhand eines Schwellenwerts und löst einen Tabwechsel aus, indem der nächste oder vorherige Tab per Klick aktiviert wird.
  */
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

// Check for saved dark mode preference immediately
if (localStorage.getItem('darkMode') === 'enabled') {
    document.body.classList.add('dark-mode');
}

document.addEventListener('DOMContentLoaded', function() {
    // GSAP animations for tab transitions
    // ... rest of code ...
});

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

    // Drag-and-drop reordering for tasks
    const taskList = document.getElementById('taskList');
    if (taskList && typeof Sortable !== 'undefined') {
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        let prevOrder = [];
        new Sortable(taskList, {
            animation: 150,
            onStart: () => {
                // Reihenfolge VOR dem Drag erfassen (echter vorheriger Zustand)
                prevOrder = Array.from(taskList.children);
            },
            onEnd: async () => {
                const items = Array.from(taskList.children);
                const headers = {
                    'Content-Type': 'application/json',
                    ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {})
                };
                const requests = items.map((el, index) => {
                    const id = el.getAttribute('data-id');
                    return fetch(`/task/${id}/reorder`, {
                        method: 'POST',
                        headers,
                        body: JSON.stringify({ position: index })
                    });
                });
                const results = await Promise.all(requests.map(p => p.catch(e => e)));
                const hasError = results.some(r => r instanceof Error || (r && !r.ok));
                if (hasError) {
                    // UI zurücksetzen
                    prevOrder.forEach(el => taskList.appendChild(el));
                    alert('Failed to reorder tasks. Please try again.');
                }
            }
        });
    }
});
