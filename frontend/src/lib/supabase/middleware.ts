import { createServerClient, type CookieOptions } from "@supabase/ssr";
import { NextRequest, NextResponse } from "next/server";

function getLocaleFromPath(pathname: string): string | null {
  const parts = pathname.split("/").filter(Boolean);
  return parts.length > 0 ? parts[0] : null;
}

function buildPath(locale: string | null, path: string) {
  if (!locale) return path;
  return `/${locale}${path.startsWith("/") ? path : `/${path}`}`;
}

export async function updateSession(request: NextRequest) {
  let response = NextResponse.next({ request: { headers: request.headers } });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return request.cookies.get(name)?.value;
        },
        set(name: string, value: string, options: CookieOptions) {
          request.cookies.set({ name, value, ...options });
          response.cookies.set({ name, value, ...options });
        },
        remove(name: string, options: CookieOptions) {
          request.cookies.set({ name, value: "", ...options });
          response.cookies.set({ name, value: "", ...options });
        },
      },
    }
  );

  // Use getSession for more reliable cookie-based auth detection
  const { data: sessionData } = await supabase.auth.getSession();
  const user = sessionData?.session?.user ?? null;

  if (user) {
    response.headers.set("x-user-id", user.id);
    if (user.email) response.headers.set("x-user-email", user.email);
  } else {
    response.headers.delete("x-user-id");
    response.headers.delete("x-user-email");
  }

  // Auth guards
  const url = request.nextUrl.clone();
  const locale = getLocaleFromPath(url.pathname);

  console.log("Locale detected in middleware:", locale);
  const loginPath = buildPath(locale, "/login");
  const registerPath = buildPath(locale, "/register");
  const isAuthPage =
    url.pathname === loginPath || url.pathname === registerPath;

  // Not authenticated: allow only login/register
  if (!user && !isAuthPage) {
    url.pathname = loginPath;
    return { response: NextResponse.redirect(url), user: null };
  }

  // Authenticated: prevent access to login/register
  if (user && isAuthPage) {
    url.pathname = buildPath(locale, "/admin");
    return { response: NextResponse.redirect(url), user };
  }

  return { response, user };
}

export async function middleware(request: NextRequest) {
  const { response } = await updateSession(request);
  return response;
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
