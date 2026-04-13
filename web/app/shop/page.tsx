import Link from "next/link";
import { getProducts } from "../actions/productActions";
import AddToCartButton from "../../components/AddToCartButton";

export const dynamic = "force-dynamic";

export default async function CatalogPage({
  searchParams,
}: {
  searchParams: { q?: string; category?: string };
}) {
  let products = await getProducts();

  // 1. Lógica del Buscador
  if (searchParams.q) {
    products = products.filter((p) =>
      p.name.toLowerCase().includes(searchParams.q!.toLowerCase())
    );
  }

  // 2. Lógica de Filtro por Categorías
  if (searchParams.category) {
    products = products.filter(
      (p) => p.category?.toLowerCase() === searchParams.category?.toLowerCase()
    );
  }

  const categories = ['Quemadores', 'Aminoácidos', 'Proteínas', 'Pre-Entrenos', 'Multivitamínicos'];

  return (
    <div className="min-h-screen bg-gray-50 pt-10 pb-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Cabecera del Catálogo */}
        <div className="mb-10">
          <h1 className="text-4xl font-black text-gray-900 uppercase tracking-tight mb-4">
            Catálogo Completo
          </h1>
          
          {/* Buscador Integrado */}
          <form action="/catalog" className="flex w-full max-w-2xl bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden mb-8">
            <input 
              type="text" 
              name="q" 
              defaultValue={searchParams.q || ""}
              placeholder="Buscar por nombre, marca o ingrediente..." 
              className="flex-grow px-6 py-4 focus:outline-none"
            />
            <button type="submit" className="bg-green-500 text-black font-black px-8 uppercase hover:bg-green-400 transition">
              Buscar
            </button>
          </form>

          {/* Filtros rápidos (Pills) */}
          <div className="flex flex-wrap gap-3">
            <Link 
              href="/catalog" 
              className={`px-6 py-2 rounded-full font-bold transition-all border ${!searchParams.category ? 'bg-black text-white border-black' : 'bg-white text-gray-600 border-gray-300 hover:border-black'}`}
            >
              Todos
            </Link>
            {categories.map((cat) => (
              <Link 
                key={cat} 
                href={`/catalog?category=${cat}`}
                className={`px-6 py-2 rounded-full font-bold transition-all border ${searchParams.category === cat ? 'bg-black text-white border-black' : 'bg-white text-gray-600 border-gray-300 hover:border-black'}`}
              >
                {cat}
              </Link>
            ))}
          </div>
        </div>

        {/* Resultados */}
        {products.length === 0 ? (
          <div className="bg-white rounded-3xl p-16 text-center shadow-sm border border-gray-100">
            <div className="text-6xl mb-4">🔍</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">No encontramos productos</h2>
            <p className="text-gray-500 mb-6">Intenta con otra palabra o elimina los filtros.</p>
            <Link href="/catalog" className="bg-black text-white px-8 py-3 rounded-full font-bold hover:bg-gray-800 transition">
              Ver todo el catálogo
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {products.map((product) => (
              <div key={product.id} className="flex flex-col h-full bg-white rounded-2xl border border-gray-100 hover:shadow-xl transition-shadow duration-300 overflow-hidden group">
                <Link href={`/product/${product.slug}`} className="relative block aspect-square bg-gray-50 overflow-hidden">
                  {product.brand && (
                    <span className="absolute top-3 left-3 z-10 bg-black text-white text-xs font-bold px-3 py-1 rounded-full uppercase shadow-md">
                      {product.brand}
                    </span>
                  )}
                  <img 
                    src={product.image_url || product.images || "https://placehold.co/600x600/eeeeee/999999?text=Sin+Imagen"} 
                    alt={product.name} 
                    className="w-full h-full object-contain p-4 group-hover:scale-105 transition-transform duration-500"
                  />
                </Link>
                <div className="p-6 flex flex-col flex-grow">
                  <p className="text-xs text-green-600 font-bold uppercase tracking-wider mb-2">{product.category}</p>
                  <Link href={`/product/${product.slug}`}>
                    <h3 className="font-bold text-gray-900 leading-tight mb-4 line-clamp-2 hover:text-green-600 transition">
                      {product.name}
                    </h3>
                  </Link>
                  <div className="mt-auto flex items-end justify-between mb-4">
                    <div>
                      {product.compare_price && product.compare_price > product.price && (
                        <p className="text-sm text-gray-400 line-through">${product.compare_price.toFixed(2)}</p>
                      )}
                      <p className="text-2xl font-black text-gray-900">${product.price.toFixed(2)}</p>
                    </div>
                  </div>
                  <AddToCartButton product={product} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
