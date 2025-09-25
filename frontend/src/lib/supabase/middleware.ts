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

  const { data: sessionData } = await supabase.auth.getSession();
  const user = sessionData?.session?.user ?? null;

  if (user) {
    response.headers.set("x-user-id", user.id);
    if (user.email) response.headers.set("x-user-email", user.email);
  } else {
    response.headers.delete("x-user-id");
    response.headers.delete("x-user-email");
  }

  const url = request.nextUrl.clone();
  const locale = getLocaleFromPath(url.pathname);

  if (url.pathname === "/") {
    const target = buildPath(locale, "/admin");
    return {
      response: NextResponse.redirect(new URL(target, request.url)),
      user,
    };
  }

  const loginPath = buildPath(locale, "/login");
  const registerPath = buildPath(locale, "/register");
  const isAuthPage =
    url.pathname === loginPath || url.pathname === registerPath;

  if (!user && !isAuthPage) {
    url.pathname = loginPath;
    return { response: NextResponse.redirect(url), user: null };
  }

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
