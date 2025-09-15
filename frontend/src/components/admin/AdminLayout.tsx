"use client";

import React, { useState } from "react";
import AdminSidebar from "./AdminSidebar";
import { AdminSection } from "@/types/admin.types";

interface AdminLayoutProps {
  children: React.ReactNode;
  activeSection: AdminSection;
  onSectionChange: (section: AdminSection) => void;
}

const AdminLayout: React.FC<AdminLayoutProps> = ({
  children,
  activeSection,
  onSectionChange,
}) => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const handleToggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <AdminSidebar
        activeSection={activeSection}
        onSectionChange={onSectionChange}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={handleToggleSidebar}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">
                {getSectionTitle(activeSection)}
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                {getSectionDescription(activeSection)}
              </p>
            </div>

            {/* Header Actions */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-600">
                  All Systems Online
                </span>
              </div>
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto bg-gray-50">
          <div className="p-6">{children}</div>
        </main>
      </div>
    </div>
  );
};

// Helper functions for section titles and descriptions
const getSectionTitle = (section: AdminSection): string => {
  switch (section) {
    case "business-settings":
      return "Business Settings";
    case "my-agents":
      return "My AI Agents";
    case "analytics":
      return "Analytics & Reports";
    case "settings":
      return "System Settings";
    default:
      return "Dashboard";
  }
};

const getSectionDescription = (section: AdminSection): string => {
  switch (section) {
    case "business-settings":
      return "Manage your company information and platform integrations";
    case "my-agents":
      return "Configure and manage your AI agents";
    case "analytics":
      return "View performance metrics and conversation analytics";
    case "settings":
      return "System preferences and advanced configuration";
    default:
      return "Welcome to your admin panel";
  }
};

export default AdminLayout;
