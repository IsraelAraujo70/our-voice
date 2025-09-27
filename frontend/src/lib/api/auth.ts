import { apiFetch } from "../api-client";
import type { AuthResponse, LoginCredentials, SignupCredentials, User } from "../../types/auth-types";

export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
  // Django expects 'username' field, but we use 'email' in the frontend
  const loginData = {
    username: credentials.email,
    password: credentials.password,
  };

  return apiFetch<AuthResponse>("/auth/token/", {
    method: "POST",
    body: JSON.stringify(loginData),
  });
}

export async function signup(credentials: SignupCredentials): Promise<User> {
  return apiFetch<User>("/users/", {
    method: "POST",
    body: JSON.stringify(credentials),
  });
}

export async function getCurrentUser(token: string): Promise<User> {
  return apiFetch<User>("/users/me/", {
    headers: {
      Authorization: `Token ${token}`,
    },
  });
}

export async function logout(): Promise<void> {
}