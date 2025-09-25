"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, useParams } from "next/navigation";
import { useTranslations } from "next-intl";

// Shadcn/ui bileşenlerini içe aktarın
import { Label } from "@/components/ui/label";
import LanguageSwitcher from "@/components/LanguageSwitcher";
import { useAuthStore } from "@/store/auth";
import { LoginCredentials } from "@/types/auth.types";
import { Button, Input } from "@/components/ui";

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

  // Auth store'u bileşen yüklendiğinde başlat
  useEffect(() => {
    initialize();
  }, [initialize]);

  // Eğer kullanıcı zaten giriş yapmışsa yönlendir
  useEffect(() => {
    if (user && !loading) {
      router.push(`/${locale}/admin`);
    }
  }, [user, loading, router, locale]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Kullanıcı yazmaya başladığında hatayı temizle
    if (errors[name as keyof LoginCredentials]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
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
      await login(formData);
    } catch (error: any) {
      console.error("Login failed:", error);
      // API'den gelen genel hatayı göster
      setErrors({
        email: error?.message || t("invalidCredentials"),
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      {/* Dil Değiştirici */}
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
            <div className="grid w-full items-center gap-1.5">
              <Label htmlFor="email">{t("email")}</Label>
              <Input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleInputChange}
                autoComplete="email"
                className={
                  errors.email
                    ? "border-red-500 focus-visible:ring-red-500"
                    : ""
                }
              />
              {errors.email && (
                <p className="text-sm text-red-500 mt-1">{errors.email}</p>
              )}
            </div>

            <div className="grid w-full items-center gap-1.5">
              <Label htmlFor="password">{t("password")}</Label>
              <Input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleInputChange}
                autoComplete="current-password"
                className={
                  errors.password
                    ? "border-red-500 focus-visible:ring-red-500"
                    : ""
                }
              />
              {errors.password && (
                <p className="text-sm text-red-500 mt-1">{errors.password}</p>
              )}
            </div>

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

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? t("loggingIn") : t("loginButton")}
            </Button>

            <div className="text-center">
              <span className="text-sm text-gray-600">
                {t("noAccount")}{" "}
                <Link
                  href={`/${locale}/register`}
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
