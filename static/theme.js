document.addEventListener('DOMContentLoaded', () => {
    const themeToggleCheckbox = document.getElementById('theme-toggle'); // Checkbox for the slider
    const body = document.body;

    // Load the saved theme preference
    const savedTheme = localStorage.getItem('theme') || 'light-mode';
    body.classList.add(savedTheme);

    // Set checkbox state based on saved theme
    themeToggleCheckbox.checked = savedTheme === 'dark-mode';

    // Toggle theme on checkbox change
    themeToggleCheckbox.addEventListener('change', () => {
        const newTheme = themeToggleCheckbox.checked ? 'dark-mode' : 'light-mode';

        // Apply the new theme to the body
        body.classList.remove('light-mode', 'dark-mode');
        body.classList.add(newTheme);

        // Save theme preference to localStorage
        localStorage.setItem('theme', newTheme);

        // Optional: Adjust card styles when switching theme
        document.querySelectorAll('.pathway-card').forEach(card => {
            card.classList.toggle('bg-dark', newTheme === 'dark-mode');
            card.classList.toggle('text-white', newTheme === 'dark-mode');
        });
    });
});
