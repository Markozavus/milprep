document.addEventListener("DOMContentLoaded", () => {
    const cards = Array.from(document.querySelectorAll(".review-card"));
    const dots = Array.from(document.querySelectorAll(".reviews-dots .dot"));

    if (!cards.length || !dots.length) return;

    let currentIndex = 0;
    const intervalMs = 5000; // כל 5 שניות מחליפים חוות דעת

    function showReview(index) {
        cards.forEach((card, i) => {
            card.classList.toggle("active", i === index);
        });
        dots.forEach((dot, i) => {
            dot.classList.toggle("active", i === index);
        });
        currentIndex = index;
    }

    // אוטומטי
    let sliderInterval = setInterval(() => {
        const nextIndex = (currentIndex + 1) % cards.length;
        showReview(nextIndex);
    }, intervalMs);

    // מעבר לפי לחיצה על הנקודות
    dots.forEach(dot => {
        dot.addEventListener("click", () => {
            const index = Number(dot.dataset.index);
            showReview(index);

            // איפוס הטיימר כדי שהמשתמש יוכל לראות יותר זמן
            clearInterval(sliderInterval);
            sliderInterval = setInterval(() => {
                const nextIndex = (currentIndex + 1) % cards.length;
                showReview(nextIndex);
            }, intervalMs);
        });
    });
});
