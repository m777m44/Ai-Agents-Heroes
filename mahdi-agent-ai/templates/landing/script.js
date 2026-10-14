document.getElementById('year').textContent = new Date().getFullYear();

document.getElementById('signup').addEventListener('submit', (event) => {
  event.preventDefault();
  const email = new FormData(event.target).get('email');
  document.getElementById('msg').textContent = `Thanks! We will write to ${email}.`;
  event.target.reset();
});
