const KEY = 'mahdi-todo-v1';
let tasks = JSON.parse(localStorage.getItem(KEY) || '[]');
let filter = 'all';

const save = () => localStorage.setItem(KEY, JSON.stringify(tasks));
const $ = (id) => document.getElementById(id);

function render() {
  const visible = tasks.filter((t) => (filter === 'all' ? true : filter === 'done' ? t.done : !t.done));
  $('list').innerHTML = visible.length
    ? ''
    : '<li class="empty">Nothing here yet ✨</li>';
  for (const t of visible) {
    const li = document.createElement('li');
    li.className = t.done ? 'done' : '';
    li.innerHTML = `<input type="checkbox" ${t.done ? 'checked' : ''} id="c-${t.id}" />
      <label for="c-${t.id}"></label>
      <button class="del" title="Delete">×</button>`;
    li.querySelector('label').textContent = t.title;
    li.querySelector('input').addEventListener('change', () => { t.done = !t.done; save(); render(); });
    li.querySelector('.del').addEventListener('click', () => { tasks = tasks.filter((x) => x.id !== t.id); save(); render(); });
    $('list').appendChild(li);
  }
  const left = tasks.filter((t) => !t.done).length;
  $('stats').textContent = `${left} remaining · ${tasks.length - left} done`;
}

$('new-task').addEventListener('submit', (e) => {
  e.preventDefault();
  const title = $('title').value.trim();
  if (!title) return;
  tasks.unshift({ id: crypto.randomUUID(), title, done: false });
  $('title').value = '';
  save(); render();
});

document.querySelectorAll('[data-filter]').forEach((btn) => btn.addEventListener('click', () => {
  filter = btn.dataset.filter;
  document.querySelectorAll('[data-filter]').forEach((b) => b.classList.toggle('active', b === btn));
  render();
}));

$('clear').addEventListener('click', () => { tasks = tasks.filter((t) => !t.done); save(); render(); });
render();
