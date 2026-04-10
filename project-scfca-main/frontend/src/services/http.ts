import axios from "axios";

export const http = axios.create({
  baseURL: "http://localhost:8000",
  withCredentials: true
});

function getCookie(name: string): string | undefined {
  const encoded = encodeURIComponent(name);
  const parts = document.cookie.split(";");
  for (const part of parts) {
    const trimmed = part.trim();
    if (!trimmed) continue;
    if (trimmed.startsWith(`${encoded}=`)) {
      return decodeURIComponent(trimmed.slice(encoded.length + 1));
    }
  }
  return undefined;
}

const UNSAFE_METHODS = new Set(["post", "put", "patch", "delete"]);

http.interceptors.request.use((config) => {
  const method = (config.method ?? "get").toLowerCase();
  if (UNSAFE_METHODS.has(method)) {
    const csrf = getCookie("scfca_csrf_token");
    if (csrf) {
        const headers: any = config.headers ?? {};
        if (typeof headers.set === "function") {
          headers.set("X-CSRF-Token", csrf);
        } else {
          headers["X-CSRF-Token"] = csrf;
        }
        config.headers = headers;
    }
  }

  // Let axios set the appropriate Content-Type.
  // (Important: do not force JSON when sending FormData/multipart.)
  return config;
});