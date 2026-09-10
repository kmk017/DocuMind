const BASE_URL = "http://127.0.0.1:5000";

const TOKEN_KEY = "documind_token";

async function extractErrorMessage(response, fallback) {
  try {
    const data = await response.json();

    if (
      data &&
      typeof data.error === "string" &&
      data.error.trim()
    ) {
      return data.error;
    }
  } catch {}

  return fallback;
}

async function request(path, options = {}) {
  let response;

  const headers = new Headers(options.headers || {});

  const token = localStorage.getItem(TOKEN_KEY);

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...options,
      headers,
    });
  } catch {
    throw new Error(
      "Could not reach the server. Check that the backend is running and try again."
    );
  }

  if (response.status === 401) {
    localStorage.removeItem(TOKEN_KEY);

    window.dispatchEvent(
      new Event("documind:auth-expired")
    );
  }

  if (!response.ok) {
    const fallback =
      response.status === 401
        ? "Your session has expired. Please log in again."
        : response.status === 404
        ? "The requested document was not found."
        : response.status === 400
        ? "The request could not be completed."
        : response.status === 409
        ? "An account with this email already exists."
        : response.status === 413
        ? "The file is too large to upload."
        : "Something went wrong on the server. Please try again.";

    const message = await extractErrorMessage(
      response,
      fallback
    );

    const error = new Error(message);
    error.status = response.status;

    throw error;
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}


// ============================================================
// AUTH
// ============================================================

export function registerUser(email, password) {
  return request("/api/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
    }),
  });
}

export function loginUser(email, password) {
  return request("/api/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
    }),
  });
}

export function getCurrentUser() {
  return request("/api/auth/me", {
    method: "GET",
  });
}


// ============================================================
// DOCUMENTS
// ============================================================

export function getDocuments() {
  return request("/api/documents", {
    method: "GET",
  });
}

export function uploadDocument(file) {
  const formData = new FormData();

  formData.append("file", file);

  return request("/api/documents", {
    method: "POST",
    body: formData,
  });
}

export function getDocument(id) {
  return request(`/api/documents/${id}`, {
    method: "GET",
  });
}

export function getDocumentStatus(id) {
  return request(`/api/documents/${id}/status`, {
    method: "GET",
  });
}

export function deleteDocument(id) {
  return request(`/api/documents/${id}`, {
    method: "DELETE",
  });
}

// ============================================================
// SEARCH / RAG
// ============================================================

export async function searchDocuments(query, documentId) {
  return request("/search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query,
      document_id: documentId,
    }),
  });
}

export async function askQuestion(question, documentId) {
  return request("/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      document_id: documentId,
    }),
  });
}