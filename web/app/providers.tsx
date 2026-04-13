"use client";

import { SessionProvider } from "next-auth/react";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider
      // 1. Sincronización Multi-Pestaña:
      // Si el usuario abre el catálogo en una pestaña, y en otra pestaña inicia sesión
      // o la cierra, NextAuth actualizará el estado aquí automáticamente al enfocar la ventana.
      refetchOnWindowFocus={true}
      
      // 2. Refresco Silencioso (Polling):
      // Verifica la validez de la sesión en segundo plano cada 5 minutos (300 segundos).
      // Esto previene que el usuario pierda su sesión a la mitad del Checkout 
      // si tu token JWT tiene un tiempo de expiración corto por seguridad.
      refetchInterval={300}
    >
      {/* Nota Arquitectónica: 
        Zustand (tu carrito) vive fuera del árbol de React, por lo que NO necesita 
        un Provider aquí. Esto hace que tu app sea mucho más rápida y ligera 
        que si usaras Redux o React Context tradicional.
      */}
      {children}
    </SessionProvider>
  );
}
