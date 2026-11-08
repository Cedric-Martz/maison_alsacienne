const button = document.querySelector('.menu');
const nav = document.querySelector('#navigation');
button?.addEventListener('click', () => {
  const open = button.getAttribute('aria-expanded') === 'true';
  button.setAttribute('aria-expanded', String(!open));
  nav.classList.toggle('open', !open);
});
nav?.addEventListener('click', event => {
  if (event.target.matches('a')) {
    nav.classList.remove('open');
    button.setAttribute('aria-expanded', 'false');
  }
});
const year = document.querySelector('#year');
if (year) year.textContent = new Date().getFullYear();

const archiveCards = [...document.querySelectorAll('.archive-card')];
document.querySelectorAll('[data-filter]').forEach(filter => filter.addEventListener('click', () => {
  document.querySelectorAll('[data-filter]').forEach(item => item.classList.remove('active'));
  filter.classList.add('active');
  archiveCards.forEach(card => {
    card.hidden = filter.dataset.filter !== 'all' && card.dataset.year !== filter.dataset.filter;
  });
}));

const lightbox = document.querySelector('.lightbox');
let lightboxLinks = [...document.querySelectorAll('[data-lightbox]')];
let currentImage = 0;
function showImage(index) {
  if (!lightboxLinks.length) return;
  currentImage = (index + lightboxLinks.length) % lightboxLinks.length;
  const link = lightboxLinks[currentImage];
  const description = link.querySelector('img').alt;
  const image = lightbox.querySelector('img');
  image.classList.remove('media-missing');
  image.src = link.getAttribute('href');
  image.alt = description;
  lightbox.querySelector('figcaption').textContent = description;
}
lightboxLinks.forEach((link, index) => link.addEventListener('click', event => {
  if (!lightbox?.showModal) return;
  event.preventDefault();
  showImage(index);
  lightbox.showModal();
}));
lightbox?.querySelector('.lightbox-close').addEventListener('click', () => lightbox.close());
lightbox?.querySelector('.lightbox-prev').addEventListener('click', () => showImage(currentImage - 1));
lightbox?.querySelector('.lightbox-next').addEventListener('click', () => showImage(currentImage + 1));
lightbox?.querySelector('img').addEventListener('error', () => {
  const brokenLink = lightboxLinks[currentImage];
  brokenLink?.closest('.archive-card')?.remove();
  lightboxLinks = [...document.querySelectorAll('[data-lightbox]')];
  window.dispatchEvent(new CustomEvent('mediaremoved', { detail: { galleryChanged: true, carouselChanged: false } }));
  lightbox.close();
});
lightbox?.addEventListener('click', event => { if (event.target === lightbox) lightbox.close(); });
document.addEventListener('keydown', event => {
  if (!lightbox?.open) return;
  if (event.key === 'ArrowLeft') showImage(currentImage - 1);
  if (event.key === 'ArrowRight') showImage(currentImage + 1);
});
window.addEventListener('mediaremoved', event => {
  if (event.detail.galleryChanged) lightboxLinks = [...document.querySelectorAll('[data-lightbox]')];
});

const carousel = document.querySelector('.carousel');
if (carousel) {
  let slides = [...carousel.querySelectorAll('.carousel-slide')];
  const count = carousel.querySelector('.carousel-count b');
  const toggle = carousel.querySelector('.carousel-toggle');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let currentSlide = 0;
  let paused = reduceMotion;
  let timer;
  const displaySlide = index => {
    if (!slides.length) return;
    slides[currentSlide].classList.remove('active');
    currentSlide = (index + slides.length) % slides.length;
    slides[currentSlide].classList.add('active');
    count.textContent = String(currentSlide + 1).padStart(2, '0');
  };
  const start = () => {
    clearInterval(timer);
    if (!paused && slides.length > 1) timer = setInterval(() => displaySlide(currentSlide + 1), 6000);
  };
  carousel.querySelector('.carousel-prev').addEventListener('click', () => { displaySlide(currentSlide - 1); start(); });
  carousel.querySelector('.carousel-next').addEventListener('click', () => { displaySlide(currentSlide + 1); start(); });
  toggle.addEventListener('click', () => {
    paused = !paused;
    toggle.setAttribute('aria-pressed', String(paused));
    toggle.setAttribute('aria-label', paused ? 'Relancer le carrousel' : 'Mettre le carrousel en pause');
    toggle.textContent = paused ? '▶' : 'Ⅱ';
    start();
  });
  if (reduceMotion) {
    toggle.setAttribute('aria-pressed', 'true');
    toggle.setAttribute('aria-label', 'Relancer le carrousel');
    toggle.textContent = '▶';
  }
  document.addEventListener('visibilitychange', () => document.hidden ? clearInterval(timer) : start());
  window.addEventListener('mediaremoved', event => {
    if (!event.detail.carouselChanged) return;
    slides = [...carousel.querySelectorAll('.carousel-slide')];
    if (!slides.length) {
      carousel.querySelector('.carousel-controls').hidden = true;
      return;
    }
    currentSlide = Math.min(currentSlide, Math.max(0, slides.length - 1));
    slides.forEach((slide, index) => slide.classList.toggle('active', index === currentSlide));
    carousel.querySelector('.carousel-count').innerHTML = `<b>${String(currentSlide + 1).padStart(2, '0')}</b> / ${String(slides.length).padStart(2, '0')}`;
    start();
  });
  start();
}
