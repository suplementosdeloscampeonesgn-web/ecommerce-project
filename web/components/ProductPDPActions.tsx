"use client";

import { useState } from "react";
import type { Product } from "@/app/generated/prisma/client";
import { getProductImageUrl } from "@/app/lib/productImage";
import { useCartStore } from "@/store/cartStore";

type ProductPDPActionsProps = {
  product: Pick<
    Product,
    "id" | "name" | "price" | "slug" | "image_url" | "images"
  >;
  maxQuantity?: number;
};

export function ProductPDPActions({
  product,
  maxQuantity,
}: ProductPDPActionsProps) {
  const addToCart = useCartStore((s) => s.addToCart);
  const [quantity, setQuantity] = useState(1);

  const cap =
    maxQuantity != null && maxQuantity > 0
      ? Math.min(maxQuantity, 999)
      : 999;
  const safeQty = Math.min(Math.max(1, quantity), cap);

  function setQty(next: number) {
    const v = Math.min(Math.max(1, next), cap);
    setQuantity(v);
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <p className="text-sm font-medium text-gray-500">Cantidad</p>
        <div className="mt-2 flex max-w-xs items-center gap-3">
          <button
            type="button"
            onClick={() => setQty(safeQty - 1)}
            disabled={safeQty <= 1}
            className="flex h-12 w-12 items-center justify-center rounded-xl border border-gray-200 text-lg font-semibold text-gray-800 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
            aria-label="Disminuir cantidad"
          >
            −
          </button>
          <span className="min-w-[3rem] text-center text-xl font-bold tabular-nums text-gray-900">
            {safeQty}
          </span>
          <button
            type="button"
            onClick={() => setQty(safeQty + 1)}
            disabled={safeQty >= cap}
            className="flex h-12 w-12 items-center justify-center rounded-xl border border-gray-200 text-lg font-semibold text-gray-800 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
            aria-label="Aumentar cantidad"
          >
            +
          </button>
        </div>
      </div>

      <button
        type="button"
        onClick={() =>
          addToCart({
            id: product.id,
            name: product.name,
            price: product.price,
            slug: product.slug,
            image: getProductImageUrl(product),
            quantity: safeQty,
          })
        }
        className="w-full rounded-2xl bg-black py-4 text-base font-bold text-white shadow-lg shadow-gray-900/10 transition hover:bg-gray-800"
      >
        Agregar al carrito
      </button>
    </div>
  );
}
