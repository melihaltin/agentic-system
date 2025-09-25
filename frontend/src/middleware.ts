import createMiddleware from "next-intl/middleware";
import { locales } from "./i18n";
import { updateSession } from "@/lib/supabase/middleware";
import { NextRequest } from "next/server";

const intlMiddleware = createMiddleware({
  locales,
  defaultLocale: "en",
});

export async function middleware(request: NextRequest) {
  const { response } = await updateSession(request);

  const intlResponse = intlMiddleware(request);

  if (intlResponse && response) {
    intlResponse.headers.forEach((value, key) => {
      response.headers.set(key, value);
    });
  }

  return response || intlResponse;
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
