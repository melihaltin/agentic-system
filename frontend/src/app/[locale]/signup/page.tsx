"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { Input, Button } from "@/components/ui";
import LanguageSwitcher from "@/components/LanguageSwitcher";
import { useAuthStore } from "@/store/auth";
import { RegisterData } from "@/types/auth.types";

interface SignUpData extends RegisterData {
  confirmPassword: string;
  firstName: string;
  lastName: string;
}

const SignUp: React.FC = () => {
  const router = useRouter();
  const params = useParams();
  const locale = params.locale as string;
  const { register, user, loading, initialize } = useAuthStore();
  const t = useTranslations("auth.signup");
  const tValidation = useTranslations("auth.validation");

  const [isLoading, setIsLoading] = useState(false);

  const [formData, setFormData] = useState<SignUpData>({
    email: "",
    password: "",
    confirmPassword: "",
    firstName: "",
    lastName: "",
    full_name: "", // Add this for RegisterData compatibility
  });

  const [errors, setErrors] = useState<Partial<SignUpData>>({});

  // Initialize auth store on component mount
  useEffect(() => {
    initialize();
  }, [initialize]);

  // Redirect if already logged in
  useEffect(() => {
    if (user && !loading) {
      router.push(`/${locale}/admin`);
    }
  }, [user, loading, router, locale]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev: SignUpData) => {
      const newData = { ...prev, [name]: value };
      // Update full_name when firstName or lastName changes
      if (name === "firstName" || name === "lastName") {
        const firstName = name === "firstName" ? value : prev.firstName;
        const lastName = name === "lastName" ? value : prev.lastName;
        newData.full_name = `${firstName} ${lastName}`.trim();
      }
      return newData;
    });
    // Clear error when user starts typing
    if (errors[name as keyof SignUpData]) {
      setErrors((prev: Partial<SignUpData>) => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<SignUpData> = {};

    if (!formData.firstName.trim()) {
      newErrors.firstName = tValidation("required", { field: t("firstName") });
    }

    if (!formData.lastName.trim()) {
      newErrors.lastName = tValidation("required", { field: t("lastName") });
    }

    if (!formData.email.trim()) {
      newErrors.email = tValidation("required", { field: t("email") });
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = tValidation("invalidEmail");
    }

    if (!formData.password.trim()) {
      newErrors.password = tValidation("required", { field: t("password") });
    } else if (formData.password.length < 6) {
      newErrors.password = t("passwordTooShort");
    }

    if (!formData.confirmPassword.trim()) {
      newErrors.confirmPassword = tValidation("required", {
        field: t("confirmPassword"),
      });
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = t("passwordsDoNotMatch");
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsLoading(true);
    try {
      await register({
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
      });

      // Show success message or redirect
      alert(t("checkEmail"));
      router.push(`/${locale}/login`);
    } catch (error: any) {
      console.error("Sign up failed:", error);
      setErrors({
        email: error?.message || t("signUpFailed"),
      });
    } finally {
      setIsLoading(false);
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
            <div className="grid grid-cols-2 gap-4">
              <Input
                label={t("firstName")}
                name="firstName"
                type="text"
                value={formData.firstName}
                onChange={handleInputChange}
                error={errors.firstName}
                autoComplete="given-name"
                required
              />

              <Input
                label={t("lastName")}
                name="lastName"
                type="text"
                value={formData.lastName}
                onChange={handleInputChange}
                error={errors.lastName}
                autoComplete="family-name"
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
              autoComplete="email"
              required
            />

            <Input
              label={t("password")}
              name="password"
              type="password"
              value={formData.password}
              onChange={handleInputChange}
              error={errors.password}
              autoComplete="new-password"
              required
            />

            <Input
              label={t("confirmPassword")}
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              error={errors.confirmPassword}
              autoComplete="new-password"
              required
            />

            <Button
              type="submit"
              className="w-full"
              isLoading={isLoading}
              disabled={isLoading}
            >
              {isLoading ? t("signingUp") : t("signUpButton")}
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

export default SignUp;
