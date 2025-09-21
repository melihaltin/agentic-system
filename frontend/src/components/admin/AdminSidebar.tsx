"use client";

import React from "react";
import Link from "next/link";
import { useParams, usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
// SVG Icons as React components
const Building2 = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-4m-5 0H3m0 0h2M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
    />
  </svg>
);

const Bot = ({ className }: { className?: string }) => (
  <svg
    className={className}
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
);

const BarChart3 = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
    />
  </svg>
);

const Settings = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
    />
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
    />
  </svg>
);

const ChevronLeft = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M15 19l-7-7 7-7"
    />
  </svg>
);

const ChevronRight = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M9 5l7 7-7 7"
    />
  </svg>
);
import { AdminSection } from "@/types/admin.types";
import { useAuthStore } from "@/store/auth";

interface AdminSidebarProps {
  activeSection: AdminSection;
  onSectionChange: (section: AdminSection) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

const AdminSidebar: React.FC<AdminSidebarProps> = ({
  activeSection,
  onSectionChange,
  isCollapsed,
  onToggleCollapse,
}) => {
  const params = useParams();
  const locale = params.locale as string;
  const t = useTranslations("admin.sidebar");

  const profile = useAuthStore((state) => state.user);
  const user = useAuthStore((state) => state.profile);

  const menuItems = [
    {
      id: "business-settings" as AdminSection,
      label: t("businessSettings"),
      icon: Building2,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
    },
    {
      id: "my-agents" as AdminSection,
      label: t("myAgents"),
      icon: Bot,
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
    {
      id: "analytics" as AdminSection,
      label: t("analytics"),
      icon: BarChart3,
      color: "text-purple-600",
      bgColor: "bg-purple-50",
    },
    {
      id: "settings" as AdminSection,
      label: t("settings"),
      icon: Settings,
      color: "text-gray-600",
      bgColor: "bg-gray-50",
    },
  ];

  const handleSectionClick = (section: AdminSection) => {
    onSectionChange(section);
  };

  return (
    <div
      className={`
        bg-white border-r border-gray-200 transition-all duration-300 ease-in-out
        ${isCollapsed ? "w-16" : "w-64"}
        flex flex-col h-screen
      `}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        {!isCollapsed && (
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                {t("adminPanel")}
              </h2>
            </div>
          </div>
        )}

        <button
          onClick={onToggleCollapse}
          className="p-1 rounded-lg hover:bg-gray-100 transition-colors"
          aria-label={isCollapsed ? t("expandSidebar") : t("collapseSidebar")}
        >
          {isCollapsed ? (
            <ChevronRight className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronLeft className="w-5 h-5 text-gray-500" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;

            return (
              <li key={item.id}>
                <button
                  onClick={() => handleSectionClick(item.id)}
                  className={`
                    w-full flex items-center space-x-3 px-3 py-3 rounded-lg transition-all duration-200
                    ${
                      isActive
                        ? `${item.bgColor} ${item.color} font-medium`
                        : "text-gray-700 hover:bg-gray-50 hover:text-gray-900"
                    }
                    ${isCollapsed ? "justify-center" : "justify-start"}
                  `}
                  title={isCollapsed ? item.label : undefined}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  {!isCollapsed && (
                    <span className="text-sm font-medium">{item.label}</span>
                  )}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* User Info */}
      {!isCollapsed && (
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-gray-700">A</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {user?.company?.company_name || "Admin User"}
              </p>
              <p className="text-xs text-gray-500 truncate">{profile?.email}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminSidebar;
