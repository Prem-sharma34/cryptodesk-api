import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
  withCredentials: true,
});

// In-memory access token
let accessToken = null;

export const setAccessToken = (token) => { accessToken = token; };
export const getAccessToken = () => accessToken;

// Attach access token to every request
api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// On 401 — try refreshing with the refresh token cookie
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        const refreshToken = document.cookie
          .split("; ")
          .find((row) => row.startsWith("refresh_token="))
          ?.split("=")[1];

        if (!refreshToken) throw new Error("No refresh token");

        const { data } = await axios.post(
          `${api.defaults.baseURL}/auth/refresh`,
          { refresh_token: refreshToken }
        );

        setAccessToken(data.access_token);
        // Rotate refresh token cookie
        document.cookie = `refresh_token=${data.refresh_token}; path=/; max-age=${7 * 24 * 3600}; SameSite=Strict`;

        original.headers.Authorization = `Bearer ${data.access_token}`;
        return api(original);
      } catch {
        setAccessToken(null);
        document.cookie = "refresh_token=; max-age=0";
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;