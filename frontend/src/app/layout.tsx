import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { AuthInitializer } from "@/components/AuthInitializer";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Agent Platform",
  description: "Manage your AI agents",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthInitializer>{children}</AuthInitializer>
      </body>
    </html>
  );
}
