"use client";

import React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui";

const RegistrationSuccess: React.FC = () => {
  const params = useParams();
  const locale = params.locale as string;
  const t = useTranslations("auth.registrationSuccess");

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow rounded-lg sm:px-10">
          <div className="text-center">
            {/* Success Icon */}
            <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-6">
              <svg
                className="h-8 w-8 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              {t("title")}
            </h2>
            <p className="text-lg text-gray-600 mb-6">{t("subtitle")}</p>
            <div className="bg-blue-50 p-4 rounded-lg mb-6">
              <h3 className="text-sm font-semibold text-blue-900 mb-2">
                {t("nextStepsTitle")}
              </h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>{t("nextSteps.testing")}</li>
                <li>{t("nextSteps.configuring")}</li>
                <li>{t("nextSteps.completing")}</li>
              </ul>
            </div>{" "}
            <div className="space-y-4">
              <Button className="w-full bg-green-600 hover:bg-green-700">
                <Link href={`/${locale}/admin`}>{t("actions.goToAdmin")}</Link>
              </Button>

              <Button variant="secondary" className="w-full">
                <Link href={`/${locale}/dashboard`}>
                  {t("actions.goToDashboard")}
                </Link>
              </Button>
            </div>
            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-xs text-gray-500">
                {t("support.text")}{" "}
                <Link
                  href={`/${locale}/support`}
                  className="text-blue-600 hover:text-blue-500"
                >
                  {t("support.link")}
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegistrationSuccess;
