"use client";

import React from "react";
import { useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuthStore } from "@/store/auth";

const DashboardStats: React.FC = () => {
  const params = useParams();
  const locale = params.locale as string;
  const { company } = useAuthStore();
  const t = useTranslations("admin.stats");

  const getLocaleDateString = (date: Date) => {
    return date.toLocaleDateString(locale === "tr" ? "tr-TR" : "en-US");
  };

  const stats = [
    {
      title: t("totalUsers"),
      value: "1",
      description: t("activeUsers"),
      icon: (
        <svg
          className="w-6 h-6 text-blue-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
          />
        </svg>
      ),
    },
    {
      title: t("aiAssistant"),
      value: company?.aiAssistantName || t("notConfigured"),
      description: t("activeAiAssistant"),
      icon: (
        <svg
          className="w-6 h-6 text-green-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
          />
        </svg>
      ),
    },
    {
      title: t("status"),
      value: t("active"),
      description: t("systemStatus"),
      icon: (
        <svg
          className="w-6 h-6 text-green-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      ),
    },
    {
      title: t("registrationDate"),
      value: company?.createdAt
        ? getLocaleDateString(new Date(company.createdAt))
        : t("unknown"),
      description: t("accountCreationDate"),
      icon: (
        <svg
          className="w-6 h-6 text-purple-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
      ),
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {stats.map((stat, index) => (
        <div
          key={index}
          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">{stat.title}</p>
              <p className="text-2xl font-semibold text-gray-900 mb-1">
                {stat.value}
              </p>
              <p className="text-xs text-gray-500">{stat.description}</p>
            </div>
            <div className="flex-shrink-0">{stat.icon}</div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default DashboardStats;
