"use client";

import React from "react";
import Link from "next/link";
import { useParams, usePathname } from "next/navigation";
import { locales } from "@/i18n";

const LanguageSwitcher: React.FC = () => {
  const params = useParams();
  const pathname = usePathname();
  const currentLocale = params.locale as string;

  // Remove the locale from the current pathname
  const pathnameWithoutLocale =
    pathname.replace(`/${currentLocale}`, "") || "/";

  const getLanguageName = (code: string) => {
    try {
      // Use the language subtag for naming (e.g., "en" from "en-US")
      const lang = code.split("-")[0];
      const dn = new Intl.DisplayNames(["en"], { type: "language" });
      return dn.of(lang) || code;
    } catch {
      return code;
    }
  };

  const getFlagEmoji = (_code: string) => {
    // Generic fallback without hardcoding per-locale flags
    return "🌐";
  };

  return (
    <div className="relative inline-block text-left">
      <div className="flex items-center space-x-2">
        {locales.map((locale) => (
          <Link
            key={locale}
            href={`/${locale}${pathnameWithoutLocale}`}
            className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              currentLocale === locale
                ? "bg-blue-100 text-blue-800 cursor-default"
                : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            }`}
          >
            <span className="mr-1">{getFlagEmoji(locale)}</span>
            {getLanguageName(locale as string)}
          </Link>
        ))}
      </div>
    </div>
  );
};

export default LanguageSwitcher;
