"use client";

import React, { useState } from "react";
import { useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuthStore } from "@/store/auth";
import { Input, Button } from "@/components/ui";
import { Company } from "@/types";

const CompanySettings: React.FC = () => {
  const params = useParams();
  const locale = params.locale as string;
  const { company, updateCompany, isLoading } = useAuthStore();
  const t = useTranslations("admin.companySettings");
  const tValidation = useTranslations("auth.validation");

  const [formData, setFormData] = useState<Partial<Company>>({
    name: company?.name || "",
    aiAssistantName: company?.aiAssistantName || "",
    industry: company?.industry || "",
    website: company?.website || "",
    description: company?.description || "",
  });

  const [errors, setErrors] = useState<Partial<Company>>({});
  const [isEditing, setIsEditing] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (errors[name as keyof Company]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
    // Clear success message when user makes changes
    if (successMessage) {
      setSuccessMessage("");
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<Company> = {};

    if (!formData.name?.trim()) {
      newErrors.name = tValidation("required", { field: t("companyName") });
    }

    if (!formData.aiAssistantName?.trim()) {
      newErrors.aiAssistantName = tValidation("required", {
        field: t("aiAssistantName"),
      });
    }

    if (formData.website && formData.website.trim()) {
      try {
        new URL(formData.website);
      } catch {
        newErrors.website = tValidation("invalidUrl");
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    try {
      await updateCompany(formData);
      setIsEditing(false);
      setSuccessMessage(t("updateSuccess"));
      setTimeout(() => setSuccessMessage(""), 5000);
    } catch (error) {
      console.error("Update failed:", error);
    }
  };

  const handleCancel = () => {
    // Reset form data to original company data
    setFormData({
      name: company?.name || "",
      aiAssistantName: company?.aiAssistantName || "",
      industry: company?.industry || "",
      website: company?.website || "",
      description: company?.description || "",
    });
    setErrors({});
    setIsEditing(false);
    setSuccessMessage("");
  };

  return (
    <div className="bg-white shadow-sm rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-900">{t("title")}</h2>
          {!isEditing && (
            <Button
              onClick={() => setIsEditing(true)}
              variant="primary"
              size="sm"
            >
              {t("edit")}
            </Button>
          )}
        </div>
      </div>

      <div className="p-6">
        {successMessage && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-md">
            <div className="flex">
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

        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <Input
              label={t("companyName")}
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              error={errors.name}
              disabled={!isEditing}
              required
            />

            <Input
              label={t("aiAssistantName")}
              name="aiAssistantName"
              value={formData.aiAssistantName}
              onChange={handleInputChange}
              error={errors.aiAssistantName}
              disabled={!isEditing}
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <Input
              label={t("industry")}
              name="industry"
              value={formData.industry}
              onChange={handleInputChange}
              disabled={!isEditing}
              placeholder={t("industryPlaceholder")}
            />

            <Input
              label={t("website")}
              name="website"
              type="url"
              value={formData.website}
              onChange={handleInputChange}
              error={errors.website}
              disabled={!isEditing}
              placeholder={t("websitePlaceholder")}
            />
          </div>

          <div className="mb-6">
            <label
              htmlFor="description"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              {t("description")}
            </label>
            <textarea
              id="description"
              name="description"
              rows={4}
              value={formData.description}
              onChange={handleInputChange}
              disabled={!isEditing}
              className={`w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                !isEditing ? "bg-gray-50 cursor-not-allowed" : ""
              }`}
              placeholder={t("descriptionPlaceholder")}
            />
          </div>

          {/* Company Creation Date */}
          {company?.createdAt && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-medium text-gray-900 mb-2">
                {t("systemInfo")}
              </h3>
              <p className="text-sm text-gray-600">
                {t("registrationDate")}:{" "}
                {new Date(company.createdAt).toLocaleDateString(
                  locale === "tr" ? "tr-TR" : "en-US",
                  {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  }
                )}
              </p>
            </div>
          )}

          {isEditing && (
            <div className="flex justify-end space-x-3">
              <Button
                type="button"
                variant="secondary"
                onClick={handleCancel}
                disabled={isLoading}
              >
                {t("cancel")}
              </Button>
              <Button type="submit" isLoading={isLoading} disabled={isLoading}>
                {isLoading ? t("saving") : t("save")}
              </Button>
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default CompanySettings;
