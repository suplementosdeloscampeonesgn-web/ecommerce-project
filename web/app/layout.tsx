import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Navbar } from "@/components/Navbar";
import { Providers } from "./providers";
import { Toaster } from "react-hot-toast";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// Configuración de SEO y Metadata a nivel de producción
export const metadata: Metadata = {
  title: {
    template: "%s | Suplementos GN",
    default: "Suplementos GN | Rendimiento de Élite",
  },
  description: "La mejor nutrición deportiva y suplementos de alto rendimiento en San Luis Potosí. Fórmulas premium, envíos exprés y asesoría para tu entrenamiento.",
  keywords: ["suplementos", "proteínas", "creatina", "quemadores", "gimnasio", "San Luis Potosí", "nutrición deportiva"],
  openGraph: {
    title: "Suplementos GN | Rendimiento de Élite",
    description: "Fórmulas de alto rendimiento y la calidad que tu entrenamiento merece.",
    siteName: "Suplementos GN",
    locale: "es_MX",
    type: "website",
  },
  // Opcional: Agrega un manifest para PWA más adelante
  // manifest: "/manifest.json", 
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="es"
      // scroll-smooth mejora la experiencia al hacer clic en enlaces con anclas (ej. #ubicacion)
      className={`${geistSans.variable} ${geistMono.variable} scroll-smooth h-full`}
    >
      {/* selection:bg-green-500 le da el toque de marca cuando el usuario selecciona texto */}
      <body className="min-h-screen flex flex-col bg-white text-black antialiased selection:bg-green-500 selection:text-black">
        <Providers>
          
          {/* Configuración Global de Notificaciones (Toasts) */}
          <Toaster 
            position="bottom-right" 
            toastOptions={{
              duration: 3000,
              style: {
                background: '#000',
                color: '#fff',
                border: '1px solid #22c55e', // Borde verde GN
                borderRadius: '0px', // Cuadrado, para mantener el diseño minimalista
                fontSize: '12px',
                fontWeight: 'bold',
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
              },
              success: {
                iconTheme: {
                  primary: '#22c55e',
                  secondary: '#000',
                },
              },
              error: {
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#000',
                },
              },
            }} 
          />

          <Navbar />
          
          {/* flex-grow asegura que el contenido empuje el footer hacia abajo */}
          <main className="flex-grow flex flex-col">
            {children}
          </main>

          {/* Footer Minimalista de la Marca */}
          <footer className="bg-black text-white py-8 border-t-[3px] border-green-500">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
              <span className="text-[10px] font-bold uppercase tracking-widest text-gray-500">
                © {new Date().getFullYear()} Suplementos GN. Todos los derechos reservados.
              </span>
              <span className="text-[9px] font-black uppercase tracking-[0.2em] text-green-500">
                Alto Rendimiento
              </span>
            </div>
          </footer>

        </Providers>
      </body>
    </html>
  );
}
