"use client";

import { useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuthStore } from "@/store/auth";
import { useTranslations } from "next-intl";
import Link from "next/link";
import LanguageSwitcher from "@/components/LanguageSwitcher";

export default function Home() {
  const router = useRouter();
  const params = useParams();
  const locale = params.locale as string;
  const isAuthenticated = true;
  const t = useTranslations("common");

  useEffect(() => {
    if (isAuthenticated) {
      router.push(`/${locale}/admin`);
    }
  }, [isAuthenticated, router, locale]);

  // Eğer kullanıcı giriş yapmışsa admin sayfasına yönlendir
  if (isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">{t("redirecting")}</p>
        </div>
      </div>
    );
  }

  // Giriş yapmamış kullanıcılar için ana sayfa
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Language Switcher */}
      <div className="absolute top-4 right-4">
        <LanguageSwitcher />
      </div>

      <div className="flex items-center justify-center min-h-screen">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            {/* Hero Section */}
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              AI Asistan
              <span className="text-blue-600"> Yönetim Sistemi</span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Yapay zeka destekli asistan sisteminizi kolayca yönetin ve
              konfigüre edin
            </p>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                href={`/${locale}/login`}
                className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                Giriş Yap
              </Link>

              <Link
                href={`/${locale}/register`}
                className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold border-2 border-blue-600 hover:bg-blue-50 transition-colors"
              >
                Hesap Oluştur
              </Link>
            </div>

            {/* Features */}
            <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  Kolay Yönetim
                </h3>
                <p className="text-gray-600">
                  AI asistanınızı kolayca konfigüre edin ve yönetin
                </p>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  Gerçek Zamanlı İzleme
                </h3>
                <p className="text-gray-600">
                  Sistem performansını ve kullanım istatistiklerini izleyin
                </p>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  Özelleştirilebilir
                </h3>
                <p className="text-gray-600">
                  İhtiyaçlarınıza göre AI asistanınızı özelleştirin
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
