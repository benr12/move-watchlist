document.addEventListener('DOMContentLoaded', function () {
  // Check if user is already logged in
  const token = localStorage.getItem('token');
  if (token) {
    window.location.href = '/frontend/index.html';
  }

  // Login form submission
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const username = document.getElementById('login-username').value;
      const password = document.getElementById('login-password').value;
      const loginMsg = document.getElementById('login-msg');

      try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch('/auth/login', {
          method: 'POST',
          body: formData
        });

        // Debug response format
        console.log("Login response status:", response.status);

        // First let's log the raw response text to see exactly what we're getting
        const responseClone = response.clone();
        const rawText = await responseClone.text();
        console.log("Raw response text:", rawText);

        if (response.ok) {
          try {
            // Now try to parse as JSON
            const data = JSON.parse(rawText);
            console.log("Parsed JSON response:", data);

            // Extract token - check all possible field names
            let tokenValue = null;

            // Check common field names
            const possibleFields = ['token', 'access_token', 'accessToken', 'jwt', 'id_token'];
            for (const field of possibleFields) {
              if (data[field]) {
                console.log(`Found token in field '${field}'`);
                tokenValue = data[field];
                break;
              }
            }

            // If not found in common fields, look for any JWT-like string
            if (!tokenValue) {
              for (const key in data) {
                if (typeof data[key] === 'string' && data[key].startsWith('ey')) {
                  console.log(`Found likely JWT in field '${key}'`);
                  tokenValue = data[key];
                  break;
                }
              }
            }

            if (tokenValue) {
              console.log(`Saving token to localStorage (first 10 chars): ${tokenValue.substring(0, 10)}...`);
              localStorage.setItem('token', tokenValue);
              window.location.href = '/frontend/index.html';
            } else {
              console.error("Could not find a token in the response");
              loginMsg.textContent = 'Login successful but could not retrieve authentication token.';
              loginMsg.classList.remove('d-none');
            }
          } catch (error) {
            console.error("Error parsing JSON response:", error);
            loginMsg.textContent = 'Error processing server response. Please try again.';
            loginMsg.classList.remove('d-none');
          }
        } else {
          try {
            const error = JSON.parse(rawText);
            loginMsg.textContent = error.detail || 'Login failed. Please check your credentials.';
          } catch (e) {
            loginMsg.textContent = 'Login failed. Please check your credentials.';
          }
          loginMsg.classList.remove('d-none');
        }
      } catch (error) {
        console.error('Login error:', error);
        loginMsg.textContent = 'An error occurred during login. Please try again.';
        loginMsg.classList.remove('d-none');
      }
    });
  }

  // Register form submission
  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const username = document.getElementById('register-username').value;
      const email = document.getElementById('register-email').value;
      const password = document.getElementById('register-password').value;
      const confirmPassword = document.getElementById('register-confirm-password').value;
      const registerMsg = document.getElementById('register-msg');

      // Validate passwords match
      if (password !== confirmPassword) {
        registerMsg.textContent = 'Passwords do not match.';
        registerMsg.classList.remove('d-none');
        return;
      }

      try {
        const response = await fetch('/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username,
            email,
            password
          })
        });

        if (response.ok) {
          // Show success message
          registerMsg.textContent = 'Registration successful! Please login.';
          registerMsg.classList.remove('d-none');
          registerMsg.classList.remove('alert-danger');
          registerMsg.classList.add('alert-success');

          // Clear form
          registerForm.reset();

          // Switch to login tab after 2 seconds
          setTimeout(() => {
            document.getElementById('login-tab').click();
          }, 2000);
        } else {
          const error = await response.json();
          registerMsg.textContent = error.detail || 'Registration failed. Please try again.';
          registerMsg.classList.remove('d-none');
          registerMsg.classList.add('alert-danger');
          registerMsg.classList.remove('alert-success');
        }
      } catch (error) {
        console.error('Registration error:', error);
        registerMsg.textContent = 'An error occurred during registration. Please try again.';
        registerMsg.classList.remove('d-none');
        registerMsg.classList.add('alert-danger');
        registerMsg.classList.remove('alert-success');
      }
    });
  }
});