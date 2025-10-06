// CSRF helper for AJAX
function getCookie(name) {
  if (!document.cookie) return null;
  const xs = document.cookie.split(';').map(c => c.trim());
  for (const c of xs) {
    if (c.startsWith(name + '=')) return decodeURIComponent(c.split('=').slice(1).join('='));
  }
  return null;
}
const csrftoken = getCookie('csrftoken');

async function postJSON(url, data) {
  const res = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrftoken},
    body: JSON.stringify(data || {})
  });
  return res.json().then(j => ({ok: res.ok, status: res.status, json: j}));
}

document.addEventListener('click', async (e) => {
  const btn = e.target.closest('.endorse-btn');
  if (!btn) return;
  e.preventDefault();

  const skillId = btn.dataset.skillId;
  btn.disabled = true;

  try {
    const {ok, json} = await postJSON(`/achievements/endorse/${skillId}/`, {});
    if (ok && json.ok) {
      // update count
      const countEls = document.querySelectorAll(`.endorse-count[data-skill-id="${skillId}"]`);
      countEls.forEach(el => el.textContent = json.count);
      btn.classList.add('endorsed');
    } else {
      alert(json.error || 'Unable to endorse.');
    }
  } catch (err) {
    alert('Network error.');
  } finally {
    btn.disabled = false;
  }
});
