// NestFind — Main JS

// Auto-dismiss flash messages
document.querySelectorAll('.flash').forEach(el => {
  setTimeout(() => el.style.opacity = '0', 4000);
  setTimeout(() => el.remove(), 4500);
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
  });
});

// Active nav link highlight
const path = window.location.pathname;
document.querySelectorAll('.nav-link').forEach(link => {
  if (link.getAttribute('href') === path) link.style.color = 'var(--terracotta)';
});

// Property card hover effect
document.querySelectorAll('.property-card').forEach(card => {
  card.addEventListener('mouseenter', () => card.style.transform = 'translateY(-6px)');
  card.addEventListener('mouseleave', () => card.style.transform = '');
});

// Search form auto-submit on select change
const filterForm = document.getElementById('filter-form');
if (filterForm) {
  filterForm.querySelectorAll('select').forEach(sel => {
    sel.addEventListener('change', () => filterForm.submit());
  });
}
