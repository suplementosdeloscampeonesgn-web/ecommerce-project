"use client";

// CORRECCIÓN: Se agregaron las llaves { } para coincidir con tu export const en cartStore.ts
import { useCartStore } from "../store/cartStore";

export default function AddToCartButton({ product }: { product: any }) {
  const addToCart = useCartStore((state) => state.addToCart);

  const handleAdd = (e: React.MouseEvent) => {
    e.preventDefault(); // Evita que al dar clic te redirija a la página del producto
    
    addToCart({
      id: product.id,
      name: product.name,
      price: product.price,
      image: product.image_url || product.images || "https://placehold.co/600x600/eeeeee/999999?text=Sin+Imagen",
      quantity: 1,
      slug: product.slug,
    });
    
    alert(`¡${product.name} agregado al carrito!`);
  };

  return (
    <button
      onClick={handleAdd}
      className="w-full bg-black text-white py-3 rounded-xl font-bold hover:bg-gray-800 transition-all mt-4 shadow-md hover:shadow-lg active:scale-95"
    >
      Agregar al carrito
    </button>
  );
}