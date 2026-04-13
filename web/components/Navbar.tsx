"use client";

import Link from "next/link";
import { useSession } from "next-auth/react";
import { useCartStore } from "../store/cartStore";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export function Navbar() {
  const { data: session, status } = useSession();
  const items = useCartStore((state) => state.items);
  const [mounted, setMounted] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const router = useRouter();

  // Prevenir errores de hidratación en Next.js con Zustand persist
  useEffect(() => setMounted(true), []);

  const cartCount = items.reduce((acc, item) => acc + item.quantity, 0);

  // Manejador de búsqueda sin recargar la página (SPA feel)
  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const searchQuery = formData.get("q");
    if (searchQuery) {
      router.push(`/catalog?q=${searchQuery}`);
      setIsMobileMenuOpen(false); // Cierra el menú al buscar
    }
  };

  return (
    <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur-xl border-b border-gray-200 shadow-sm transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20 gap-4 md:gap-8">
          
          {/* LOGO - Contraste corregido */}
          <Link href="/" className="font-black text-2xl tracking-tighter uppercase flex-shrink-0 group flex items-center">
            <span className="text-black group-hover:text-gray-700 transition-colors">Suplementos</span>
            <span className="text-green-500 group-hover:text-green-600 transition-colors">GN</span>
          </Link>

          {/* ENLACES DE NAVEGACIÓN (Desktop) */}
          <div className="hidden lg:flex items-center gap-6 xl:gap-8">
            <Link href="/catalog" className="text-[11px] font-black uppercase tracking-[0.2em] text-gray-500 hover:text-green-600 transition-colors">
              Tienda
            </Link>
            <Link href="/asesorias" className="text-[11px] font-black uppercase tracking-[0.2em] text-gray-500 hover:text-green-600 transition-colors">
              Asesorías
            </Link>
            <Link href="/#servicios" className="text-[11px] font-black uppercase tracking-[0.2em] text-gray-500 hover:text-green-600 transition-colors">
              Servicios
            </Link>
            <Link href="/#ubicacion" className="text-[11px] font-black uppercase tracking-[0.2em] text-gray-500 hover:text-green-600 transition-colors">
              Ubicación
            </Link>
          </div>

          {/* BUSCADOR (Desktop) */}
          <div className="hidden md:block flex-grow max-w-sm xl:max-w-md">
            <form onSubmit={handleSearch} className="relative group">
              <input 
                type="text" 
                name="q" 
                placeholder="Buscar proteínas, creatina..." 
                className="w-full bg-gray-100 border border-transparent rounded-full py-2.5 pl-6 pr-12 text-sm text-black placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-black focus:bg-white transition-all duration-300"
              />
              <button type="submit" className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-black transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                  <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
                </svg>
              </button>
            </form>
          </div>

          {/* ACCIONES (Perfil y Carrito) */}
          <div className="flex items-center gap-4 sm:gap-6 flex-shrink-0">
            
            {/* AUTENTICACIÓN */}
            <div className="hidden sm:flex items-center gap-4">
              {status === "loading" ? (
                <div className="w-32 h-8 bg-gray-100 rounded animate-pulse"></div>
              ) : session ? (
                <Link 
                  href={session.user?.role === "admin" ? "/admin" : "/profile"} 
                  className="flex items-center gap-2 text-xs font-bold text-gray-900 hover:text-green-600 transition-colors uppercase tracking-widest border border-gray-200 px-4 py-2 rounded-full hover:border-green-600"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
                  </svg>
                  {session.user?.role === "admin" ? "Búnker" : "Perfil"}
                </Link>
              ) : (
                <>
                  <Link href="/login" className="text-[11px] font-black text-gray-500 hover:text-black transition-colors uppercase tracking-[0.1em]">
                    Iniciar Sesión
                  </Link>
                  <Link href="/register" className="text-[11px] font-black bg-black text-white px-5 py-2.5 rounded-none hover:bg-green-500 hover:text-black transition-colors uppercase tracking-[0.1em]">
                    Crear Cuenta
                  </Link>
                </>
              )}
            </div>

            {/* SEPARADOR */}
            <div className="w-px h-6 bg-gray-200 hidden sm:block"></div>

            {/* CARRITO */}
            <Link 
              href="/cart" 
              className="relative flex items-center text-black hover:text-green-500 transition-colors p-1"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 10.5V6a3.75 3.75 0 1 0-7.5 0v4.5m11.356-1.993 1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 0 1-1.12-1.243l1.264-12A1.125 1.125 0 0 1 5.513 7.5h12.974c.576 0 1.059.435 1.119 1.007ZM8.625 10.5a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm7.5 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
              </svg>
              
              {mounted && cartCount > 0 && (
                <span className="absolute -top-1.5 -right-2 bg-green-500 text-black text-[10px] font-black w-5 h-5 flex items-center justify-center rounded-full border-2 border-white shadow-sm">
                  {cartCount > 99 ? '99+' : cartCount}
                </span>
              )}
            </Link>

            {/* BOTÓN MENÚ HAMBURGUESA (Solo Mobile) */}
            <button 
              className="lg:hidden text-black p-1"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
              </svg>
            </button>
            
          </div>
        </div>
      </div>

      {/* MENÚ DESPLEGABLE MOBILE */}
      {isMobileMenuOpen && (
        <div className="lg:hidden bg-white border-t border-gray-100 p-4 shadow-lg absolute w-full">
          <form onSubmit={handleSearch} className="relative mb-4">
            <input 
              type="text" 
              name="q" 
              placeholder="Buscar..." 
              className="w-full bg-gray-100 rounded-md py-2.5 px-4 text-sm focus:outline-none focus:ring-2 focus:ring-black"
            />
          </form>
          <div className="flex flex-col gap-4">
            <Link href="/catalog" onClick={() => setIsMobileMenuOpen(false)} className="text-sm font-bold uppercase tracking-widest text-gray-800">Tienda</Link>
            <Link href="/asesorias" onClick={() => setIsMobileMenuOpen(false)} className="text-sm font-bold uppercase tracking-widest text-gray-800">Asesorías</Link>
            <Link href="/#servicios" onClick={() => setIsMobileMenuOpen(false)} className="text-sm font-bold uppercase tracking-widest text-gray-800">Servicios</Link>
            <Link href="/#ubicacion" onClick={() => setIsMobileMenuOpen(false)} className="text-sm font-bold uppercase tracking-widest text-gray-800">Ubicación</Link>
            
            <div className="border-t border-gray-200 mt-2 pt-4 flex flex-col gap-3">
              {!session ? (
                <>
                  <Link href="/login" onClick={() => setIsMobileMenuOpen(false)} className="text-sm font-bold uppercase tracking-widest text-gray-500">Iniciar Sesión</Link>
                  <Link href="/register" onClick={() => setIsMobileMenuOpen(false)} className="text-sm font-bold uppercase tracking-widest bg-black text-white text-center py-3">Crear Cuenta</Link>
                </>
              ) : (
                <Link href={session.user?.role === "admin" ? "/admin" : "/profile"} onClick={() => setIsMobileMenuOpen(false)} className="text-sm font-bold uppercase tracking-widest text-green-600">
                  Mi Perfil
                </Link>
              )}
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
