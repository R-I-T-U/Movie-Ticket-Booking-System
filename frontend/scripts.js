// ====== CONFIG & STATE ======
const state = {
    baseUrl: localStorage.getItem('api_base') || document.getElementById('baseUrl').value,
    token: localStorage.getItem('access_token') || ''
  };
  
  // Initialize UI with saved values
  document.getElementById('baseUrl').value = state.baseUrl;
  document.getElementById('token').value = state.token;
  updateAuthUI();

  // ====== UTILITY FUNCTIONS ======
  function saveBaseUrl() {
    const v = document.getElementById('baseUrl').value.trim();
    state.baseUrl = v || 'http://localhost:8000';
    localStorage.setItem('api_base', state.baseUrl);
    toast('Base URL saved: ' + state.baseUrl);
  }
  
  function setTokenFromInput() {
    const v = document.getElementById('token').value.trim();
    state.token = v; 
    localStorage.setItem('access_token', v); 
    updateAuthUI();
    toast('Token set.');
  }
  
  function logout() { 
    state.token = ''; 
    localStorage.removeItem('access_token'); 
    updateAuthUI(); 
    toast('Logged out.'); 
  }
  
  function updateAuthUI() {
    const chip = document.getElementById('authStatus');
    if (state.token) { 
      chip.textContent = 'Authenticated'; 
      chip.style.background = '#064e3b'; 
      chip.style.color = '#bbf7d0'; 
    } else { 
      chip.textContent = 'Not authenticated'; 
      chip.style.background = 'var(--chip)'; 
      chip.style.color = 'var(--text)'; 
    }
    document.getElementById('token').value = state.token;
  }
  
  function toast(msg) { 
    console.log(msg); 
  }

  // ====== API FUNCTIONS ======
  async function apiFetch(path, { method = 'GET', body, isForm = false, headers = {} } = {}) {
    const url = state.baseUrl.replace(/\/$/, '') + path;
    const h = Object.assign({ 'Accept': 'application/json' }, headers);
    
    if (!isForm) { 
      h['Content-Type'] = 'application/json'; 
    }
    
    if (state.token) { 
      h['Authorization'] = 'Bearer ' + state.token; 
    }
    
    const res = await fetch(url, { 
      method, 
      headers: h, 
      body: isForm ? body : (body ? JSON.stringify(body) : undefined) 
    });
    
    const text = await res.text();
    let data; 
    
    try { 
      data = text ? JSON.parse(text) : {}; 
    } catch { 
      data = { raw: text }; 
    }
    
    document.getElementById('raw_out').textContent = JSON.stringify({ status: res.status, data }, null, 2);
    
    if (!res.ok) { 
      throw new Error(data?.detail || res.statusText || 'Request failed'); 
    }
    
    return data;
  }

  // ====== AUTH FUNCTIONS ======
  async function register() {
    const body = {
      username: document.getElementById('reg_username').value.trim(),
      email: document.getElementById('reg_email').value.trim(),
      full_name: document.getElementById('reg_fullname').value.trim(),
      password: document.getElementById('reg_password').value
    };
    
    try {
      const data = await apiFetch('/api/v1/auth/register', { method: 'POST', body });
      document.getElementById('reg_out').textContent = 'Registered user #' + data.id + ' (' + data.username + ')';
    } catch (e) { 
      document.getElementById('reg_out').textContent = 'Error: ' + e.message; 
    }
  }

  async function login() {
    const form = new URLSearchParams();
    form.append('username', document.getElementById('login_username').value.trim());
    form.append('password', document.getElementById('login_password').value);
    
    try {
      const data = await apiFetch('/api/v1/auth/login', { 
        method: 'POST', 
        body: form, 
        isForm: true, 
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' } 
      });
      
      state.token = data.access_token; 
      localStorage.setItem('access_token', state.token); 
      updateAuthUI();
      document.getElementById('login_out').textContent = 'Token acquired.';
    } catch (e) { 
      document.getElementById('login_out').textContent = 'Error: ' + e.message; 
    }
  }

  // ====== MOVIE FUNCTIONS ======
  async function loadMovies() {
    const skip = Number(document.getElementById('movies_skip').value || 0);
    const limit = Number(document.getElementById('movies_limit').value || 50);
    
    try {
      const data = await apiFetch(`/api/v1/movies?skip=${skip}&limit=${limit}`);
      const tbody = document.getElementById('movies_tbody');
      tbody.innerHTML = '';
      
      data.forEach(m => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${m.id}</td>
          <td>${escapeHtml(m.title)}</td>
          <td>${escapeHtml(m.genre)}</td>
          <td>${m.duration} min</td>
          <td>${m.is_active ? '✅' : '❌'}</td>
          <td>
            <button class="btn" onclick='prefillMovie(${JSON.stringify(m.id)}, ${JSON.stringify(m.title)}, ${JSON.stringify(m.genre)}, ${JSON.stringify(m.duration)}, ${JSON.stringify(m.description || "")})'>Edit</button>
            <button class="btn" onclick='deactivateMovie(${m.id})'>Deactivate</button>
            <button class="btn danger" onclick='deleteMovie(${m.id})'>Delete</button>
          </td>`;
        tbody.appendChild(tr);
      });
      
      document.getElementById('movies_out').textContent = 'Loaded ' + data.length + ' movies.';
    } catch (e) { 
      document.getElementById('movies_out').textContent = 'Error: ' + e.message; 
    }
  }

  function prefillMovie(id, title, genre, duration, description) {
    document.getElementById('mv_id').value = id;
    document.getElementById('mv_title').value = title;
    document.getElementById('mv_genre').value = genre;
    document.getElementById('mv_duration').value = duration;
    document.getElementById('mv_description').value = description || '';
  }

  async function createMovie() {
    const body = readMovieForm();
    
    try {
      const m = await apiFetch('/api/v1/movies', { method: 'POST', body });
      document.getElementById('movies_out').textContent = 'Created movie #' + m.id;
      loadMovies();
    } catch (e) { 
      document.getElementById('movies_out').textContent = 'Error: ' + e.message; 
    }
  }

  async function updateMovie() {
    const id = (document.getElementById('mv_id').value || '').trim();
    if (!id) { 
      return document.getElementById('movies_out').textContent = 'Provide movie ID to update.'; 
    }
    
    const body = readMovieForm();
    
    try {
      const m = await apiFetch(`/api/v1/movies/${id}`, { method: 'PUT', body });
      document.getElementById('movies_out').textContent = 'Updated movie #' + m.id;
      loadMovies();
    } catch (e) { 
      document.getElementById('movies_out').textContent = 'Error: ' + e.message; 
    }
  }

  async function deactivateMovie(id) {
    try { 
      await apiFetch(`/api/v1/movies/${id}/deactivate`, { method: 'PATCH' }); 
      loadMovies(); 
    } catch (e) { 
      alert('Failed: ' + e.message); 
    }
  }
  
  async function deleteMovie(id) {
    if (!confirm('Delete movie #' + id + '?')) return;
    
    try { 
      await apiFetch(`/api/v1/movies/${id}`, { method: 'DELETE' }); 
      loadMovies(); 
    } catch (e) { 
      alert('Failed: ' + e.message); 
    }
  }

  function readMovieForm() {
    return {
      title: document.getElementById('mv_title').value.trim(),
      description: (document.getElementById('mv_description').value || '').trim() || null,
      duration: Number(document.getElementById('mv_duration').value),
      genre: document.getElementById('mv_genre').value.trim()
    };
  }

  // ====== SHOWTIME FUNCTIONS ======
  async function loadShowtimes() {
    try {
      const data = await apiFetch('/api/v1/showtimes');
      const tbody = document.getElementById('st_tbody');
      tbody.innerHTML = '';
      
      data.forEach(s => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${s.id}</td>
          <td>${s.movie_id}</td>
          <td>${fmtDate(s.start_time)}</td>
          <td>${fmtDate(s.end_time)}</td>
          <td>${s.total_seats}</td>
          <td>${s.available_seats}</td>
          <td>${s.is_active ? '✅' : '❌'}</td>
          <td>
            <button class="btn" onclick='prefillShowtime(${JSON.stringify(s)})'>Edit</button>
            <button class="btn" onclick='deactivateShowtime(${s.id})'>Deactivate</button>
            <button class="btn danger" onclick='deleteShowtime(${s.id})'>Delete</button>
          </td>`;
        tbody.appendChild(tr);
      });
      
      document.getElementById('st_out').textContent = 'Loaded ' + data.length + ' showtimes.';
    } catch (e) { 
      document.getElementById('st_out').textContent = 'Error: ' + e.message; 
    }
  }

  function prefillShowtime(s) {
    document.getElementById('st_id').value = s.id;
    document.getElementById('st_movie_id').value = s.movie_id;
    document.getElementById('st_start').value = toLocalInputValue(s.start_time);
    document.getElementById('st_total').value = s.total_seats;
  }

  async function createShowtime() {
    const body = readShowtimeForm();
    
    try {
      const s = await apiFetch('/api/v1/showtimes', { method: 'POST', body });
      document.getElementById('st_out').textContent = 'Created showtime #' + s.id;
      loadShowtimes();
    } catch (e) { 
      document.getElementById('st_out').textContent = 'Error: ' + e.message; 
    }
  }
  
  async function updateShowtime() {
    const id = (document.getElementById('st_id').value || '').trim();
    if (!id) { 
      return document.getElementById('st_out').textContent = 'Provide showtime ID to update.'; 
    }
    
    const body = readShowtimeForm();
    
    try {
      const s = await apiFetch(`/api/v1/showtimes/${id}`, { method: 'PUT', body });
      document.getElementById('st_out').textContent = 'Updated showtime #' + s.id;
      loadShowtimes();
    } catch (e) { 
      document.getElementById('st_out').textContent = 'Error: ' + e.message; 
    }
  }
  
  async function deactivateShowtime(id) {
    try { 
      await apiFetch(`/api/v1/showtimes/${id}/deactivate`, { method: 'PATCH' }); 
      loadShowtimes(); 
    } catch (e) { 
      alert('Failed: ' + e.message); 
    }
  }
  
  async function deleteShowtime(id) {
    if (!confirm('Delete showtime #' + id + '?')) return;
    
    try { 
      await apiFetch(`/api/v1/showtimes/${id}`, { method: 'DELETE' }); 
      loadShowtimes(); 
    } catch (e) { 
      alert('Failed: ' + e.message); 
    }
  }

  function readShowtimeForm() {
    return {
      movie_id: Number(document.getElementById('st_movie_id').value),
      start_time: new Date(document.getElementById('st_start').value).toISOString(),
      total_seats: Number(document.getElementById('st_total').value)
    };
  }

  // ====== BOOKING FUNCTIONS ======
  async function loadBookings() {
    try {
      const data = await apiFetch('/api/v1/bookings');
      const tbody = document.getElementById('bookings_tbody');
      tbody.innerHTML = '';
      
      data.forEach(b => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${b.id}</td>
          <td>${b.seats}</td>
          <td>${b.status}</td>
          <td>${fmtDate(b.booking_time)}</td>
          <td>${b.user_id}</td>
          <td>${b.showtime_id}</td>
          <td>${b.showtime.movie_id || 'N/A'}</td>
          <td>
            <button class="btn" onclick='prefillBooking(${JSON.stringify(b)})'>Edit</button>
            <button class="btn" onclick='cancelBooking(${b.id})'>Cancel</button>
            <button class="btn danger" onclick='deleteBooking(${b.id})'>Delete</button>
          </td>`;
        tbody.appendChild(tr);
      });
      
      document.getElementById('bookings_out').textContent = 'Loaded ' + data.length + ' bookings.';
    } catch (e) { 
      document.getElementById('bookings_out').textContent = 'Error: ' + e.message; 
    }
  }

  function prefillBooking(booking) {
    document.getElementById('bk_id').value = booking.id;
    document.getElementById('bk_showtime_id').value = booking.showtime_id;
    document.getElementById('bk_seats').value = booking.seats;
  }

  async function createBooking() {
    const body = {
      showtime_id: Number(document.getElementById('bk_showtime_id').value),
      seats: Number(document.getElementById('bk_seats').value)
    };
    
    try {
      const b = await apiFetch('/api/v1/bookings', { method: 'POST', body });
      document.getElementById('bookings_out').textContent = 'Created booking #' + b.id;
      loadBookings();
    } catch (e) { 
      document.getElementById('bookings_out').textContent = 'Error: ' + e.message; 
    }
  }

  async function cancelBooking() {
    const id = (document.getElementById('bk_id').value || '').trim();
    if (!id) { 
      return document.getElementById('bookings_out').textContent = 'Provide booking ID to cancel.'; 
    }
    
    try {
      await apiFetch(`/api/v1/bookings/${id}/cancel`, { method: 'PATCH' });
      document.getElementById('bookings_out').textContent = 'Cancel booking #' + id;
      loadBookings();
    } catch (e) { 
      document.getElementById('bookings_out').textContent = 'Error: ' + e.message; 
    }
  }

  async function cancelMyBooking(id) {
    if (!confirm('Cancel booking #' + id + '?')) return;
    
    try {
      await apiFetch(`/api/v1/bookings/${id}/cancel`, { method: 'PATCH' });
      loadBookings();
    } catch (e) { 
    }
  }

  async function deleteBooking(id) {
    if (!confirm('Delete booking #' + id + '?')) return;
    
    try { 
      await apiFetch(`/api/v1/bookings/${id}`, { method: 'DELETE' }); 
      loadBookings(); 
    } catch (e) { 
      alert('Failed: ' + e.message); 
    }
  }

  async function cancelBooking(id) {
    if (!confirm('Cancelled booking #' + id + '?')) return;
    
    try { 
      await apiFetch(`/api/v1/bookings/${id}`, { method: 'PATCH' }); 
      loadBookings(); 
    } catch (e) { 
      alert('Failed: ' + e.message); 
    }
  }

  

  // ====== HELPER FUNCTIONS ======
  function fmtDate(iso) { 
    try { 
      return new Date(iso).toLocaleString(); 
    } catch { 
      return iso; 
    } 
  }
  
  function toLocalInputValue(iso) { 
    if (!iso) return ''; 
    const d = new Date(iso); 
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset()); 
    return d.toISOString().slice(0, 16); 
  }
  
  function escapeHtml(s) { 
    return String(s).replace(/[&<>"']/g, m => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#039;"}[m])); 
  }

  // Auto-load data if token exists
  if (state.token) { 
    loadMovies(); 
    loadShowtimes(); 
    loadBookings();
  }