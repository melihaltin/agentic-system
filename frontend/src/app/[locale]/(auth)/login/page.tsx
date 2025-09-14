"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { Input, Button } from "@/components/ui";
import LanguageSwitcher from "@/components/LanguageSwitcher";
import { useAuthStore } from "@/store/auth";
import { LoginCredentials } from "@/types/auth.types";

const Login: React.FC = () => {
  const router = useRouter();
  const params = useParams();
  const locale = params.locale as string;
  const { login, user, loading, initialize } = useAuthStore();
  const t = useTranslations("auth.login");
  const tValidation = useTranslations("auth.validation");

  const [isLoading, setIsLoading] = useState(false);

  const [formData, setFormData] = useState<LoginCredentials>({
    email: "",
    password: "",
  });

  const [errors, setErrors] = useState<Partial<LoginCredentials>>({});

  // Initialize auth store on component mount
  useEffect(() => {
    initialize();
  }, [initialize]);

  // Redirect if already logged in
  useEffect(() => {
    if (user && !loading) {
      console.log("User:", user);
      router.push(`/${locale}/admin`);
    }
  }, [user, loading, router, locale]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev: LoginCredentials) => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (errors[name as keyof LoginCredentials]) {
      setErrors((prev: Partial<LoginCredentials>) => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<LoginCredentials> = {};

    if (!formData.email.trim()) {
      newErrors.email = tValidation("required", { field: t("email") });
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = tValidation("invalidEmail");
    }

    if (!formData.password.trim()) {
      newErrors.password = tValidation("required", { field: t("password") });
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsLoading(true);
    try {
      const result = await login(formData);
      console.log("Login successful, redirecting...", result);
    } catch (error: any) {
      console.error("Login failed:", error);
      setErrors({
        email: error?.message || t("invalidCredentials"),
        password: error?.message || t("invalidCredentials"),
      });
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
              autoComplete="current-password"
              required
            />

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label
                  htmlFor="remember-me"
                  className="ml-2 block text-sm text-gray-900"
                >
                  {t("rememberMe")}
                </label>
              </div>

              <div className="text-sm">
                <a
                  href="#"
                  className="font-medium text-blue-600 hover:text-blue-500 transition-colors"
                >
                  {t("forgotPassword")}
                </a>
              </div>
            </div>

            <Button
              type="submit"
              className="w-full"
              isLoading={isLoading}
              disabled={isLoading}
            >
              {isLoading ? t("loggingIn") : t("loginButton")}
            </Button>

            <div className="text-center">
              <span className="text-sm text-gray-600">
                {t("noAccount")}{" "}
                <Link
                  href={`/${locale}/signup`}
                  className="font-medium text-blue-600 hover:text-blue-500 transition-colors"
                >
                  {t("createAccount")}
                </Link>
              </span>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
