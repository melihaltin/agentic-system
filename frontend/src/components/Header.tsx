"use client";

import React from "react";
import { useRouter, useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuthStore } from "@/store/auth";
import { Button } from "@/components/ui";
import LanguageSwitcher from "./LanguageSwitcher";

const Header: React.FC = () => {
  const router = useRouter();
  const params = useParams();
  const locale = params.locale as string;
  const { user, company, logout } = useAuthStore();
  const t = useTranslations("admin.header");
  const tDashboard = useTranslations("admin.dashboard");

  const handleLogout = () => {
    logout();
    router.push(`/${locale}/login`);
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-gray-900">
              {company?.name || tDashboard("title")}
            </h1>
            {company?.aiAssistantName && (
              <span className="ml-4 px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
                {company.aiAssistantName}
              </span>
            )}
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-600">
              {tDashboard("welcome")},{" "}
              <span className="font-medium">
                {user?.firstName} {user?.lastName}
              </span>
            </div>
            <LanguageSwitcher />
            <Button variant="secondary" size="sm" onClick={handleLogout}>
              {t("logout")}
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
