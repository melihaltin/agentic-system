"use client";

import React, { useState, useEffect } from "react";
import { BusinessSettings } from "@/types/admin.types";
import { useAuthStore } from "@/store/auth";

const BusinessSettingsForm: React.FC = () => {
  const { profile, updateProfile, refreshProfile, loading, initialized } =
    useAuthStore();
  const [settings, setSettings] = useState<BusinessSettings>({
    companyName: "",
    companyEmail: "",
    companyPhone: "",
    businessCategory: "e-commerce",
    address: "",
    website: "",
    timezone: "America/New_York",
    currency: "USD",
  });
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    if (profile) {
      setSettings({
        companyName: profile.company?.company_name || "",
        companyEmail: profile.email,
        companyPhone: profile.company?.phone_number || "",
        businessCategory: profile.company?.business_category || "e-commerce",
        address: profile.company?.address || "",
        website: profile.company?.website || "",
        timezone: profile.company?.timezone || "America/New_York",
        currency: profile.company?.currency || "USD",
      });
      setIsEditing(false);
    }
  }, [profile]);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setSettings((prev) => ({ ...prev, [name]: value }));
    if (successMessage) setSuccessMessage("");
  };

  const handleSave = async () => {
    setIsLoading(true);
    try {
      await updateProfile({
        full_name: profile?.full_name,
        company_name: settings.companyName,
        phone_number: settings.companyPhone,
        business_category: settings.businessCategory,
        address: settings.address,
        website: settings.website,
        timezone: settings.timezone,
        currency: settings.currency,
      });
      await refreshProfile();
      setIsEditing(false);
      setSuccessMessage("Business settings updated successfully!");
      setTimeout(() => setSuccessMessage(""), 5000);
    } catch (error: any) {
      const errorMessage =
        error?.message || "Failed to update settings. Please try again.";
      setSuccessMessage(`Error: ${errorMessage}`);
      setTimeout(() => setSuccessMessage(""), 5000);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    if (profile) {
      setSettings({
        companyName: profile.company?.company_name || "",
        companyEmail: profile.email,
        companyPhone: profile.company?.phone_number || "",
        businessCategory: profile.company?.business_category || "e-commerce",
        address: profile.company?.address || "",
        website: profile.company?.website || "",
        timezone: profile.company?.timezone || "America/New_York",
        currency: profile.company?.currency || "USD",
      });
    }
    setIsEditing(false);
    setSuccessMessage("");
  };

  if (!initialized || (loading && !profile)) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-700 font-medium">
          Loading business settings...
        </span>
      </div>
    );
  }

  if (initialized && !profile && !loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-center">
          <p className="text-gray-700 font-medium">No profile data found.</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-2 text-blue-700 font-semibold hover:text-blue-900 underline"
          >
            Refresh Page
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Success/Error Message */}
      {successMessage && (
        <div
          className={`${
            successMessage.startsWith("Error:")
              ? "bg-red-100 border-red-400"
              : "bg-green-100 border-green-400"
          } border rounded-lg p-4 shadow-sm`}
        >
          <div className="flex items-center">
            <div className="flex-shrink-0">
              {successMessage.startsWith("Error:") ? (
                <svg
                  className="h-5 w-5 text-red-500"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              ) : (
                <svg
                  className="h-5 w-5 text-green-600"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
            </div>
            <div className="ml-3">
              <p
                className={`text-sm font-semibold ${
                  successMessage.startsWith("Error:")
                    ? "text-red-800"
                    : "text-green-800"
                }`}
              >
                {successMessage}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Company Information */}
      <div className="bg-white rounded-2xl shadow-md border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <div>
            <h3 className="text-lg font-bold text-gray-900">
              Company Information
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              Basic information about your company
            </p>
          </div>
          {!isEditing && (
            <button
              onClick={() => setIsEditing(true)}
              className="px-5 py-2 text-sm font-bold text-white bg-blue-600 rounded-xl shadow hover:bg-blue-700 transition-all"
            >
              Edit Settings
            </button>
          )}
        </div>

        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-1">
              Company Name
            </label>
            <input
              type="text"
              name="companyName"
              value={settings.companyName}
              onChange={handleInputChange}
              disabled={!isEditing}
              className={`
                w-full px-3 py-2 border border-gray-300 rounded-lg
                text-gray-900 font-medium placeholder-gray-400
                ${isEditing ? "bg-white" : "bg-gray-100"}
                focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent
                transition-all
              `}
              placeholder="Enter company name"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-1">
              Company Email
            </label>
            <input
              type="email"
              name="companyEmail"
              value={settings.companyEmail}
              onChange={handleInputChange}
              disabled={!isEditing}
              className={`
                w-full px-3 py-2 border border-gray-300 rounded-lg
                text-gray-900 font-medium placeholder-gray-400
                ${isEditing ? "bg-white" : "bg-gray-100"}
                focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent
                transition-all
              `}
              placeholder="Enter company email"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-1">
              Phone Number
            </label>
            <input
              type="tel"
              name="companyPhone"
              value={settings.companyPhone}
              onChange={handleInputChange}
              disabled={!isEditing}
              className={`
                w-full px-3 py-2 border border-gray-300 rounded-lg
                text-gray-900 font-medium placeholder-gray-400
                ${isEditing ? "bg-white" : "bg-gray-100"}
                focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent
                transition-all
              `}
              placeholder="Enter phone number"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-1">
              Business Category
            </label>
            <select
              name="businessCategory"
              value={settings.businessCategory}
              onChange={handleInputChange}
              disabled={!isEditing}
              className={`
                w-full px-3 py-2 border border-gray-300 rounded-lg
                text-gray-900 font-medium
                ${isEditing ? "bg-white" : "bg-gray-100"}
                focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent
                transition-all
              `}
            >
              <option value="e-commerce">E-commerce</option>
              <option value="car-rental">Car Rental</option>
              <option value="hospitality">Hospitality</option>
              <option value="healthcare">Healthcare</option>
              <option value="real-estate">Real Estate</option>
            </select>
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-semibold text-gray-800 mb-1">
              Address
            </label>
            <input
              type="text"
              name="address"
              value={settings.address || ""}
              onChange={handleInputChange}
              disabled={!isEditing}
              placeholder="Enter your business address"
              className={`
                w-full px-3 py-2 border border-gray-300 rounded-lg
                text-gray-900 font-medium placeholder-gray-400
                ${isEditing ? "bg-white" : "bg-gray-100"}
                focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent
                transition-all
              `}
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-1">
              Website
            </label>
            <input
              type="url"
              name="website"
              value={settings.website || ""}
              onChange={handleInputChange}
              disabled={!isEditing}
              placeholder="https://yourwebsite.com"
              className={`
                w-full px-3 py-2 border border-gray-300 rounded-lg
                text-gray-900 font-medium placeholder-gray-400
                ${isEditing ? "bg-white" : "bg-gray-100"}
                focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent
                transition-all
              `}
            />
          </div>
        </div>
      </div>

      {/* Business Settings */}
      <div className="bg-white rounded-2xl shadow-md border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-bold text-gray-900">Business Settings</h3>
          <p className="text-sm text-gray-500 mt-1">
            Regional and currency settings
          </p>
        </div>
        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-1">
              Timezone
            </label>
            <select
              name="timezone"
              value={settings.timezone}
              onChange={handleInputChange}
              disabled={!isEditing}
              className={`
                w-full px-3 py-2 border border-gray-300 rounded-lg
                text-gray-900 font-medium
                ${isEditing ? "bg-white" : "bg-gray-100"}
                focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent
                transition-all
              `}
            >
              <option value="America/New_York">Eastern Time</option>
              <option value="America/Chicago">Central Time</option>
              <option value="America/Denver">Mountain Time</option>
              <option value="America/Los_Angeles">Pacific Time</option>
              <option value="Europe/London">London</option>
              <option value="Europe/Istanbul">Istanbul</option>
            </select>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      {isEditing && (
        <div className="flex justify-end space-x-3">
          <button
            onClick={handleCancel}
            disabled={isLoading}
            className="px-5 py-2 text-sm font-bold text-gray-700 bg-white border border-gray-300 rounded-xl shadow hover:bg-gray-100 transition-all disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={isLoading}
            className="px-5 py-2 text-sm font-bold text-white bg-gradient-to-r from-blue-600 to-blue-500 rounded-xl shadow hover:from-blue-700 hover:to-blue-600 transition-all disabled:opacity-50 flex items-center space-x-2"
          >
            {isLoading && (
              <svg
                className="animate-spin h-4 w-4 text-white"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
            )}
            <span>{isLoading ? "Saving..." : "Save Changes"}</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default BusinessSettingsForm;
