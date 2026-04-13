"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import useCartStore from "../../store/cartStore";
import { createOrder } from "../actions/orderActions";

export default function CheckoutPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const { items, clearCart } = useCartStore();
  
  const [shippingType, setShippingType] = useState("Uber");
  const [address, setAddress] = useState("");
  const [pickupTime, setPickupTime] = useState("12:00 PM");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login?callbackUrl=/checkout");
    }
  }, [status, router]);

  const total = items.reduce((acc, item) => acc + (item.price * item.quantity), 0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (items.length === 0) return;
    
    setLoading(true);
    try {
      const result = await createOrder({ shipping_type: shippingType, address, pickup_time: pickupTime }, items);
      if (result.success) {
        clearCart();
        router.push(`/checkout/success/${result.orderId}`);
      }
    } catch (error) {
      alert("Error al procesar el pedido. Intenta de nuevo.");
      setLoading(false);
    }
  };

  if (items.length === 0) return <div className="p-12 text-center text-xl font-bold">Tu carrito está vacío.</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-black mb-8">Finalizar Pedido</h1>
      
      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-12">
        {/* Columna Izquierda */}
        <div className="space-y-8">
          <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
            <h2 className="text-xl font-bold mb-4">Método de Entrega</h2>
            <div className="flex gap-4 mb-6">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="shipping" checked={shippingType === "Uber"} onChange={() => setShippingType("Uber")} className="w-5 h-5 accent-black" />
                <span>Uber (Solo SLP)</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="shipping" checked={shippingType === "Recoger"} onChange={() => setShippingType("Recoger")} className="w-5 h-5 accent-black" />
                <span>Recoger en Sucursal</span>
              </label>
            </div>

            {shippingType === "Uber" ? (
              <div>
                <label className="block text-sm font-semibold mb-2">Dirección de entrega</label>
                <input required type="text" value={address} onChange={(e) => setAddress(e.target.value)} placeholder="Calle, Número, Colonia..." className="w-full p-3 border rounded-xl" />
              </div>
            ) : (
              <div>
                <label className="block text-sm font-semibold mb-2">Horario de recogida</label>
                <select value={pickupTime} onChange={(e) => setPickupTime(e.target.value)} className="w-full p-3 border rounded-xl bg-white">
                  <option>10:00 AM</option>
                  <option>12:00 PM</option>
                  <option>04:00 PM</option>
                  <option>06:00 PM</option>
                </select>
                <p className="text-sm text-gray-500 mt-2">📍 Te esperamos en Suplementos De Los Campeones GN, SLP.</p>
              </div>
            )}
          </div>

          <div className="bg-gray-900 text-white p-6 rounded-2xl shadow-sm">
            <h2 className="text-xl font-bold mb-2">Pago por Transferencia</h2>
            <p className="text-sm text-gray-400 mb-4">Transfiere el total exacto a la siguiente cuenta:</p>
            <div className="bg-gray-800 p-4 rounded-xl font-mono text-center text-lg tracking-widest border border-gray-700">
              CLABE: 012 345 67890 123456 7
            </div>
            <p className="text-xs text-center mt-4 text-gray-400">Podrás enviar tu comprobante por WhatsApp en el siguiente paso.</p>
          </div>
        </div>

        {/* Columna Derecha */}
        <div className="bg-gray-50 p-6 rounded-2xl border border-gray-200 h-fit">
          <h2 className="text-xl font-bold mb-6">Resumen del Pedido</h2>
          <div className="space-y-4 mb-6">
            {items.map((item) => (
              <div key={item.id} className="flex justify-between items-center border-b pb-4">
                <div>
                  <p className="font-semibold">{item.name}</p>
                  <p className="text-sm text-gray-500">Cant: {item.quantity}</p>
                </div>
                <p className="font-bold">${(item.price * item.quantity).toFixed(2)}</p>
              </div>
            ))}
          </div>
          <div className="flex justify-between items-center text-xl font-black mb-8 pt-4 border-t-2 border-gray-900">
            <span>TOTAL</span>
            <span>${total.toFixed(2)} mxn</span>
          </div>
          <button type="submit" disabled={loading} className="w-full bg-black text-white py-4 rounded-xl font-bold hover:bg-gray-800 transition disabled:opacity-50">
            {loading ? "Procesando..." : "Confirmar Pedido"}
          </button>
        </div>
      </form>
    </div>
  );
}