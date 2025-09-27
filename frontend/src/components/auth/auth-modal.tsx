"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { LoginForm } from "./login-form";
import { SignupForm } from "./signup-form";

interface AuthModalProps {
  children?: React.ReactNode;
}

export function AuthModal({ children }: AuthModalProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isSignup, setIsSignup] = useState(false);

  const handleSuccess = () => {
    setIsOpen(false);
    setIsSignup(false);
  };

  const handleSwitchMode = () => {
    setIsSignup(!isSignup);
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {children || (
          <Button variant="outline">
            Login
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>
            {isSignup ? "Join OUR Voice" : "Welcome back"}
          </DialogTitle>
        </DialogHeader>
        {isSignup ? (
          <SignupForm
            onSuccess={handleSuccess}
            onSwitchToLogin={handleSwitchMode}
          />
        ) : (
          <LoginForm
            onSuccess={handleSuccess}
            onSwitchToSignup={handleSwitchMode}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}