/* showing & hiding registeration forms */
const signUpBtn = document.querySelector('.signup-button');
const loginBtn = document.querySelector('.login-button');

const signUpForm = document.getElementById('signup');
const loginForm = document.getElementById('login');

signUpBtn.addEventListener('click', function() {
/* activate and show sign-up elements while hiding login elements */
  this.classList.add('active');
  loginBtn.classList.remove('active');
  loginForm.classList.remove('show');
  signUpForm.classList.add('show');
});

loginBtn.addEventListener('click', function() {
/* activate and show login elements while hiding sign-up elements */
  this.classList.add('active');
  signUpBtn.classList.remove('active');
  signUpForm.classList.remove('show');
  loginForm.classList.add('show');    
});