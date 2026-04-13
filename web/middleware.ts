import { getToken } from "next-auth/jwt";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export async function middleware(req: NextRequest) {
  const token = await getToken({ req, secret: process.env.AUTH_SECRET });
  const isAuth = !!token;
  const path = req.nextUrl.pathname;

  // Protegemos rutas que requieren estar logueado
  if (!isAuth && (path.startsWith("/profile") || path.startsWith("/checkout") || path.startsWith("/admin"))) {
    return NextResponse.redirect(new URL(`/login?callbackUrl=${encodeURIComponent(path)}`, req.url));
  }

  // Protección extrema: Si intenta entrar a /admin y no es admin, lo mandamos al inicio
  if (path.startsWith("/admin") && token?.role !== "admin") {
    return NextResponse.redirect(new URL("/", req.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/profile", "/checkout", "/admin/:path*"],
};