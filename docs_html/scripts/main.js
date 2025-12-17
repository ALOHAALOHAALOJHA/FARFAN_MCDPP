document.addEventListener('DOMContentLoaded', () => {
    // Entrance animations for feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach((card, index) => {
        card.style.animation = `fadeInUp 0.5s ease-out ${index * 0.2}s forwards`;
        card.style.opacity = 0; // Start hidden
    });

    // Add more interactivity here based on the protocol...
});
