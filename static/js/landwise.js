/**
 * LANDWISE — National Digital Platform for Research, Policy Innovation,
 * and Evidence-Based Land Governance.
 * Client Interactivity & Visual Dynamics
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Sticky Navbar on Scroll
  const navbar = document.querySelector('.lw-navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 20) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    });
  }

  // 2. Animated Counter for Impact Stats
  const statNumbers = document.querySelectorAll('.lw-stat-number');
  if ('IntersectionObserver' in window && statNumbers.length > 0) {
    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          const targetText = el.getAttribute('data-target') || el.innerText;
          const match = targetText.match(/^([\d,]+)(\+?.*)$/);
          if (match) {
            const rawNumber = parseInt(match[1].replace(/,/g, ''), 10);
            const suffix = match[2] || '';
            let start = 0;
            const duration = 1400;
            const stepTime = 25;
            const steps = duration / stepTime;
            const increment = rawNumber / steps;

            const timer = setInterval(() => {
              start += increment;
              if (start >= rawNumber) {
                el.innerText = rawNumber.toLocaleString() + suffix;
                clearInterval(timer);
              } else {
                el.innerText = Math.floor(start).toLocaleString() + suffix;
              }
            }, stepTime);
          }
          obs.unobserve(el);
        }
      });
    }, { threshold: 0.3 });

    statNumbers.forEach(el => observer.observe(el));
  }

  // 3. Floating Badges Micro-interaction
  const badges = document.querySelectorAll('.lw-floating-badge');
  badges.forEach((badge, index) => {
    badge.style.animationDelay = `${index * 0.15}s`;
  });
});

