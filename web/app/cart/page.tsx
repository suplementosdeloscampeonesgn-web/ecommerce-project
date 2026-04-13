"use client";

import Link from "next/link";
import { useCartStore } from "@/store/cartStore";

export default function CartPage() {
  const items = useCartStore((s) => s.items);
  const updateQuantity = useCartStore((s) => s.updateQuantity);
  const removeFromCart = useCartStore((s) => s.removeFromCart);

  const subtotal = items.reduce(
    (sum, i) => sum + i.price * i.quantity,
    0,
  );

  const formatted = new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "MXN",
  }).format(subtotal);

  return (
    <div className="min-h-screen bg-stone-50 px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-3xl">
        <h1 className="text-3xl font-extrabold tracking-tight text-gray-900">
          Tu carrito
        </h1>
        <p className="mt-2 text-gray-600">
          Revisa los artículos antes de continuar al pago.
        </p>

        {items.length === 0 ? (
          <div className="mt-10 rounded-2xl border border-gray-100 bg-white p-10 text-center shadow-sm">
            <p className="text-gray-600">Tu carrito está vacío.</p>
            <Link
              href="/"
              className="mt-6 inline-block rounded-xl bg-black px-6 py-3 text-sm font-semibold text-white hover:bg-gray-800"
            >
              Ver catálogo
            </Link>
          </div>
        ) : (
          <ul className="mt-8 space-y-4">
            {items.map((item) => (
              <li
                key={item.id}
                className="flex gap-4 rounded-2xl border border-gray-100 bg-white p-4 shadow-sm"
              >
                <Link
                  href={`/product/${item.slug}`}
                  className="relative h-24 w-24 flex-shrink-0 overflow-hidden rounded-xl bg-gray-100"
                >
                  {/* eslint-disable-next-line @next/next/no-img-element -- external / placeholder URLs */}
                  <img
                    src={item.image}
                    alt=""
                    className="h-full w-full object-cover"
                  />
                </Link>
                <div className="min-w-0 flex-1">
                  <Link
                    href={`/product/${item.slug}`}
                    className="font-semibold text-gray-900 hover:underline"
                  >
                    {item.name}
                  </Link>
                  <p className="mt-1 text-sm text-gray-500">
                    {new Intl.NumberFormat("es-MX", {
                      style: "currency",
                      currency: "MXN",
                    }).format(item.price)}{" "}
                    c/u
                  </p>
                  <div className="mt-3 flex flex-wrap items-center gap-3">
                    <div className="flex items-center gap-2 rounded-lg border border-gray-200">
                      <button
                        type="button"
                        onClick={() =>
                          updateQuantity(item.id, item.quantity - 1)
                        }
                        className="px-3 py-1 text-lg font-medium text-gray-700 hover:bg-gray-50"
                        aria-label="Menos"
                      >
                        −
                      </button>
                      <span className="min-w-[2rem] text-center text-sm font-semibold">
                        {item.quantity}
                      </span>
                      <button
                        type="button"
                        onClick={() =>
                          updateQuantity(item.id, item.quantity + 1)
                        }
                        className="px-3 py-1 text-lg font-medium text-gray-700 hover:bg-gray-50"
                        aria-label="Más"
                      >
                        +
                      </button>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeFromCart(item.id)}
                      className="text-sm font-medium text-red-600 hover:underline"
                    >
                      Quitar
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}

        {items.length > 0 ? (
          <div className="mt-8 flex items-center justify-between rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
            <span className="text-lg font-semibold text-gray-700">
              Subtotal
            </span>
            <span className="text-2xl font-extrabold text-gray-900">
              {formatted}
            </span>
          </div>
        ) : null}
      </div>
    </div>
  );
}
