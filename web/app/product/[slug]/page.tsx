import { getProductImageUrl } from "@/app/lib/productImage";
import { prisma } from "@/app/lib/prisma";
import { ProductPDPActions } from "@/components/ProductPDPActions";
import { notFound } from "next/navigation";

function formatMxn(value: number): string {
  return new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "MXN",
  }).format(value);
}

type PageProps = {
  params: Promise<{ slug: string }>;
};

export default async function ProductPage({ params }: PageProps) {
  const { slug } = await params;

  const product = await prisma.product.findUnique({
    where: { slug },
  });

  if (!product || product.is_active === false) {
    notFound();
  }

  const imageUrl = getProductImageUrl(product);
  const maxQty =
    product.stock != null && product.stock > 0 ? product.stock : undefined;

  return (
    <div className="min-h-screen bg-gradient-to-b from-stone-50 to-white">
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8 lg:py-14">
        <div className="grid gap-10 lg:grid-cols-2 lg:gap-16 lg:items-start">
          <div className="overflow-hidden rounded-3xl border border-gray-100 bg-white shadow-sm">
            <div className="aspect-square w-full bg-gray-50">
              <img
                src={imageUrl}
                alt={product.name}
                className="h-full w-full object-cover"
              />
            </div>
          </div>

          <div className="flex flex-col">
            {product.category ? (
              <p className="text-sm font-semibold uppercase tracking-wide text-gray-500">
                {product.category}
              </p>
            ) : null}
            <h1 className="mt-2 text-3xl font-extrabold tracking-tight text-gray-900 sm:text-4xl lg:text-5xl">
              {product.name}
            </h1>

            {product.brand ? (
              <p className="mt-3 text-sm font-medium text-gray-600">
                Marca: <span className="text-gray-900">{product.brand}</span>
              </p>
            ) : null}

            <div className="mt-8 flex flex-wrap items-baseline gap-3">
              {product.compare_price != null &&
              product.compare_price > product.price ? (
                <span className="text-lg text-gray-400 line-through">
                  {formatMxn(product.compare_price)}
                </span>
              ) : null}
              <span className="text-4xl font-extrabold text-gray-900">
                {formatMxn(product.price)}
              </span>
            </div>

            {product.stock != null ? (
              <p className="mt-4 text-sm text-gray-600">
                {product.stock > 0 ? (
                  <>
                    <span className="font-medium text-emerald-700">
                      En stock
                    </span>
                    <span className="text-gray-500">
                      {" "}
                      ({product.stock} disponibles)
                    </span>
                  </>
                ) : (
                  <span className="font-medium text-red-600">
                    Agotado temporalmente
                  </span>
                )}
              </p>
            ) : null}

            <div className="mt-10 border-t border-gray-100 pt-10">
              <h2 className="text-sm font-bold uppercase tracking-wide text-gray-900">
                Descripción
              </h2>
              <div className="prose prose-gray mt-3 max-w-none text-base leading-relaxed text-gray-600">
                {product.description?.trim() ? (
                  <p className="whitespace-pre-wrap">{product.description}</p>
                ) : (
                  <p className="text-gray-500">
                    Sin descripción detallada para este producto.
                  </p>
                )}
              </div>
            </div>

            <div className="mt-10">
              {product.stock != null && product.stock <= 0 ? (
                <p className="rounded-2xl border border-amber-100 bg-amber-50 px-4 py-3 text-sm text-amber-900">
                  Este producto no se puede añadir al carrito en este momento.
                </p>
              ) : (
                <ProductPDPActions product={product} maxQuantity={maxQty} />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
