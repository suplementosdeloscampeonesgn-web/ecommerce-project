"use client";

import Link from "next/link";
import { useSession } from "next-auth/react";
import { useEffect, useState } from "react";
import { selectCartItemCount, useCartStore } from "@/store/cartStore";

export function Navbar() {
  const { data: session, status } = useSession();
  const [mounted, setMounted] = useState(false);
  const totalItems = useCartStore(selectCartItemCount);

  useEffect(() => {
    setMounted(true);
  }, []);

  const badgeCount = mounted ? totalItems : 0;

  return (
    <header className="sticky top-0 z-50 border-b border-gray-100/80 bg-white/85 backdrop-blur-md shadow-sm">
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-4 px-4 sm:px-6 lg:px-8">
        <div className="flex min-w-0 flex-1 items-center">
          <Link
            href="/"
            className="text-lg font-extrabold tracking-tight text-gray-900 transition hover:text-gray-700"
          >
            Suplementos
          </Link>
        </div>

        <div className="hidden min-w-0 flex-[1.5] sm:block">
          <label htmlFor="nav-search" className="sr-only">
            Buscar productos
          </label>
          <input
            id="nav-search"
            type="search"
            placeholder="Buscar suplementos…"
            readOnly
            className="w-full rounded-full border border-gray-200 bg-gray-50/80 px-4 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 outline-none ring-gray-900/10 transition focus:border-gray-300 focus:bg-white focus:ring-2"
          />
        </div>

        <div className="flex flex-shrink-0 items-center justify-end gap-2 sm:gap-3">
          <Link
            href="/cart"
            className="relative flex h-10 w-10 items-center justify-center rounded-xl text-gray-800 transition hover:bg-gray-100"
            aria-label="Ver carrito"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="22"
              height="22"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden
            >
              <circle cx="9" cy="21" r="1" />
              <circle cx="20" cy="21" r="1" />
              <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
            </svg>
            {badgeCount > 0 ? (
              <span className="absolute -right-0.5 -top-0.5 flex h-5 min-w-5 items-center justify-center rounded-full bg-red-600 px-1 text-[11px] font-bold text-white">
                {badgeCount > 99 ? "99+" : badgeCount}
              </span>
            ) : null}
          </Link>

          {status === "loading" ? (
            <div className="h-10 w-10 animate-pulse rounded-xl bg-gray-100" />
          ) : session?.user ? (
            <Link
              href="/profile"
              className="flex h-10 w-10 items-center justify-center rounded-xl text-gray-800 transition hover:bg-gray-100"
              aria-label="Mi perfil"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="22"
                height="22"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden
              >
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
            </Link>
          ) : (
            <Link
              href="/login"
              className="rounded-xl bg-black px-4 py-2 text-sm font-semibold text-white transition hover:bg-gray-800"
            >
              Entrar
            </Link>
          )}
        </div>
      </div>

      <div className="border-t border-gray-50 px-4 pb-3 sm:hidden">
        <input
          type="search"
          placeholder="Buscar…"
          readOnly
          className="w-full rounded-full border border-gray-200 bg-gray-50/80 px-4 py-2 text-sm outline-none"
        />
      </div>
    </header>
  );
}
