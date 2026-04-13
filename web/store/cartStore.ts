import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface CartItem {
  id: number;
  name: string;
  price: number;
  image: string;
  quantity: number;
  slug: string;
}

type CartItemInput = Omit<CartItem, "quantity"> & { quantity?: number };

interface CartState {
  items: CartItem[];
  addToCart: (item: CartItemInput) => void;
  removeFromCart: (id: number) => void;
  updateQuantity: (id: number, quantity: number) => void;
  clearCart: () => void;
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],
      addToCart: (item) => {
        const qty = item.quantity ?? 1;
        const { id, name, price, image, slug } = item;
        const existing = get().items.find((i) => i.id === id);
        if (existing) {
          set({
            items: get().items.map((i) =>
              i.id === id ? { ...i, quantity: i.quantity + qty } : i,
            ),
          });
        } else {
          set({
            items: [
              ...get().items,
              { id, name, price, image, slug, quantity: qty },
            ],
          });
        }
      },
      removeFromCart: (id) =>
        set({ items: get().items.filter((i) => i.id !== id) }),
      updateQuantity: (id, quantity) => {
        if (quantity <= 0) {
          get().removeFromCart(id);
          return;
        }
        set({
          items: get().items.map((i) =>
            i.id === id ? { ...i, quantity } : i,
          ),
        });
      },
      clearCart: () => set({ items: [] }),
    }),
    { name: "ecommerce-cart" },
  ),
);

export function selectCartItemCount(state: CartState): number {
  return state.items.reduce((acc, item) => acc + item.quantity, 0);
}
