import Link from "next/link";
import { getProducts } from "./actions/productActions";
import AddToCartButton from "../components/AddToCartButton";

export const dynamic = "force-dynamic";

export default async function Home() {
  const products = await getProducts();

  // Definimos las categorías con sus iconos y descripciones reales
  const categoriesData = [
    { name: "Quemadores", icon: "🔥", desc: "Maximiza tu definición y energía." },
    { name: "Aminoácidos", icon: "⚛️", desc: "Protege y nutre tus fibras musculares." },
    { name: "Proteínas", icon: "💪", desc: "Acelera tu recuperación y crecimiento." },
    { name: "Pre-Entrenos", icon: "⚡", desc: "Potencia tu rendimiento y enfoque." },
    { name: "Multivitamínicos", icon: "💊", desc: "Refuerza tu salud general y vitalidad." },
  ];

  // Definimos tus servicios exclusivos para SLP
  const servicesData = [
    { name: "Entrega Local Rápida", icon: "🚚", desc: "Servicio garantizado en toda el área de SLP." },
    { name: "Asesoría Personalizada", icon: "🧑‍🏫", desc: "Plan nutricional adaptado a tus metas físicas." },
    { name: "Productos Premium", icon: "💎", desc: "Solo marcas probadas, seguras y originales." },
  ];

  return (
    <div className="flex flex-col min-h-screen">
      
      {/* 1. HERO SECTION (Banner Principal con Gimnasio) */}
      <section className="relative bg-black text-white overflow-hidden">
        <div className="absolute inset-0 opacity-40 bg-[url('https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-32 md:py-48 flex flex-col items-center text-center">
          <span className="px-4 py-1 bg-green-500 text-black font-black text-sm uppercase tracking-widest rounded-full mb-6">
            Rendimiento de Élite
          </span>
          <h1 className="text-5xl md:text-7xl font-black uppercase tracking-tight mb-6">
            Suplementos De Los <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-600">Campeones GN</span>
          </h1>
          <p className="text-lg md:text-2xl text-gray-300 max-w-3xl mb-10">
            Fórmulas de alto rendimiento, envío local confiable y la calidad que tu entrenamiento en San Luis Potosí merece.
          </p>
          <div className="flex gap-4">
            <a href="#productos" className="bg-white text-black px-8 py-4 rounded-full font-bold hover:bg-gray-200 transition transform hover:scale-105 shadow-xl">
              Ver Catálogo
            </a>
            <a href="#ubicacion" className="bg-transparent border-2 border-white text-white px-8 py-4 rounded-full font-bold hover:bg-white hover:text-black transition">
              Nuestra Ubicación
            </a>
          </div>
        </div>
      </section>

      {/* 2. SECCIÓN DE CATEGORÍAS */}
      <section className="py-20 bg-gray-50 border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-black text-center mb-16 uppercase tracking-tight text-gray-900">Encuentra tu Suplemento Ideal</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
            {categoriesData.map((cat) => (
              <div key={cat.name} className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 text-center hover:shadow-xl transition-all cursor-pointer hover:border-green-500 group flex flex-col items-center">
                <div className="text-5xl mb-6 group-hover:scale-110 transition-transform">{cat.icon}</div>
                <h3 className="font-bold text-lg text-gray-900 mb-2 group-hover:text-green-600 transition">{cat.name}</h3>
                <p className="text-sm text-gray-500 mt-auto">{cat.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 3. CATÁLOGO DE PRODUCTOS (Los Más Vendidos) */}
      <section id="productos" className="py-24 bg-white flex-grow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-end mb-16">
            <div>
              <h2 className="text-4xl font-black text-gray-900 uppercase">Los Más Vendidos</h2>
              <p className="text-gray-500 mt-2">Productos destacados por nuestros clientes.</p>
            </div>
            {/* Aquí irán los filtros reales en el Módulo 6 */}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {products.slice(0, 4).map((product) => (
              <div key={product.id} className="flex flex-col h-full bg-white rounded-2xl border border-gray-100 hover:shadow-xl transition-shadow duration-300 overflow-hidden group relative">
                
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
        </div>
      </section>

      {/* 4. SECCIÓN DE SERVICIOS EXCLUSIVOS */}
      <section className="py-20 bg-gray-50 border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-black text-center mb-16 uppercase tracking-tight text-gray-900">Por Qué Elegirnos</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {servicesData.map((service) => (
              <div key={service.name} className="bg-white p-10 rounded-3xl shadow-sm border border-gray-100 text-center hover:shadow-lg transition flex flex-col items-center">
                <div className="text-6xl mb-6">{service.icon}</div>
                <h3 className="font-bold text-xl text-gray-900 mb-3">{service.name}</h3>
                <p className="text-sm text-gray-500">{service.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 5. SECCIÓN DE UBICACIÓN Y CONTACTO (SLP) */}
      <section id="ubicacion" className="py-24 bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
          <div>
            <span className="text-green-500 font-bold uppercase tracking-widest text-sm mb-4 block">Visítanos</span>
            <h2 className="text-4xl font-black uppercase mb-6">Nuestra Tienda en San Luis Potosí</h2>
            <p className="text-gray-400 mb-8 text-lg">
              Selecciona "Recoger en Sucursal" al finalizar tu compra y te estaremos esperando con tu pedido listo. También contamos con envíos exprés por Uber en toda el área metropolitana de SLP.
            </p>
            <div className="space-y-6">
              <div className="flex items-center gap-4 bg-gray-800 p-5 rounded-xl border border-gray-700">
                <div className="text-3xl">📍</div>
                <div>
                  <p className="font-bold text-lg">Suplementos De Los Campeones GN</p>
                  <p className="text-gray-400">Av Vicente Rivera 131 A, Colonia Nuevo Paseo SLP. México.</p>
                </div>
              </div>
              <div className="flex items-center gap-4 bg-gray-800 p-5 rounded-xl border border-gray-700">
                <div className="text-3xl">📱</div>
                <div>
                  <p className="font-bold text-lg">WhatsApp Directo</p>
                  <p className="text-gray-400">444 316 6595</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-800 rounded-3xl p-2 aspect-square md:aspect-video relative overflow-hidden shadow-2xl border border-gray-700">
            <iframe 
              src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d118237.75620959325!2d-101.0664273574972!3d22.14981145391295!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x842aa1fdd5e1657d%3A0x2db47fc3677e5d1b!2sSan%20Luis%20Potos%C3%AD%!,%20S.L.P.!5e0!3m2!1ses!2smx!4v1713028213600!5m2!1ses!2smx" 
              className="w-full h-full rounded-2xl opacity-80 hover:opacity-100 transition-opacity" 
              loading="lazy"
            ></iframe>
          </div>
        </div>
      </section>

    </div>
  );
}