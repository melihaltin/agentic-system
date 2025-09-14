"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../hooks/useAuth";

interface AuthGuardProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  redirectTo?: string;
}

export const AuthGuard: React.FC<AuthGuardProps> = ({
  children,
  requireAuth = true,
  redirectTo = "/auth/login",
}) => {
  const { authState } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authState.loading && authState.initialized) {
      if (requireAuth && !authState.user) {
        router.push(redirectTo);
      } else if (!requireAuth && authState.user) {
        router.push("/dashboard");
      }
    }
  }, [authState, requireAuth, redirectTo, router]);

  if (authState.loading || !authState.initialized) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (requireAuth && !authState.user) {
    return null; // Will redirect
  }

  if (!requireAuth && authState.user) {
    return null; // Will redirect
  }

  return <>{children}</>;
};
