// Global variables
let data = [];
let selectedMovie = {};
let currentFilter = 'all';
const api = '/movies';

// Debug function to check token
function debugToken() {
  const token = localStorage.getItem('token');
  console.log("Current token:", token ? token.substring(0, 10) + "..." : "none");
  console.log("Token length:", token ? token.length : 0);
}

// Function to try all auth header formats
async function tryAllAuthFormats(url, options = {}) {
  const token = localStorage.getItem('token');
  console.log("Trying all auth formats with token:", token ? token.substring(0, 10) + "..." : "none");

  // Try standard format first
  let response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  });
  console.log("Standard Bearer format response:", response.status);

  if (response.status !== 401) {
    return response;
  }

  // Try without Bearer
  response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': token
    }
  });
  console.log("No prefix format response:", response.status);

  if (response.status !== 401) {
    return response;
  }

  // Try with JWT prefix
  response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `JWT ${token}`
    }
  });
  console.log("JWT prefix format response:", response.status);

  if (response.status !== 401) {
    return response;
  }

  // Try with Token prefix
  response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Token ${token}`
    }
  });
  console.log("Token prefix format response:", response.status);

  return response;
}

// Check authentication on page load
document.addEventListener('DOMContentLoaded', function () {
  console.log("DOM Content Loaded");

  // Check if token exists
  const token = localStorage.getItem('token');
  console.log("Token exists:", !!token, "First 10 chars:", token ? token.substring(0, 10) : "none");

  if (!token) {
    console.log("No token found, redirecting to login");
    window.location.href = '/frontend/login.html';
    return;
  }

  // Debug token info
  debugToken();

  // Setup logout button
  const navbarEl = document.getElementById('navbar');
  console.log("Navbar element found:", !!navbarEl);

  if (navbarEl) {
    console.log("Adding logout button to navbar");
    const userInfoEl = document.createElement('div');
    userInfoEl.className = 'ms-auto d-flex align-items-center';
    userInfoEl.innerHTML = `
      <button id="logout-btn" class="btn btn-outline-danger ms-2">Logout</button>
    `;
    navbarEl.appendChild(userInfoEl);

    // Add logout event listener
    document.getElementById('logout-btn').addEventListener('click', function () {
      console.log("Logout button clicked");
      localStorage.removeItem('token');
      window.location.href = '/frontend/login.html';
    });
    console.log("Logout button added and event listener attached");
  } else {
    console.error("Navbar element not found");
  }

  // Get user info
  getUserInfo();

  // Initialize form handlers
  setupFormHandlers();

  // Get movies
  getMovies();
});

function getUserInfo() {
  console.log("Getting user info");
  tryAllAuthFormats('/auth/me')
    .then(response => {
      console.log("User info response status:", response.status);
      if (response.ok) {
        return response.json();
      } else if (response.status === 401) {
        console.error("Authentication failed, token invalid");
        localStorage.removeItem('token');
        window.location.href = '/frontend/login.html';
        throw new Error('Unauthorized');
      }
      throw new Error('Failed to get user info');
    })
    .then(user => {
      console.log("User info retrieved:", user.username);
      const welcomeEl = document.getElementById('welcome-message');
      if (welcomeEl) {
        welcomeEl.textContent = `Welcome, ${user.username}!`;
      }
    })
    .catch(error => {
      console.error('Error getting user info:', error);
    });
}

function setupFormHandlers() {
  const formAdd = document.getElementById('form-add');
  if (formAdd) {
    formAdd.addEventListener('submit', addMovie);
  }

  const formEdit = document.getElementById('form-edit');
  if (formEdit) {
    formEdit.addEventListener('submit', updateMovie);
  }
}

function filterMovies(filter) {
  console.log("Filtering movies:", filter);
  currentFilter = filter;
  refreshMovies();
}

function tryAdd() {
  let msg = document.getElementById('msg');
  if (msg) msg.innerHTML = '';
}

function tryEditMovie(id) {
  console.log("Editing movie:", id);
  const movie = data.find((x) => x.id === id);
  if (!movie) {
    console.error("Movie not found:", id);
    return;
  }

  selectedMovie = movie;

  const titleEditInput = document.getElementById('title-edit');
  const directorEditInput = document.getElementById('director-edit');
  const yearEditInput = document.getElementById('year-edit');
  const watchedEditInput = document.getElementById('watched-edit');
  const movieId = document.getElementById('movie-id');

  if (movieId) movieId.innerText = movie.id;
  if (titleEditInput) titleEditInput.value = movie.title;
  if (directorEditInput) directorEditInput.value = movie.director;
  if (yearEditInput) yearEditInput.value = movie.release_year;
  if (watchedEditInput) watchedEditInput.checked = movie.watched;

  const editMsg = document.getElementById('edit-msg');
  if (editMsg) editMsg.innerHTML = '';
}

function toggleWatched(id) {
  console.log("Toggling watched status for movie:", id);

  tryAllAuthFormats(`${api}/${id}/toggle-watched`, {
    method: 'PUT'
  })
    .then(response => {
      console.log("Toggle watched response status:", response.status);
      if (response.ok) {
        const movie = data.find(x => x.id === id);
        if (movie) {
          movie.watched = !movie.watched;
          refreshMovies();
        }
      } else if (response.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/frontend/login.html';
      } else {
        console.error("Error toggling watched status");
      }
    })
    .catch(error => {
      console.error("Error:", error);
    });
}

function deleteMovie(id) {
  console.log("Deleting movie:", id);

  tryAllAuthFormats(`${api}/${id}`, {
    method: 'DELETE'
  })
    .then(response => {
      console.log("Delete movie response status:", response.status);
      if (response.ok) {
        data = data.filter((x) => x.id !== id);
        refreshMovies();
      } else if (response.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/frontend/login.html';
      } else {
        console.error("Error deleting movie");
      }
    })
    .catch(error => {
      console.error("Error:", error);
    });
}

function addMovie(e) {
  e.preventDefault();
  console.log("Form submitted");

  const titleInput = document.getElementById('title');
  const directorInput = document.getElementById('director');
  const yearInput = document.getElementById('year');
  const watchedInput = document.getElementById('watched');
  const msg = document.getElementById('msg');

  if (!titleInput || !titleInput.value) {
    if (msg) msg.innerHTML = 'Movie title cannot be blank';
    return;
  }

  if (!directorInput || !directorInput.value) {
    if (msg) msg.innerHTML = 'Director name cannot be blank';
    return;
  }

  if (!yearInput || !yearInput.value) {
    if (msg) msg.innerHTML = 'Release year cannot be blank';
    return;
  }

  const title = titleInput.value;
  const director = directorInput.value;
  const year = yearInput.value;
  const watched = watchedInput ? watchedInput.checked : false;

  console.log("Adding movie:", title, director, year, watched);

  tryAllAuthFormats(api, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      title,
      director,
      release_year: parseInt(year),
      watched
    })
  })
    .then(response => {
      console.log("Response status:", response.status);
      if (response.ok) {
        return response.json();
      } else {
        throw new Error(`Network response was not ok: ${response.status}`);
      }
    })
    .then(newMovie => {
      console.log("Movie added successfully:", newMovie);
      data.push(newMovie);
      refreshMovies();
      resetForm();

      const closeBtn = document.getElementById('add-close');
      if (closeBtn) {
        closeBtn.click();
      }
    })
    .catch(error => {
      console.error("Error adding movie:", error);
      if (msg) msg.innerHTML = 'Error adding movie: ' + error.message;
    });
}

function updateMovie(e) {
  e.preventDefault();
  console.log("Edit form submitted");

  const titleEditInput = document.getElementById('title-edit');
  const directorEditInput = document.getElementById('director-edit');
  const yearEditInput = document.getElementById('year-edit');
  const watchedEditInput = document.getElementById('watched-edit');
  const editMsg = document.getElementById('edit-msg');

  if (!titleEditInput || !titleEditInput.value) {
    if (editMsg) editMsg.innerHTML = 'Movie title cannot be blank';
    return;
  }

  if (!directorEditInput || !directorEditInput.value) {
    if (editMsg) editMsg.innerHTML = 'Director name cannot be blank';
    return;
  }

  if (!yearEditInput || !yearEditInput.value) {
    if (editMsg) editMsg.innerHTML = 'Release year cannot be blank';
    return;
  }

  const title = titleEditInput.value;
  const director = directorEditInput.value;
  const year = yearEditInput.value;
  const watched = watchedEditInput ? watchedEditInput.checked : false;

  tryAllAuthFormats(`${api}/${selectedMovie.id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      title,
      director,
      release_year: parseInt(year),
      watched
    })
  })
    .then(response => {
      console.log("Update movie response status:", response.status);
      if (response.ok) {
        return response.json();
      } else {
        throw new Error(`Network response was not ok: ${response.status}`);
      }
    })
    .then(updatedMovie => {
      const index = data.findIndex(movie => movie.id === selectedMovie.id);
      if (index !== -1) {
        data[index] = updatedMovie;
      }
      refreshMovies();

      const closeBtn = document.getElementById('edit-close');
      if (closeBtn) {
        closeBtn.click();
      }
    })
    .catch(error => {
      console.error("Error updating movie:", error);
      if (editMsg) editMsg.innerHTML = 'Error updating movie: ' + error.message;
    });
}

function refreshMovies() {
  const moviesDiv = document.getElementById('movies');
  if (!moviesDiv) {
    console.error("Movies div not found");
    return;
  }

  moviesDiv.innerHTML = '';
  let filteredData = [...data];

  if (currentFilter === 'watched') {
    filteredData = data.filter(movie => movie.watched);
  } else if (currentFilter === 'unwatched') {
    filteredData = data.filter(movie => !movie.watched);
  }

  console.log("Filtered data:", filteredData);

  if (filteredData.length === 0) {
    moviesDiv.innerHTML = '<div class="text-center mt-3">No movies to display.</div>';
    return;
  }

  filteredData.forEach(movie => {
    const movieCard = document.createElement('div');
    movieCard.className = 'card my-2';
    movieCard.innerHTML = `
      <div class="card-body">
        <h5 class="card-title">${movie.title}</h5>
        <h6 class="card-subtitle mb-2 text-muted">${movie.director} (${movie.release_year})</h6>
        <p class="card-text">Watched: ${movie.watched ? '✅' : '❌'}</p>
        <button class="btn btn-sm btn-primary me-2" onclick="tryEditMovie(${movie.id})" data-bs-toggle="modal" data-bs-target="#editModal">Edit</button>
        <button class="btn btn-sm btn-danger me-2" onclick="deleteMovie(${movie.id})">Delete</button>
        <button class="btn btn-sm btn-secondary" onclick="toggleWatched(${movie.id})">Toggle Watched</button>
      </div>
    `;
    moviesDiv.appendChild(movieCard);
  });
}

function resetForm() {
  const titleInput = document.getElementById('title');
  const directorInput = document.getElementById('director');
  const yearInput = document.getElementById('year');
  const watchedInput = document.getElementById('watched');
  const msg = document.getElementById('msg');

  if (titleInput) titleInput.value = '';
  if (directorInput) directorInput.value = '';
  if (yearInput) yearInput.value = '';
  if (watchedInput) watchedInput.checked = false;
  if (msg) msg.innerHTML = '';
}

function getMovies() {
  console.log("Getting movies from API");
  tryAllAuthFormats(api)
    .then(response => {
      console.log("Get movies response status:", response.status);
      if (response.ok) {
        return response.json();
      } else {
        throw new Error('Network response was not ok');
      }
    })
    .then(movies => {
      console.log("Movies retrieved:", movies.length);
      data = movies;
      refreshMovies();
    })
    .catch(error => {
      console.error('Error getting movies:', error);
    });
}