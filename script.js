// Mobile navigation
const toggle = document.querySelector('.nav-toggle');
const links = document.getElementById('nav-links');

function setMenu(open) {
  toggle.setAttribute('aria-expanded', String(open));
  toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  links.classList.toggle('open', open);
}

toggle.addEventListener('click', () => {
  setMenu(toggle.getAttribute('aria-expanded') !== 'true');
});

links.addEventListener('click', (e) => {
  if (e.target.closest('a')) setMenu(false);
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && links.classList.contains('open')) {
    setMenu(false);
    toggle.focus();
  }
});

// Enquiry links preselect the topic (and, for workshops, start the message)
const topic = document.getElementById('topic');
const messageField = document.getElementById('message');

document.querySelectorAll('[data-topic]').forEach((link) => {
  link.addEventListener('click', () => {
    topic.value = link.dataset.topic;
    if (link.dataset.message && !messageField.value.trim()) {
      messageField.value = `${link.dataset.message}\n\n`;
    }
  });
});

// Contact form
// Delivery: set data-endpoint on the form to a Formspree (or compatible) form URL to send
// enquiries directly with an on-page confirmation. Without it, the visitor's email app opens.
const RECIPIENT = 'saifeddin.al-imamy@zu.ac.ae';

const form = document.getElementById('contact-form');
const endpoint = (form.dataset.endpoint || '').trim();
const note = document.getElementById('form-note');
const submitBtn = document.getElementById('submit-btn');
const success = document.getElementById('form-success');
const fallback = document.getElementById('fallback');
const fallbackText = document.getElementById('fallback-text');

if (!endpoint) {
  note.textContent = 'Sending opens your email app with your enquiry ready to send.';
}

function composeEnquiry(data) {
  const subject = `${data.topic} enquiry from ${data.name}`;
  const body = [
    `Name: ${data.name}`,
    `Email: ${data.email}`,
    data.organization ? `Organization: ${data.organization}` : null,
    `Interested in: ${data.topic}`,
    '',
    data.message,
  ].filter((line) => line !== null).join('\n');
  return { subject, body };
}

function showFallback(subject, body) {
  fallbackText.textContent = `Subject: ${subject}\n\n${body}`;
  fallback.hidden = false;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }

  const data = Object.fromEntries(new FormData(form));
  if (data._gotcha) return; // spam bot

  const { subject, body } = composeEnquiry(data);

  if (!endpoint) {
    window.location.href =
      `mailto:${RECIPIENT}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    showFallback(subject, body);
    note.textContent = 'Your email app should open with your enquiry ready to send.';
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = 'Sending…';
  note.textContent = '';

  try {
    const payload = new FormData(form);
    payload.set('_subject', subject);
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { Accept: 'application/json' },
      body: payload,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    form.reset();
    fallback.hidden = true;
    form.hidden = true;
    success.hidden = false;
    success.focus();
  } catch {
    note.textContent = `Your enquiry could not be sent. Please try again, or email ${RECIPIENT} directly.`;
    showFallback(subject, body);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Send enquiry';
  }
});

document.getElementById('form-reset').addEventListener('click', () => {
  success.hidden = true;
  form.hidden = false;
  topic.focus();
});

// Copy buttons
async function copyText(text, button, doneLabel) {
  const original = button.textContent;
  try {
    await navigator.clipboard.writeText(text);
    button.textContent = doneLabel;
  } catch {
    button.textContent = 'Select and copy';
  }
  setTimeout(() => { button.textContent = original; }, 2500);
}

document.querySelectorAll('[data-copy]').forEach((btn) => {
  btn.addEventListener('click', () => copyText(btn.dataset.copy, btn, 'Copied'));
});

document.getElementById('copy-message').addEventListener('click', (e) => {
  const range = document.createRange();
  range.selectNodeContents(fallbackText);
  const sel = window.getSelection();
  sel.removeAllRanges();
  sel.addRange(range);
  copyText(fallbackText.textContent, e.currentTarget, 'Copied');
});

document.getElementById('year').textContent = new Date().getFullYear();
