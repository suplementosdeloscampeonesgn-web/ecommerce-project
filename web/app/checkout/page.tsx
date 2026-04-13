"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { useCartStore } from "../../store/cartStore";
import { createOrder } from "../actions/orderActions";
import toast from "react-hot-toast";
import Link from "next/link";

export default function CheckoutPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const { items, clearCart } = useCartStore();
  const [shippingType, setShippingType] = useState("Uber");
  const [address, setAddress] = useState("");
  const [pickupTime, setPickupTime] = useState("12:00 PM");
  const [loading, setLoading] = useState(false);
  const [mounted, setMounted] = useState(false);

  // Evitar errores de hidratación con Zustand
  useEffect(() => setMounted(true), []);

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login?callbackUrl=/checkout");
    }
  }, [status, router]);

  const total = items.reduce((acc, item) => acc + item.price * item.quantity, 0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (items.length === 0) return;
    
    setLoading(true);
    // Notificación de inicio de proceso
    const loadingToast = toast.loading("Encriptando y procesando pedido...");

    try {
      const result = await createOrder(
        { shipping_type: shippingType, address, pickup_time: pickupTime },
        items
      );

      if (result.success) {
        clearCart();
        toast.success("¡Pedido confirmado con éxito!", { id: loadingToast });
        router.push(`/checkout/success/${result.orderId}`);
      } else {
        toast.error("Hubo un problema con la base de datos.", { id: loadingToast });
        setLoading(false);
      }
    } catch (error) {
      toast.error("Error al procesar el pedido. Intenta de nuevo.", { id: loadingToast });
      setLoading(false);
    }
  };

  // Prevenir renderizado erróneo en SSR
  if (!mounted) return null;

  // ESTADO DE CARRITO VACÍO (Estética Premium)
  if (items.length === 0) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center bg-gray-50 px-4">
        <div className="text-6xl mb-6 grayscale opacity-30">🛒</div>
        <h1 className="text-3xl font-black uppercase tracking-tight text-gray-900 mb-2">Tu Búnker está vacío</h1>
        <p className="text-gray-500 mb-8 font-light text-center max-w-md">
          Aún no tienes suplementos listos para ordenar. Explora nuestro catálogo y prepárate para tu próximo entrenamiento.
        </p>
        <Link 
          href="/catalog" 
          className="bg-black text-white px-10 py-4 text-xs font-bold uppercase tracking-widest hover:bg-green-500 hover:text-black transition-colors duration-300"
        >
          Volver a la Tienda
        </Link>
      </div>
    );
  }

  // ESTADO DE CHECKOUT ACTIVO
  return (
    <div className="min-h-screen bg-white pb-32 selection:bg-green-500 selection:text-black pt-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* HEADER */}
        <div className="mb-12 border-b border-gray-200 pb-6">
          <span className="text-green-500 font-bold text-xs uppercase tracking-[0.2em] mb-2 block">
            Paso Final
          </span>
          <h1 className="text-4xl md:text-5xl font-black uppercase tracking-tighter text-gray-900">
            Confirmar Pedido
          </h1>
        </div>

        <form onSubmit={handleSubmit} className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-start">
          
          {/* COLUMNA IZQUIERDA: Formulario de Datos (Ocupa 7 columnas en desktop) */}
          <div className="lg:col-span-7 space-y-8">
            
            {/* SECCIÓN DE ENVÍO */}
            <div className="bg-white border border-gray-200 p-8">
              <h2 className="text-sm font-bold uppercase tracking-widest text-gray-900 mb-6 border-b border-gray-100 pb-4">
                Método de Entrega
              </h2>
              
              <div className="flex flex-col sm:flex-row gap-4 mb-8">
                <label className={`flex-1 border p-4 cursor-pointer transition-colors flex items-center gap-3 ${shippingType === "Uber" ? 'border-black bg-gray-50' : 'border-gray-200 hover:border-gray-300'}`}>
                  <input 
                    type="radio" 
                    name="shipping" 
                    checked={shippingType === "Uber"} 
                    onChange={() => setShippingType("Uber")} 
                    className="w-4 h-4 text-black focus:ring-black accent-black" 
                  />
                  <span className="text-sm font-bold uppercase tracking-wide">Uber (Solo SLP)</span>
                </label>
                
                <label className={`flex-1 border p-4 cursor-pointer transition-colors flex items-center gap-3 ${shippingType === "Recoger" ? 'border-black bg-gray-50' : 'border-gray-200 hover:border-gray-300'}`}>
                  <input 
                    type="radio" 
                    name="shipping" 
                    checked={shippingType === "Recoger"} 
                    onChange={() => setShippingType("Recoger")} 
                    className="w-4 h-4 text-black focus:ring-black accent-black" 
                  />
                  <span className="text-sm font-bold uppercase tracking-wide">Recoger en Sucursal</span>
                </label>
              </div>

              {shippingType === "Uber" ? (
                <div className="animate-in fade-in slide-in-from-top-2 duration-300">
                  <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">
                    Dirección Completa de Entrega
                  </label>
                  <input 
                    required 
                    type="text" 
                    value={address} 
                    onChange={(e) => setAddress(e.target.value)} 
                    placeholder="Calle, Número, Colonia, Referencias..." 
                    className="w-full bg-gray-50 border border-gray-200 text-sm py-3 px-4 focus:outline-none focus:border-black focus:bg-white transition-all rounded-none" 
                  />
                </div>
              ) : (
                <div className="animate-in fade-in slide-in-from-top-2 duration-300">
                  <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">
                    Horario de Recogida
                  </label>
                  <select 
                    value={pickupTime} 
                    onChange={(e) => setPickupTime(e.target.value)} 
                    className="w-full bg-gray-50 border border-gray-200 text-sm py-3 px-4 focus:outline-none focus:border-black focus:bg-white transition-all rounded-none appearance-none cursor-pointer"
                  >
                    <option>10:00 AM</option>
                    <option>12:00 PM</option>
                    <option>04:00 PM</option>
                    <option>06:00 PM</option>
                  </select>
                  <div className="mt-4 bg-gray-50 p-4 border-l-4 border-black">
                    <p className="text-xs text-gray-600 uppercase tracking-wide font-semibold">📍 Punto de Entrega</p>
                    <p className="text-sm text-gray-900 mt-1">Av Vicente Rivera 131 A, Colonia Nuevo Paseo, SLP.</p>
                  </div>
                </div>
              )}
            </div>

            {/* SECCIÓN DE PAGO (Diseño de Alta Seguridad) */}
            <div className="bg-black text-white p-8 border-t-4 border-green-500">
              <h2 className="text-sm font-bold uppercase tracking-widest mb-2 flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5 text-green-500">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" />
                </svg>
                Transferencia Bancaria
              </h2>
              <p className="text-xs text-gray-400 mb-6 font-light">Transfiere el total exacto a la siguiente cuenta. Validaremos tu pago vía WhatsApp.</p>
              
              <div className="bg-[#111] p-5 border border-gray-800 text-center relative group">
                <span className="absolute -top-2.5 left-1/2 -translate-x-1/2 bg-black text-gray-500 text-[10px] uppercase tracking-widest px-2 font-bold">CLABE Interbancaria</span>
                <p className="font-mono text-xl md:text-2xl tracking-[0.15em] text-green-400 group-hover:text-green-300 transition-colors">
                  012 345 67890 123456 7
                </p>
              </div>
            </div>
          </div>

          {/* COLUMNA DERECHA: Resumen de Compra (Ocupa 5 columnas en desktop, se vuelve sticky) */}
          <div className="lg:col-span-5 lg:sticky lg:top-28">
            <div className="bg-gray-50 border border-gray-200 p-8">
              <h2 className="text-sm font-bold uppercase tracking-widest text-gray-900 mb-6 border-b border-gray-200 pb-4">
                Resumen del Pedido
              </h2>
              
              <div className="space-y-4 mb-8 max-h-[40vh] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-gray-300">
                {items.map((item) => (
                  <div key={item.id} className="flex justify-between items-start gap-4">
                    <div className="flex-1">
                      <p className="font-bold text-sm text-gray-900 leading-tight mb-1">{item.name}</p>
                      <p className="text-[10px] text-gray-500 uppercase tracking-wider font-bold">Cant: {item.quantity}</p>
                    </div>
                    <p className="font-black text-sm text-gray-900 whitespace-nowrap">
                      ${(item.price * item.quantity).toFixed(2)}
                    </p>
                  </div>
                ))}
              </div>
              
              <div className="border-t-2 border-black pt-6 mb-8">
                <div className="flex justify-between items-end mb-2">
                  <span className="text-xs font-bold text-gray-500 uppercase tracking-widest">Subtotal</span>
                  <span className="font-bold text-gray-900">${total.toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-end mb-6">
                  <span className="text-xs font-bold text-gray-500 uppercase tracking-widest">Envío</span>
                  <span className="font-bold text-gray-900">{shippingType === "Uber" ? "Calculado en WhatsApp" : "Gratis"}</span>
                </div>
                
                <div className="flex justify-between items-end">
                  <span className="text-lg font-black uppercase tracking-tight">Total (MXN)</span>
                  <span className="text-3xl font-black text-green-600">${total.toFixed(2)}</span>
                </div>
              </div>

              <button 
                type="submit" 
                disabled={loading} 
                className="w-full bg-black text-white py-4 text-sm font-bold uppercase tracking-widest hover:bg-green-500 hover:text-black transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Procesando...
                  </>
                ) : (
                  "Confirmar Pedido"
                )}
              </button>
            </div>
          </div>

        </form>
      </div>
    </div>
  );
}
