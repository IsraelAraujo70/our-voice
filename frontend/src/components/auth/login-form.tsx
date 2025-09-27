"use client";

import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AuthService } from "@/lib/auth-service";
import { useAuthStore } from "@/stores/auth-store";
import type { LoginCredentials } from "@/types/auth-types";

interface LoginFormProps {
  onSuccess?: () => void;
  onSwitchToSignup?: () => void;
}

export function LoginForm({ onSuccess, onSwitchToSignup }: LoginFormProps) {
  const [credentials, setCredentials] = useState<LoginCredentials>({
    email: "",
    password: "",
  });

  const { isLoading, error, fieldErrors, clearError, clearFieldError } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await AuthService.login(credentials);
      onSuccess?.();
    } catch {
      // Error is handled by AuthService and stored in global state
    }
  };

  // Clear errors with debounce when user starts typing
  const handleInputChange = useCallback((field: keyof LoginCredentials) => {
    let timeoutId: NodeJS.Timeout;
    return (e: React.ChangeEvent<HTMLInputElement>) => {
      setCredentials(prev => ({ ...prev, [field]: e.target.value }));

      // Clear field-specific error after typing stops
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        if (fieldErrors[field]) {
          clearFieldError(field);
        }
        if (error) {
          clearError();
        }
      }, 300);
    };
  }, [error, fieldErrors, clearError, clearFieldError]);

  return (
    <Card className="w-full border-0 shadow-none">
      <CardHeader className="px-0 pt-0">
        <CardDescription>
          Enter your email and password to access your account
        </CardDescription>
      </CardHeader>

      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={credentials.email}
              onChange={handleInputChange("email")}
              placeholder="your@email.com"
              required
              disabled={isLoading}
              className={fieldErrors.email ? "border-red-500" : ""}
            />
            {fieldErrors.email && (
              <p className="text-sm text-red-500">{fieldErrors.email}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              value={credentials.password}
              onChange={handleInputChange("password")}
              placeholder="••••••••"
              required
              disabled={isLoading}
              className={fieldErrors.password ? "border-red-500" : ""}
            />
            {fieldErrors.password && (
              <p className="text-sm text-red-500">{fieldErrors.password}</p>
            )}
          </div>
        </CardContent>

        <CardFooter className="flex flex-col space-y-4">
          <Button
            type="submit"
            className="w-full"
            disabled={isLoading || !credentials.email || !credentials.password}
          >
            {isLoading ? "Signing in..." : "Sign in"}
          </Button>

          {onSwitchToSignup && (
            <Button
              type="button"
              variant="ghost"
              className="w-full"
              onClick={onSwitchToSignup}
              disabled={isLoading}
            >
              Don't have an account? Sign up
            </Button>
          )}
        </CardFooter>
      </form>
    </Card>
  );
}