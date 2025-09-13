"use client";

import React from "react";
import { useRouter, useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui";
import { LogoutButton, UserProfile } from "@/components/auth";
import LanguageSwitcher from "./LanguageSwitcher";

const Header: React.FC = () => {
  const router = useRouter();
  const params = useParams();
  const locale = params.locale as string;
  const { user } = useAuth();
  const t = useTranslations("admin.header");
  const tDashboard = useTranslations("admin.dashboard");

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-gray-900">
              {tDashboard("title")}
            </h1>
          </div>

          <div className="flex items-center space-x-4">
            <UserProfile />
            <LanguageSwitcher />
            <LogoutButton />
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
