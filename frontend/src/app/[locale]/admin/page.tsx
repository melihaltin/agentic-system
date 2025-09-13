"use client";

import React from "react";
import { useTranslations } from "next-intl";
import ProtectedRoute from "@/components/ProtectedRoute";
import Header from "@/components/Header";
import DashboardStats from "@/components/admin/DashboardStats";
import CompanySettings from "@/components/admin/CompanySettings";

const AdminDashboard: React.FC = () => {
  const t = useTranslations("admin");
  const tQuickActions = useTranslations("admin.quickActions");
  const tSystemStatus = useTranslations("admin.systemStatus");
  const tHelp = useTranslations("admin.help");

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Header />

        <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          {/* Welcome Section */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {t("dashboard.title")}
            </h1>
            <p className="text-gray-600">{t("dashboard.subtitle")}</p>
          </div>

          {/* Dashboard Stats */}
          <DashboardStats />

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Company Settings - Takes 2 columns on large screens */}
            <div className="lg:col-span-2">
              <CompanySettings />
            </div>

            {/* Quick Actions Sidebar */}
            <div className="space-y-6">
              {/* Quick Actions */}
              <div className="bg-white shadow-sm rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  {tQuickActions("title")}
                </h3>
                <div className="space-y-3">
                  <button className="w-full flex items-center px-4 py-3 text-left text-sm font-medium text-gray-700 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                    <svg
                      className="w-5 h-5 text-blue-500 mr-3"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 11H5m14-4l-4-4m4 4l-4 4"
                      />
                    </svg>
                    {tQuickActions("aiSettings")}
                  </button>

                  <button className="w-full flex items-center px-4 py-3 text-left text-sm font-medium text-gray-700 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                    <svg
                      className="w-5 h-5 text-green-500 mr-3"
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
                    {tQuickActions("reports")}
                  </button>

                  <button className="w-full flex items-center px-4 py-3 text-left text-sm font-medium text-gray-700 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                    <svg
                      className="w-5 h-5 text-purple-500 mr-3"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4"
                      />
                    </svg>
                    {tQuickActions("advancedSettings")}
                  </button>
                </div>
              </div>

              {/* System Status */}
              <div className="bg-white shadow-sm rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  {tSystemStatus("title")}
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">
                      {tSystemStatus("aiAssistant")}
                    </span>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      {tSystemStatus("online")}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">
                      {tSystemStatus("apiStatus")}
                    </span>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      {tSystemStatus("active")}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">
                      {tSystemStatus("lastUpdate")}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date().toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>

              {/* Help Section */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-lg font-medium text-blue-900 mb-2">
                  {tHelp("title")}
                </h3>
                <p className="text-sm text-blue-700 mb-4">
                  {tHelp("subtitle")}
                </p>
                <div className="flex space-x-3">
                  <button className="text-sm font-medium text-blue-600 hover:text-blue-500 transition-colors">
                    {tHelp("documentation")}
                  </button>
                  <button className="text-sm font-medium text-blue-600 hover:text-blue-500 transition-colors">
                    {tHelp("support")}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
};

export default AdminDashboard;
