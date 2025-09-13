"use client";

import React from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui";

interface LogoutButtonProps {
  className?: string;
  variant?: "primary" | "secondary";
}

const LogoutButton: React.FC<LogoutButtonProps> = ({
  className = "",
  variant = "secondary",
}) => {
  const router = useRouter();
  const params = useParams();
  const locale = params.locale as string;
  const { signOut, user } = useAuth();

  const handleLogout = async () => {
    try {
      const { error } = await signOut();
      if (error) {
        console.error("Logout failed:", error);
      } else {
        router.push(`/${locale}/login`);
      }
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  if (!user) return null;

  return (
    <Button
      onClick={handleLogout}
      className={`${className} ${
        variant === "secondary" ? "bg-red-600 hover:bg-red-700 text-white" : ""
      }`}
    >
      Çıkış Yap
    </Button>
  );
};

export default LogoutButton;
