import { z } from 'zod';

// Login schema
export const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Invalid email format'),
  password: z
    .string()
    .min(1, 'Password is required')
    .min(8, 'Password must be at least 8 characters'),
});

// Signup schema
export const signupSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Invalid email format'),
  handle: z
    .string()
    .min(1, 'Handle is required')
    .max(30, 'Handle must be 30 characters or less')
    .regex(/^[a-zA-Z0-9_]+$/, 'Handle can only contain letters, numbers, and underscores'),
  password: z
    .string()
    .min(1, 'Password is required')
    .min(8, 'Password must be at least 8 characters'),
  display_name: z
    .string()
    .max(80, 'Display name must be 80 characters or less')
    .optional()
    .or(z.literal('')),
});

// Types
export type LoginFormData = z.infer<typeof loginSchema>;
export type SignupFormData = z.infer<typeof signupSchema>;

// Field mappings from backend to frontend
export const backendToFrontendFieldMap: Record<string, string> = {
  username: 'email', // Django uses 'username' for email login
  password: 'password',
  handle: 'handle',
  display_name: 'display_name',
  email: 'email',
  non_field_errors: '__general__',
  detail: '__general__',
};

// Parse backend validation errors
export interface ParsedError {
  field: string | null;
  message: string;
}

export interface ValidationResult {
  success: boolean;
  errors: Record<string, string>;
  generalError?: string;
}

export function parseBackendErrors(errorData: unknown): ValidationResult {
  const errors: Record<string, string> = {};
  let generalError: string | undefined;

  if (!errorData || typeof errorData !== 'object') {
    return { success: false, errors, generalError: 'An error occurred' };
  }

  const data = errorData as Record<string, unknown>;

  // Handle 'detail' field (general error message)
  if (typeof data.detail === 'string') {
    generalError = data.detail;
    return { success: false, errors, generalError };
  }

  // Handle field-specific errors
  for (const [backendField, messages] of Object.entries(data)) {
    const frontendField = backendToFrontendFieldMap[backendField] || backendField;

    let message = '';
    if (Array.isArray(messages) && messages.length > 0) {
      message = String(messages[0]);
    } else if (typeof messages === 'string') {
      message = messages;
    }

    if (message) {
      if (frontendField === '__general__') {
        generalError = message;
      } else {
        errors[frontendField] = message;
      }
    }
  }

  return {
    success: false,
    errors,
    generalError,
  };
}

// Validate form data locally
export function validateLogin(data: unknown): ValidationResult {
  try {
    loginSchema.parse(data);
    return { success: true, errors: {} };
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors: Record<string, string> = {};
      if (error.issues && Array.isArray(error.issues)) {
        error.issues.forEach((issue) => {
          if (issue.path && issue.path.length > 0) {
            const field = String(issue.path[0]);
            errors[field] = issue.message;
          }
        });
      }
      return { success: false, errors };
    }
    return {
      success: false,
      errors: {},
      generalError: 'Validation failed'
    };
  }
}

export function validateSignup(data: unknown): ValidationResult {
  try {
    signupSchema.parse(data);
    return { success: true, errors: {} };
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors: Record<string, string> = {};
      if (error.issues && Array.isArray(error.issues)) {
        error.issues.forEach((issue) => {
          if (issue.path && issue.path.length > 0) {
            const field = String(issue.path[0]);
            errors[field] = issue.message;
          }
        });
      }
      return { success: false, errors };
    }
    return {
      success: false,
      errors: {},
      generalError: 'Validation failed'
    };
  }
}