"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter, useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { Input, Button } from "@/components/ui";
import LanguageSwitcher from "@/components/LanguageSwitcher";
import { useAuthStore } from "@/store/auth";
import { RegisterData } from "@/types";

const Register: React.FC = () => {
  const router = useRouter();
  const params = useParams();
  const locale = params.locale as string;
  const { register, isLoading } = useAuthStore();
  const t = useTranslations("auth.register");
  const tValidation = useTranslations("auth.validation");

  const [formData, setFormData] = useState<RegisterData>({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    companyName: "",
    aiAssistantName: "",
    industry: "",
    website: "",
    description: "",
  });

  const [errors, setErrors] = useState<Partial<RegisterData>>({});

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (errors[name as keyof RegisterData]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<RegisterData> = {};

    // Required fields validation
    if (!formData.firstName.trim())
      newErrors.firstName = tValidation("required", { field: t("firstName") });
    if (!formData.lastName.trim())
      newErrors.lastName = tValidation("required", { field: t("lastName") });
    if (!formData.email.trim())
      newErrors.email = tValidation("required", { field: t("email") });
    if (!formData.password.trim())
      newErrors.password = tValidation("required", { field: t("password") });
    if (!formData.companyName.trim())
      newErrors.companyName = tValidation("required", {
        field: t("companyName"),
      });
    if (!formData.aiAssistantName.trim())
      newErrors.aiAssistantName = tValidation("required", {
        field: t("aiAssistantName"),
      });

    // Email validation
    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = tValidation("invalidEmail");
    }

    // Password validation
    if (formData.password && formData.password.length < 6) {
      newErrors.password = tValidation("passwordMinLength");
    }

    // Website validation
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
      await register(formData);
      router.push(`/${locale}/admin`);
    } catch (error) {
      console.error("Registration failed:", error);
      // Handle registration error
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      {/* Language Switcher */}
      <div className="absolute top-4 right-4">
        <LanguageSwitcher />
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <div className="sm:mx-auto sm:w-full sm:max-w-md mb-8">
            <h2 className="text-center text-3xl font-extrabold text-gray-900">
              {t("title")}
            </h2>
            <p className="mt-2 text-center text-sm text-gray-600">
              {t("subtitle")}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Personal Information */}
            <div className="border-b border-gray-200 pb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {t("personalInfo")}
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label={t("firstName")}
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleInputChange}
                  error={errors.firstName}
                  required
                />
                <Input
                  label={t("lastName")}
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleInputChange}
                  error={errors.lastName}
                  required
                />
              </div>
              <Input
                label={t("email")}
                name="email"
                type="email"
                value={formData.email}
                onChange={handleInputChange}
                error={errors.email}
                required
              />
              <Input
                label={t("password")}
                name="password"
                type="password"
                value={formData.password}
                onChange={handleInputChange}
                error={errors.password}
                required
              />
            </div>

            {/* Company Information */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {t("companyInfo")}
              </h3>
              <Input
                label={t("companyName")}
                name="companyName"
                value={formData.companyName}
                onChange={handleInputChange}
                error={errors.companyName}
                required
              />
              <Input
                label={t("aiAssistantName")}
                name="aiAssistantName"
                value={formData.aiAssistantName}
                onChange={handleInputChange}
                error={errors.aiAssistantName}
                placeholder={t("aiAssistantPlaceholder")}
                required
              />
              <Input
                label={t("industry")}
                name="industry"
                value={formData.industry}
                onChange={handleInputChange}
                placeholder={t("industryPlaceholder")}
              />
              <Input
                label={t("website")}
                name="website"
                type="url"
                value={formData.website}
                onChange={handleInputChange}
                error={errors.website}
                placeholder={t("websitePlaceholder")}
              />
              <div className="mb-4">
                <label
                  htmlFor="description"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  {t("description")}
                </label>
                <textarea
                  id="description"
                  name="description"
                  rows={3}
                  value={formData.description}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder={t("descriptionPlaceholder")}
                />
              </div>
            </div>

            <Button
              type="submit"
              className="w-full"
              isLoading={isLoading}
              disabled={isLoading}
            >
              {isLoading ? t("registering") : t("registerButton")}
            </Button>

            <div className="text-center">
              <span className="text-sm text-gray-600">
                {t("haveAccount")}{" "}
                <Link
                  href={`/${locale}/login`}
                  className="font-medium text-blue-600 hover:text-blue-500 transition-colors"
                >
                  {t("signIn")}
                </Link>
              </span>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Register;
