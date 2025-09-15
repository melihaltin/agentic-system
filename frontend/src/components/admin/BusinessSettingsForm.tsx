"use client";

import React, { useState } from "react";
import { BusinessSettings } from "@/types/admin.types";

// Mock data service - will be replaced with real API
const getMockBusinessSettings = (): BusinessSettings => ({
  companyName: "Demo Company Inc.",
  companyEmail: "contact@democompany.com",
  companyPhone: "+1 (555) 123-4567",
  businessCategory: "e-commerce",
  platform: "shopify",
  apiKey: "sk_test_123456789",
  apiSecret: "sk_secret_987654321",
  address: "123 Business Ave, Suite 100, New York, NY 10001",
  website: "https://democompany.com",
  timezone: "America/New_York",
  currency: "USD",
});

const BusinessSettingsForm: React.FC = () => {
  const [settings, setSettings] = useState<BusinessSettings>(
    getMockBusinessSettings()
  );
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setSettings((prev) => ({ ...prev, [name]: value }));

    // Clear success message when user makes changes
    if (successMessage) {
      setSuccessMessage("");
    }
  };

  const handleSave = async () => {
    setIsLoading(true);
    try {
      // Mock API call - simulate delay
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // In real implementation, this would be an API call
      console.log("Saving business settings:", settings);

      setIsEditing(false);
      setSuccessMessage("Business settings updated successfully!");

      // Clear success message after 5 seconds
      setTimeout(() => setSuccessMessage(""), 5000);
    } catch (error) {
      console.error("Error saving settings:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    // Reset to original mock data
    setSettings(getMockBusinessSettings());
    setIsEditing(false);
    setSuccessMessage("");
  };

  return (
    <div className="space-y-6">
      {/* Success Message */}
      {successMessage && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-green-400"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-green-800">
                {successMessage}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Company Information */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Company Information
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Basic information about your company
            </p>
          </div>
          {!isEditing && (
            <button
              onClick={() => setIsEditing(true)}
              className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
            >
              Edit Settings
            </button>
          )}
        </div>

        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
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
                ${isEditing ? "bg-white" : "bg-gray-50"}
                ${
                  isEditing
                    ? "focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    : ""
                }
                transition-colors
              `}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
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
                ${isEditing ? "bg-white" : "bg-gray-50"}
                ${
                  isEditing
                    ? "focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    : ""
                }
                transition-colors
              `}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
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
                ${isEditing ? "bg-white" : "bg-gray-50"}
                ${
                  isEditing
                    ? "focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    : ""
                }
                transition-colors
              `}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Business Category
            </label>
            <select
              name="businessCategory"
              value={settings.businessCategory}
              onChange={handleInputChange}
              disabled={!isEditing}
              className={`
                w-full px-3 py-2 border border-gray-300 rounded-lg
                ${isEditing ? "bg-white" : "bg-gray-50"}
                ${
                  isEditing
                    ? "focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    : ""
                }
                transition-colors
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
            <label className="block text-sm font-medium text-gray-700 mb-2">
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
                ${isEditing ? "bg-white" : "bg-gray-50"}
                ${
                  isEditing
                    ? "focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    : ""
                }
                transition-colors
              `}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
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
                ${isEditing ? "bg-white" : "bg-gray-50"}
                ${
                  isEditing
                    ? "focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    : ""
                }
                transition-colors
              `}
            />
          </div>
        </div>
      </div>

      {/* API Configuration */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            API Configuration
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Platform integration settings
          </p>
        </div>

        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Platform
            </label>
            <select
              name="platform"
              value={settings.platform}
              onChange={handleInputChange}
              disabled={!isEditing}
              className={`
                w-full px-3 py-2 border border-gray-300 rounded-lg
                ${isEditing ? "bg-white" : "bg-gray-50"}
                ${
                  isEditing
                    ? "focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    : ""
                }
                transition-colors
              `}
            >
              <option value="shopify">Shopify</option>
              <option value="woocommerce">WooCommerce</option>
              <option value="magento">Magento</option>
              <option value="custom">Custom API</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Currency
            </label>
            <select
              name="currency"
              value={settings.currency}
              onChange={handleInputChange}
              disabled={!isEditing}
              className={`
                w-full px-3 py-2 border border-gray-300 rounded-lg
                ${isEditing ? "bg-white" : "bg-gray-50"}
                ${
                  isEditing
                    ? "focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    : ""
                }
                transition-colors
              `}
            >
              <option value="USD">USD - US Dollar</option>
              <option value="EUR">EUR - Euro</option>
              <option value="TRY">TRY - Turkish Lira</option>
              <option value="GBP">GBP - British Pound</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              API Key
            </label>
            <input
              type="password"
              name="apiKey"
              value={settings.apiKey}
              onChange={handleInputChange}
              disabled={!isEditing}
              className={`
                w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm
                ${isEditing ? "bg-white" : "bg-gray-50"}
                ${
                  isEditing
                    ? "focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    : ""
                }
                transition-colors
              `}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              API Secret
            </label>
            <input
              type="password"
              name="apiSecret"
              value={settings.apiSecret}
              onChange={handleInputChange}
              disabled={!isEditing}
              className={`
                w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm
                ${isEditing ? "bg-white" : "bg-gray-50"}
                ${
                  isEditing
                    ? "focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    : ""
                }
                transition-colors
              `}
            />
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      {isEditing && (
        <div className="flex justify-end space-x-3">
          <button
            onClick={handleCancel}
            disabled={isLoading}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={isLoading}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
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
