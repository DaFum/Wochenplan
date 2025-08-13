document.addEventListener('DOMContentLoaded', () => {
    'use strict';

    // GSAP animations for tab transitions
    const tabs = document.querySelectorAll('.nav-link');
    if (typeof gsap !== 'undefined') {
        tabs.forEach(tab => {
            tab.addEventListener('show.bs.tab', event => {
                const targetId = event.target.getAttribute('data-bs-target');
                const targetPane = document.querySelector(targetId);
                if (targetPane) {
                    gsap.fromTo(targetPane, { opacity: 0 }, { opacity: 1, duration: 0.5 });
                }
            });
        });
    }

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
        }, { passive: true });
        tabsElement.addEventListener('touchend', e => {
            touchendX = e.changedTouches[0].screenX;
            handleGesture();
        }, { passive: true });
    }

    // Dark mode toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', document.body.classList.contains('dark-mode') ? 'enabled' : 'disabled');
        });
    }

    // Apply saved dark mode preference
    if (localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark-mode');
    }

    // Search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', function () {
            const filter = this.value.toLowerCase();
            document.querySelectorAll('.search-item').forEach(item => {
                const text = item.textContent.toLowerCase();
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
                // Capture current order before drag
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
                    // Reset UI
                    prevOrder.forEach(el => taskList.appendChild(el));
                    alert('Failed to reorder tasks. Please try again.');
                }
            }
        });
    }

    // Asynchronous text generation
    const textGenForm = document.getElementById('textGenForm');
    if (textGenForm) {
        textGenForm.addEventListener('submit', async e => {
            e.preventDefault();
            const formData = new FormData(textGenForm);
            try {
                const response = await fetch(textGenForm.action, {
                    method: 'POST',
                    headers: { 'X-Requested-With': 'XMLHttpRequest' },
                    body: formData
                });
                const data = await response.json();
                if (response.ok && data.generated_text) {
                    const container = document.getElementById('generatedTextContainer');
                    const textEl = document.getElementById('generatedText');
                    if (container && textEl) {
                        textEl.textContent = data.generated_text;
                        container.style.display = '';
                        if (typeof confetti === 'function') {
                            confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });
                        }
                    }
                } else if (data.error) {
                    alert(data.error);
                } else {
                    alert('Fehler bei der Textgenerierung.');
                }
            } catch {
                alert('Fehler bei der Textgenerierung.');
            }
        });
    }

    // Load task suggestions from content library
    const subjectSelect = document.getElementById('learning_subject');
    const taskSuggestions = document.getElementById('taskSuggestions');

    async function loadTaskSuggestions() {
        if (!subjectSelect || !taskSuggestions) return;
        try {
            const resp = await fetch(`/api/library-tasks/${encodeURIComponent(subjectSelect.value)}`);
            if (!resp.ok) return;
            const data = await resp.json();
            taskSuggestions.innerHTML = '';
            data.tasks.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t;
                taskSuggestions.appendChild(opt);
            });
        } catch (e) {
            console.error('Failed to load suggestions', e);
        }
    }

    subjectSelect?.addEventListener('change', loadTaskSuggestions);
    loadTaskSuggestions();
});
