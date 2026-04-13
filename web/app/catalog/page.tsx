import Link from "next/link";
import { getProducts } from "../actions/productActions";
import AddToCartButton from "../../components/AddToCartButton";

export const dynamic = "force-dynamic";

export default async function CatalogPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; category?: string; page?: string }>;
}) {
  // En Next.js 15 searchParams es una promesa
  const params = await searchParams;
  const currentQuery = params.q || "";
  const currentCategory = params.category || "";
  const currentPage = parseInt(params.page || "1");
  const ITEMS_PER_PAGE = 30;

  // Obtenemos todos los productos desde tu action
  const allProducts = await getProducts();

  // 1. Extracción Dinámica de Categorías (Directo de la DB)
  // Crea un array único con todas las categorías que existen actualmente en tus productos
  const dbCategories = Array.from(
    new Set(allProducts.map((p: any) => p.category).filter(Boolean))
  ).sort() as string[];

  // 2. Lógica de Filtrado (Buscador y Categoría)
  let filteredProducts = allProducts;

  if (currentQuery) {
    filteredProducts = filteredProducts.filter(
      (p: any) =>
        p.name.toLowerCase().includes(currentQuery.toLowerCase()) ||
        (p.brand && p.brand.toLowerCase().includes(currentQuery.toLowerCase()))
    );
  }

  if (currentCategory) {
    filteredProducts = filteredProducts.filter(
      (p: any) => p.category?.toLowerCase() === currentCategory.toLowerCase()
    );
  }

  // 3. Lógica de Paginación (Máximo 30 productos)
  const totalProducts = filteredProducts.length;
  const totalPages = Math.ceil(totalProducts / ITEMS_PER_PAGE);
  const paginatedProducts = filteredProducts.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  return (
    <div className="min-h-screen bg-white pb-32 selection:bg-green-500 selection:text-black">
      
      {/* HEADER DEL CATÁLOGO - Diseño Cinemático */}
      <div className="bg-black text-white pt-24 pb-16 px-4 mb-12 border-b-4 border-green-500">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-end justify-between gap-8">
          <div>
            <span className="text-green-500 font-bold text-xs uppercase tracking-[0.2em] mb-2 block">
              Explora Nuestro arsenal
            </span>
            <h1 className="text-5xl md:text-6xl font-black uppercase tracking-tighter">
              {currentCategory ? currentCategory : currentQuery ? `Búsqueda` : "Catálogo"}
            </h1>
          </div>
          <div className="text-left md:text-right">
            <p className="text-gray-400 text-sm tracking-widest uppercase font-light">
              Mostrando {paginatedProducts.length} de {totalProducts} suplementos
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* BARRA DE HERRAMIENTAS (Buscador y Filtros) */}
        <div className="flex flex-col lg:flex-row gap-8 mb-16">
          
          {/* Buscador de Precisión */}
          <form action="/catalog" className="w-full lg:w-1/3 flex group">
            <input
              type="text"
              name="q"
              defaultValue={currentQuery}
              placeholder="Buscar por nombre o marca..."
              className="flex-grow bg-gray-50 border border-gray-200 text-sm py-4 px-6 focus:outline-none focus:border-black focus:bg-white transition-all rounded-none"
            />
            <button
              type="submit"
              className="bg-black text-white px-8 uppercase text-xs font-bold tracking-widest hover:bg-green-500 hover:text-black transition-colors"
            >
              Buscar
            </button>
          </form>

          {/* Filtros de Categorías Dinámicos */}
          <div className="w-full lg:w-2/3 flex flex-wrap gap-2 items-center">
            <Link
              href="/catalog"
              className={`px-6 py-3 text-xs font-bold uppercase tracking-widest transition-colors border ${
                !currentCategory && !currentQuery
                  ? "bg-black text-white border-black"
                  : "bg-transparent text-gray-500 border-gray-200 hover:border-black hover:text-black"
              }`}
            >
              Todos
            </Link>
            {dbCategories.map((cat) => (
              <Link
                key={cat}
                href={`/catalog?category=${cat}`}
                className={`px-6 py-3 text-xs font-bold uppercase tracking-widest transition-colors border ${
                  currentCategory === cat
                    ? "bg-black text-white border-black"
                    : "bg-transparent text-gray-500 border-gray-200 hover:border-black hover:text-black"
                }`}
              >
                {cat}
              </Link>
            ))}
          </div>
        </div>

        {/* GRID DE RESULTADOS */}
        {paginatedProducts.length === 0 ? (
          <div className="py-32 text-center border border-gray-100 bg-gray-50">
            <div className="text-5xl mb-6 grayscale opacity-50">🔍</div>
            <h2 className="text-2xl font-black text-gray-900 uppercase tracking-tight mb-2">
              Sin Resultados
            </h2>
            <p className="text-gray-500 text-sm mb-8 font-light">
              No se encontraron suplementos para tu búsqueda actual.
            </p>
            <Link
              href="/catalog"
              className="inline-block bg-black text-white px-10 py-4 text-xs font-bold uppercase tracking-widest hover:bg-green-500 hover:text-black transition-colors"
            >
              Restablecer Filtros
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {paginatedProducts.map((product: any) => (
              <div
                key={product.id}
                className="flex flex-col h-full bg-white group border border-gray-200 hover:border-black transition-colors duration-300"
              >
                <Link
                  href={`/product/${product.slug}`}
                  className="relative block aspect-[4/5] bg-gray-50 overflow-hidden"
                >
                  {product.brand && (
                    <span className="absolute top-4 left-4 z-10 bg-black text-white text-[9px] font-bold px-3 py-1.5 uppercase tracking-[0.2em]">
                      {product.brand}
                    </span>
                  )}
                  <img
                    src={
                      product.image_url ||
                      product.images ||
                      "https://placehold.co/600x800/eeeeee/999999?text=Sin+Imagen"
                    }
                    alt={product.name}
                    className="w-full h-full object-contain p-8 mix-blend-multiply group-hover:scale-110 transition-transform duration-700 ease-out"
                  />
                </Link>

                <div className="p-6 flex flex-col flex-grow">
                  <p className="text-[10px] text-gray-400 font-bold uppercase tracking-[0.2em] mb-2">
                    {product.category}
                  </p>
                  <Link href={`/product/${product.slug}`}>
                    <h3 className="font-bold text-gray-900 leading-snug mb-4 line-clamp-2 hover:text-green-600 transition-colors">
                      {product.name}
                    </h3>
                  </Link>
                  <div className="mt-auto flex items-end gap-3 mb-6">
                    <p className="text-2xl font-black text-gray-900">
                      ${Number(product.price).toFixed(2)}
                    </p>
                    {product.compare_price && product.compare_price > product.price && (
                      <p className="text-xs text-gray-400 line-through mb-1.5">
                        ${Number(product.compare_price).toFixed(2)}
                      </p>
                    )}
                  </div>
                  <AddToCartButton product={product} />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* CONTROLES DE PAGINACIÓN */}
        {totalPages > 1 && (
          <div className="mt-20 pt-10 border-t border-gray-200 flex justify-center items-center gap-6">
            {currentPage > 1 ? (
              <Link
                href={`/catalog?page=${currentPage - 1}${currentQuery ? `&q=${currentQuery}` : ""}${currentCategory ? `&category=${currentCategory}` : ""}`}
                className="px-6 py-3 border border-black text-xs font-bold uppercase tracking-widest hover:bg-black hover:text-white transition-colors"
              >
                ← Anterior
              </Link>
            ) : (
              <span className="px-6 py-3 border border-gray-200 text-gray-300 text-xs font-bold uppercase tracking-widest cursor-not-allowed">
                ← Anterior
              </span>
            )}

            <span className="text-xs font-bold text-gray-900 uppercase tracking-widest">
              Página {currentPage} de {totalPages}
            </span>

            {currentPage < totalPages ? (
              <Link
                href={`/catalog?page=${currentPage + 1}${currentQuery ? `&q=${currentQuery}` : ""}${currentCategory ? `&category=${currentCategory}` : ""}`}
                className="px-6 py-3 border border-black text-xs font-bold uppercase tracking-widest hover:bg-black hover:text-white transition-colors"
              >
                Siguiente →
              </Link>
            ) : (
              <span className="px-6 py-3 border border-gray-200 text-gray-300 text-xs font-bold uppercase tracking-widest cursor-not-allowed">
                Siguiente →
              </span>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
