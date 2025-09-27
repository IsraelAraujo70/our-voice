import { useAuthStore } from "../stores/auth-store";
import { login as apiLogin, signup as apiSignup, getCurrentUser } from "./api/auth";
import type { LoginCredentials, SignupCredentials } from "../types/auth-types";
import { parseBackendErrors, validateLogin, validateSignup } from "./validation/auth-schemas";
import { ApiError } from "./api-error";

export class AuthService {
  static async login(credentials: LoginCredentials): Promise<void> {
    const { setLoading, setError, setFieldErrors, setToken, setUser, clearAllErrors } = useAuthStore.getState();

    try {
      setLoading(true);
      clearAllErrors();

      // Validate locally first
      const validation = validateLogin(credentials);
      if (!validation.success) {
        setFieldErrors(validation.errors);
        if (validation.generalError) {
          setError(validation.generalError);
        }
        throw new Error('Validation failed');
      }

      // Get token from login
      const authResponse = await apiLogin(credentials);
      setToken(authResponse.token);

      // Get user data
      const user = await getCurrentUser(authResponse.token);
      setUser(user);

    } catch (error) {
      // Check if it's an API error with structured data
      if (error instanceof ApiError) {
        const parsed = parseBackendErrors(error.data);
        setFieldErrors(parsed.errors);
        setError(parsed.generalError || null);
      } else if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Login failed");
      }
      throw error;
    } finally {
      setLoading(false);
    }
  }

  static async signup(credentials: SignupCredentials): Promise<void> {
    const { setLoading, setError, setFieldErrors, clearAllErrors } = useAuthStore.getState();

    try {
      setLoading(true);
      clearAllErrors();

      // Validate locally first
      const validation = validateSignup(credentials);
      if (!validation.success) {
        setFieldErrors(validation.errors);
        if (validation.generalError) {
          setError(validation.generalError);
        }
        throw new Error('Validation failed');
      }

      // Create user account
      await apiSignup(credentials);

      // Auto-login after signup
      await this.login({
        email: credentials.email,
        password: credentials.password,
      });

    } catch (error) {
      // Check if it's an API error with structured data
      if (error instanceof ApiError) {
        const parsed = parseBackendErrors(error.data);
        setFieldErrors(parsed.errors);
        setError(parsed.generalError || null);
      } else if (error instanceof Error && error.message !== 'Validation failed') {
        setError(error.message);
      }
      throw error;
    } finally {
      setLoading(false);
    }
  }

  static async logout(): Promise<void> {
    const { logout } = useAuthStore.getState();
    logout();
  }

  static async initializeAuth(): Promise<void> {
    const { token, setUser, setError, logout } = useAuthStore.getState();

    if (!token) return;

    try {
      const user = await getCurrentUser(token);
      setUser(user);
    } catch {
      // Token is invalid, clear auth state
      logout();
      setError("Session expired. Please login again.");
    }
  }
}