export const PLACEHOLDER_IMG =
  "https://placehold.co/800x800/e5e7eb/9ca3af?text=Producto";

/** Mínimo necesario para resolver la URL de imagen (coincide con campos en Prisma `Product`). */
export type ProductImageSource = {
  image_url: string | null;
  images: string | null;
};

export function getProductImageUrl(product: ProductImageSource): string {
  if (product.image_url?.trim()) {
    return product.image_url.trim();
  }
  const raw = product.images?.trim();
  if (!raw) {
    return PLACEHOLDER_IMG;
  }
  try {
    const parsed: unknown = JSON.parse(raw);
    if (Array.isArray(parsed) && parsed.length > 0) {
      const first = parsed[0];
      if (typeof first === "string" && first.startsWith("http")) {
        return first;
      }
    }
  } catch {
    if (raw.startsWith("http")) {
      return raw;
    }
  }
  return PLACEHOLDER_IMG;
}
