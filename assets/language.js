(function () {
  const siteBase = document.querySelector('meta[name="maison-site-base"]')?.content.replace(/\/$/, '') || '';
  document.addEventListener('error', function (event) {
    if (!(event.target instanceof HTMLImageElement)) return;
    const image = event.target;
    image.classList.add('media-missing');
    const removable = image.closest('.archive-card, .carousel-slide');
    if (removable) {
      const galleryChanged = removable.classList.contains('archive-card');
      const carouselChanged = removable.classList.contains('carousel-slide');
      removable.remove();
      if (galleryChanged) {
        requestAnimationFrame(function () {
          const cards = [...document.querySelectorAll('.archive-card')];
          const total = cards.length;
          const totalLabel = document.querySelector('[data-filter="all"] span');
          if (totalLabel) totalLabel.textContent = total;
          document.querySelectorAll('[data-filter]:not([data-filter="all"])').forEach(function (filter) {
            filter.querySelector('span').textContent = cards.filter(card => card.dataset.year === filter.dataset.filter).length;
          });
          const headingCount = document.querySelector('.archive-intro strong');
          if (headingCount?.firstChild) headingCount.firstChild.nodeValue = total;
        });
      }
      window.dispatchEvent(new CustomEvent('mediaremoved', { detail: { galleryChanged, carouselChanged } }));
    }
  }, true);

  const supported = ['fr', 'de', 'en', 'es'];
  const pathname = siteBase && (window.location.pathname === siteBase || window.location.pathname.startsWith(siteBase + '/'))
    ? window.location.pathname.slice(siteBase.length)
    : window.location.pathname;
  const pathParts = pathname.split('/').filter(Boolean);
  const pathLocale = supported.includes(pathParts[0]) ? pathParts[0] : null;
  const unknownLocale = !pathLocale && /^[a-z]{2}$/i.test(pathParts[0] || '') ? pathParts[0].toLowerCase() : null;
  const currentLocale = pathLocale || 'fr';
  const page = pathLocale ? (pathParts.slice(1).join('/') || 'index.html') : (pathParts.at(-1) || 'index.html');
  const preferenceKey = 'maison-alsacienne-language';

  function closestLocale(languages) {
    for (const language of languages) {
      const code = String(language).toLowerCase();
      const primary = code.split('-')[0];
      if (supported.includes(primary)) return primary;
      if (['gsw', 'lb', 'af', 'da', 'no', 'sv'].includes(primary)) return 'de';
      if (['ca', 'gl', 'eu', 'ro'].includes(primary)) return 'es';
      if (primary === 'oc') return 'fr';
    }
    return 'en';
  }

  function urlFor(locale) {
    const suffix = page === 'index.html' ? '' : page;
    const route = locale === 'fr' ? `/${suffix}` : `/${locale}/${suffix}`;
    return siteBase + route;
  }

  const stored = localStorage.getItem(preferenceKey);
  if (!pathLocale && page !== 'mentions-legales.html') {
    const detected = unknownLocale ? 'en' : (supported.includes(stored) ? stored : closestLocale(navigator.languages || [navigator.language]));
    if (detected !== 'fr') {
      window.location.replace(urlFor(detected) + window.location.search + window.location.hash);
      return;
    }
  }

  const messages = {
    en: 'You’re viewing the English version of this website.',
    de: 'Sie sehen die deutsche Version dieser Website.',
    es: 'Estás viendo la versión española de este sitio.'
  };
  const original = {
    en: 'View the original French version',
    de: 'Französisches Original anzeigen',
    es: 'Ver la versión original en francés'
  };

  window.addEventListener('DOMContentLoaded', function () {
    const footer = document.querySelector('footer .wrap');
    if (!footer) return;
    const block = document.createElement('div');
    block.className = 'language-footer';
    if (currentLocale !== 'fr') {
      const note = document.createElement('p');
      note.className = 'language-note';
      note.append(messages[currentLocale] + ' ');
      const link = document.createElement('a');
      link.href = urlFor('fr');
      link.textContent = original[currentLocale];
      link.dataset.language = 'fr';
      note.append(link, '.');
      block.append(note);
    }
    const choices = document.createElement('nav');
    choices.className = 'language-switcher';
    choices.setAttribute('aria-label', currentLocale === 'fr' ? 'Choisir la langue' : 'Choose language');
    const labels = { fr: 'FR', de: 'DE', en: 'EN', es: 'ES' };
    supported.forEach(function (locale) {
      const link = document.createElement('a');
      link.href = urlFor(locale);
      link.hreflang = locale;
      link.lang = locale;
      link.textContent = labels[locale];
      link.dataset.language = locale;
      if (locale === currentLocale) link.setAttribute('aria-current', 'true');
      choices.append(link);
    });
    block.append(choices);
    footer.append(block);
    block.addEventListener('click', function (event) {
      const link = event.target.closest('[data-language]');
      if (link) localStorage.setItem(preferenceKey, link.dataset.language);
    });
  });
}());
