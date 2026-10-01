// Mobile navigation
const toggle = document.querySelector('.nav-toggle');
const links = document.getElementById('nav-links');

toggle.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') === 'true';
  toggle.setAttribute('aria-expanded', String(!open));
  links.classList.toggle('open', !open);
});

links.addEventListener('click', (e) => {
  if (e.target.closest('a')) {
    toggle.setAttribute('aria-expanded', 'false');
    links.classList.remove('open');
  }
});

// "Work with me" buttons preselect the inquiry type
const topic = document.getElementById('topic');
document.querySelectorAll('[data-topic]').forEach((btn) => {
  btn.addEventListener('click', () => {
    topic.value = btn.dataset.topic;
  });
});

// Contact form: compose an email in the visitor's mail app.
// To receive submissions directly instead, set FORM_ENDPOINT to a
// Formspree (or similar) URL, e.g. 'https://formspree.io/f/xxxxxxx'.
const FORM_ENDPOINT = '';
const RECIPIENT = 'saifeddin.al-imamy@zu.ac.ae';

const form = document.getElementById('contact-form');
const note = document.getElementById('form-note');

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }

  const data = Object.fromEntries(new FormData(form));

  if (FORM_ENDPOINT) {
    try {
      const res = await fetch(FORM_ENDPOINT, {
        method: 'POST',
        headers: { Accept: 'application/json' },
        body: new FormData(form),
      });
      if (!res.ok) throw new Error(res.statusText);
      form.reset();
      note.textContent = 'Thank you — your message has been sent.';
    } catch {
      note.textContent = `Sorry, something went wrong. Please email ${RECIPIENT} directly.`;
    }
    return;
  }

  const subject = `${data.topic} inquiry from ${data.name}`;
  const body = [
    `Name: ${data.name}`,
    `Email: ${data.email}`,
    data.org ? `Organization: ${data.org}` : null,
    `Interest: ${data.topic}`,
    '',
    data.message,
  ].filter((line) => line !== null).join('\n');

  window.location.href =
    `mailto:${RECIPIENT}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;

  // If no email app opens, the visitor can copy the message instead.
  fallbackText.textContent = `Subject: ${subject}\n\n${body}`;
  fallback.hidden = false;
  note.textContent = 'Your email app should open with the message ready to send.';
});

const fallback = document.getElementById('fallback');
const fallbackText = document.getElementById('fallback-text');
document.getElementById('copy-message').addEventListener('click', async (e) => {
  try {
    await navigator.clipboard.writeText(fallbackText.textContent);
    e.target.textContent = 'Copied';
  } catch {
    const range = document.createRange();
    range.selectNodeContents(fallbackText);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
    e.target.textContent = 'Press Ctrl/⌘ + C to copy';
  }
});

document.getElementById('year').textContent = new Date().getFullYear();
