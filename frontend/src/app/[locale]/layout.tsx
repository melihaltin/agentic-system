import { NextIntlClientProvider } from "next-intl";
import { getMessages } from "next-intl/server";
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { AuthProvider } from "@/contexts/AuthContext";
import "../globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Asistan - Yönetim Paneli",
  description: "AI Asistan yönetim ve konfigürasyon paneli",
};

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const resolvedParams = await params;
  console.log("DEBUG - Resolved params:", resolvedParams);
  const { locale } = resolvedParams;
  console.log("DEBUG - Extracted locale:", locale);

  // Safe message loading with error handling
  let messages;
  try {
    console.log(
      `DEBUG - Layout attempting to get messages for locale: ${locale}`
    );
    messages = await getMessages({ locale });
    console.log(
      `DEBUG - Layout successfully got messages for locale: ${locale}`
    );
  } catch (error) {
    console.error("Error loading messages:", error);
    // Provide a fallback empty object
    messages = {};
  }

  return (
    <html lang={locale}>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <NextIntlClientProvider messages={messages}>
          <AuthProvider>{children}</AuthProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
