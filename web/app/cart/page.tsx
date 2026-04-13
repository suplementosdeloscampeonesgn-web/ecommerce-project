"use client";

import Link from "next/link";
import { useCartStore } from "@/store/cartStore";
import { useEffect, useState } from "react";

export default function CartPage() {
  const items = useCartStore((s) => s.items);
  const updateQuantity = useCartStore((s) => s.updateQuantity);
  const removeFromCart = useCartStore((s) => s.removeFromCart);
  
  // Prevención de Hydration Mismatch en Next.js
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  if (!mounted) return null; // Previene el renderizado hasta que Zustand cargue el localStorage

  const subtotal = items.reduce((sum, i) => sum + i.price * i.quantity, 0);

  const formattedSubtotal = new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "MXN",
  }).format(subtotal);

  return (
    <div className="min-h-screen bg-white pb-32 selection:bg-green-500 selection:text-black pt-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* HEADER DEL CARRITO */}
        <div className="mb-12 border-b-2 border-black pb-6">
          <span className="text-green-600 font-black text-xs uppercase tracking-[0.2em] mb-2 block">
            Revisión de Búnker
          </span>
          <h1 className="text-4xl md:text-5xl font-black uppercase tracking-tighter text-black">
            Tu Carrito
          </h1>
        </div>

        {items.length === 0 ? (
          // ESTADO: CARRITO VACÍO
          <div className="py-24 text-center border-2 border-black bg-white flex flex-col items-center">
            <div className="text-6xl mb-6 grayscale">🛒</div>
            <h2 className="text-2xl font-black text-black uppercase tracking-tight mb-2">
              Tu carrito está vacío
            </h2>
            <p className="text-black font-medium mb-8 max-w-md">
              Aún no tienes suplementos seleccionados. Explora nuestro catálogo y potencia tu próximo entrenamiento.
            </p>
            <Link
              href="/catalog"
              className="inline-block bg-black text-white px-10 py-4 text-xs font-black uppercase tracking-widest hover:bg-green-500 hover:text-black transition-colors"
            >
              Ir al Catálogo
            </Link>
          </div>
        ) : (
          // ESTADO: CARRITO CON PRODUCTOS
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
            
            {/* COLUMNA IZQUIERDA: Lista de Artículos */}
            <div className="lg:col-span-7 space-y-6">
              <div className="hidden md:grid grid-cols-12 gap-4 pb-4 border-b-2 border-black text-xs font-black text-black uppercase tracking-widest">
                <div className="col-span-6">Producto</div>
                <div className="col-span-3 text-center">Cantidad</div>
                <div className="col-span-3 text-right">Subtotal</div>
              </div>

              <ul className="space-y-6">
                {items.map((item) => (
                  <li key={item.id} className="flex flex-col sm:flex-row items-start sm:items-center gap-6 pb-6 border-b border-gray-200 group">
                    
                    {/* Imagen */}
                    <Link href={`/product/${item.slug}`} className="relative h-24 w-24 sm:h-32 sm:w-32 flex-shrink-0 bg-white border border-gray-200 p-2 hover:border-black transition-colors">
                      <img
                        src={item.image || "https://placehold.co/600x600/eeeeee/999999?text=Sin+Imagen"}
                        alt={item.name}
                        className="h-full w-full object-contain mix-blend-multiply"
                      />
                    </Link>

                    {/* Info del Producto */}
                    <div className="flex-1 min-w-0 w-full flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      
                      {/* Título y Precio Unitario */}
                      <div className="sm:w-1/2">
                        <Link href={`/product/${item.slug}`} className="font-black text-sm text-black hover:text-green-600 transition-colors line-clamp-2 uppercase">
                          {item.name}
                        </Link>
                        <p className="mt-1 text-xs text-black font-bold">
                          {new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN" }).format(item.price)} c/u
                        </p>
                      </div>

                      {/* Controles de Cantidad */}
                      <div className="flex items-center gap-4 sm:w-1/4 justify-start sm:justify-center">
                        <div className="flex items-center border-2 border-black bg-white">
                          <button
                            type="button"
                            onClick={() => updateQuantity(item.id, item.quantity - 1)}
                            className="px-3 py-1 text-black font-black hover:bg-black hover:text-white transition-colors"
                            aria-label="Disminuir cantidad"
                          >
                            −
                          </button>
                          <span className="w-8 text-center text-xs font-black text-black">
                            {item.quantity}
                          </span>
                          <button
                            type="button"
                            onClick={() => updateQuantity(item.id, item.quantity + 1)}
                            className="px-3 py-1 text-black font-black hover:bg-black hover:text-white transition-colors"
                            aria-label="Aumentar cantidad"
                          >
                            +
                          </button>
                        </div>
                      </div>

                      {/* Subtotal por Item y Botón de Quitar */}
                      <div className="flex items-center justify-between sm:w-1/4 sm:flex-col sm:items-end gap-2">
                        <p className="font-black text-sm text-black">
                          {new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN" }).format(item.price * item.quantity)}
                        </p>
                        <button
                          type="button"
                          onClick={() => removeFromCart(item.id)}
                          className="text-[10px] font-black text-black hover:text-red-600 uppercase tracking-widest transition-colors"
                        >
                          Quitar
                        </button>
                      </div>

                    </div>
                  </li>
                ))}
              </ul>
            </div>

            {/* COLUMNA DERECHA: Resumen y Checkout (Alta Visibilidad) */}
            <div className="lg:col-span-5 lg:sticky lg:top-28">
              <div className="bg-white border-2 border-black p-8 shadow-xl">
                <h2 className="text-sm font-black uppercase tracking-widest text-black mb-6 border-b-2 border-black pb-4">
                  Resumen de Compra
                </h2>
                
                <div className="space-y-4 mb-6">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-black uppercase tracking-widest text-xs font-black">Subtotal</span>
                    <span className="font-black text-black">{formattedSubtotal}</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-black uppercase tracking-widest text-xs font-black">Envío</span>
                    <span className="font-black text-black text-[10px] uppercase text-right">Calculado en el siguiente paso</span>
                  </div>
                </div>

                <div className="border-t-4 border-black pt-6 mb-8 flex justify-between items-end">
                  <span className="text-lg font-black uppercase tracking-tight text-black">Total (MXN)</span>
                  <span className="text-3xl font-black text-black">{formattedSubtotal}</span>
                </div>

                {/* BOTÓN PARA IR AL CHECKOUT */}
                <Link
                  href="/checkout"
                  className="w-full flex justify-center items-center bg-black text-white py-4 text-sm font-black uppercase tracking-widest hover:bg-green-500 hover:text-black transition-colors duration-300 gap-2"
                >
                  Proceder al Checkout
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={3} stroke="currentColor" className="w-5 h-5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
                  </svg>
                </Link>
                
                <p className="text-center text-[10px] text-black font-black uppercase tracking-widest mt-4">
                  Pago seguro. Podrás elegir Uber o Recoger en Sucursal.
                </p>
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  );
}
