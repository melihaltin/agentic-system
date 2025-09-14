"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/store/auth";

export const AuthInitializer = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const { initialize } = useAuthStore();

  useEffect(() => {
    initialize();
  }, [initialize]);

  return <>{children}</>;
};
