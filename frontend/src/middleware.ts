import createMiddleware from "next-intl/middleware";
import { locales } from "./i18n";
import { updateSession } from "@/lib/supabase/middleware";
import { NextRequest } from "next/server";

const intlMiddleware = createMiddleware({
  // A list of all locales that are supported
  locales,

  // Used when no locale matches
  defaultLocale: "tr",
});

export async function middleware(request: NextRequest) {
  // First handle authentication
  const response = await updateSession(request);

  // Then handle internationalization
  const intlResponse = intlMiddleware(request);

  // Merge headers from both middlewares
  if (intlResponse && response) {
    intlResponse.headers.forEach((value, key) => {
      response.headers.set(key, value);
    });
  }

  return response || intlResponse;
}

export const config = {
  // Match only internationalized pathnames, exclude static files and API routes
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
