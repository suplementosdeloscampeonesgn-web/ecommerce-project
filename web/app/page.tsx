import Link from "next/link";
import { getProducts } from "./actions/productActions";
import AddToCartButton from "../components/AddToCartButton";

export const dynamic = "force-dynamic";

export default async function Home() {
  const products = await getProducts();

  const categoriesData = [
    { name: "Quemadores", icon: "🔥", desc: "Maximiza tu definición y energía." },
    { name: "Aminoácidos", icon: "⚛️", desc: "Protege y nutre tus fibras musculares." },
    { name: "Proteínas", icon: "💪", desc: "Acelera tu recuperación y crecimiento." },
    { name: "Pre-Entrenos", icon: "⚡", desc: "Potencia tu rendimiento y enfoque." },
    { name: "Multivitamínicos", icon: "💊", desc: "Refuerza tu salud general y vitalidad." },
  ];

  const servicesData = [
    { name: "Entrega Local Rápida", icon: "🚚", desc: "Servicio garantizado en toda el área metropolitana de SLP." },
    { name: "Asesoría Personalizada", icon: "🧑‍🏫", desc: "Plan nutricional adaptado a tus metas físicas." },
    { name: "Productos Premium", icon: "💎", desc: "Solo marcas probadas, seguras y originales." },
  ];

  return (
    <div className="flex flex-col min-h-screen bg-white selection:bg-green-500 selection:text-black">
      
      {/* 1. HERO SECTION - High Contrast & Cinematic */}
      <section className="relative bg-black text-white overflow-hidden">
        <div className="absolute inset-0 opacity-50 bg-[url('https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center mix-blend-luminosity" />
        <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-black/40" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-32 md:py-48 flex flex-col items-center text-center z-10">
          <span className="px-4 py-1.5 bg-green-500/10 text-green-400 border border-green-500/20 font-bold text-xs uppercase tracking-[0.2em] rounded-full mb-8 backdrop-blur-sm">
            Rendimiento de Élite
          </span>
          <h1 className="text-5xl md:text-7xl font-black uppercase tracking-tighter mb-6 leading-tight">
            Suplementos De Los <br className="hidden md:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-500">Campeones GN</span>
          </h1>
          <p className="text-lg md:text-xl text-gray-400 max-w-2xl mb-12 font-light tracking-wide">
            Fórmulas de alto rendimiento, envío local confiable y la calidad que tu entrenamiento merece.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
            <Link 
              href="/catalog" 
              className="bg-white text-black px-8 py-4 rounded-none font-bold text-sm uppercase tracking-widest hover:bg-green-400 hover:text-black transition-colors duration-300 flex items-center justify-center"
            >
              Ir al Catálogo
            </Link>
            <a 
              href="#ubicacion" 
              className="bg-transparent border border-white/30 text-white px-8 py-4 rounded-none font-bold text-sm uppercase tracking-widest hover:bg-white/10 transition-colors duration-300 flex items-center justify-center"
            >
              Ubicación
            </a>
          </div>
        </div>
      </section>

      {/* 2. SECCIÓN DE CATEGORÍAS - Minimalist Grid */}
      <section className="py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-sm font-bold text-green-600 uppercase tracking-[0.2em] mb-2">Explora</h2>
            <h3 className="text-3xl font-black text-gray-900 uppercase tracking-tight">Tu Suplemento Ideal</h3>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {categoriesData.map((cat) => (
              <Link 
                href={`/catalog?category=${cat.name}`} 
                key={cat.name} 
                className="bg-white p-8 border border-gray-200 hover:border-black text-center transition-all duration-300 group flex flex-col items-center"
              >
                <div className="text-4xl mb-6 grayscale group-hover:grayscale-0 transition-all duration-500">{cat.icon}</div>
                <h3 className="font-bold text-sm uppercase text-gray-900 mb-2 tracking-wide group-hover:text-green-600 transition-colors">{cat.name}</h3>
                <p className="text-xs text-gray-500 mt-auto leading-relaxed">{cat.desc}</p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* 3. CATÁLOGO DE PRODUCTOS (Los Más Vendidos) - Clean Architecture */}
      <section className="py-32 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-end mb-16 gap-6 border-b border-gray-100 pb-8">
            <div>
              <h2 className="text-sm font-bold text-green-600 uppercase tracking-[0.2em] mb-2">Top Ventas</h2>
              <h3 className="text-4xl font-black text-gray-900 uppercase tracking-tight">Destacados</h3>
            </div>
            <Link href="/catalog" className="text-sm font-bold uppercase tracking-widest border-b-2 border-black pb-1 hover:text-green-600 hover:border-green-600 transition-colors">
              Ver Todos →
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {products.slice(0, 4).map((product) => (
              <div key={product.id} className="flex flex-col h-full group">
                <Link href={`/product/${product.slug}`} className="relative block aspect-[4/5] bg-gray-50 mb-6 overflow-hidden border border-gray-100">
                  {product.brand && (
                    <span className="absolute top-4 left-4 z-10 bg-black text-white text-[10px] font-bold px-3 py-1 uppercase tracking-widest">
                      {product.brand}
                    </span>
                  )}
                  <img 
                    src={product.image_url || product.images || "https://placehold.co/600x800/eeeeee/999999?text=Sin+Imagen"} 
                    alt={product.name} 
                    className="w-full h-full object-contain p-8 mix-blend-multiply group-hover:scale-110 transition-transform duration-700 ease-in-out"
                  />
                </Link>

                <div className="flex flex-col flex-grow px-2">
                  <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-2">{product.category}</p>
                  <Link href={`/product/${product.slug}`}>
                    <h3 className="font-bold text-lg text-gray-900 leading-tight mb-4 line-clamp-2 hover:text-green-600 transition-colors">
                      {product.name}
                    </h3>
                  </Link>
                  <div className="mt-auto flex items-end gap-3 mb-6">
                    <p className="text-2xl font-black text-gray-900">${product.price.toFixed(2)}</p>
                    {product.compare_price && product.compare_price > product.price && (
                      <p className="text-sm text-gray-400 line-through mb-1">${product.compare_price.toFixed(2)}</p>
                    )}
                  </div>
                  {/* Asegúrate de que AddToCartButton tenga un diseño acorde en su propio componente */}
                  <AddToCartButton product={product} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 4. SECCIÓN DE SERVICIOS - Modern & Crisp */}
      <section className="py-24 bg-black text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12 divide-y md:divide-y-0 md:divide-x divide-gray-800">
            {servicesData.map((service) => (
              <div key={service.name} className="flex flex-col items-center text-center pt-8 md:pt-0 md:px-8">
                <div className="text-4xl mb-6">{service.icon}</div>
                <h3 className="font-bold text-lg uppercase tracking-wide mb-3">{service.name}</h3>
                <p className="text-sm text-gray-400 font-light leading-relaxed">{service.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 5. SECCIÓN DE UBICACIÓN Y CONTACTO */}
      <section id="ubicacion" className="py-32 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
          <div>
            <h2 className="text-sm font-bold text-green-600 uppercase tracking-[0.2em] mb-2">Visítanos</h2>
            <h3 className="text-4xl font-black text-gray-900 uppercase tracking-tight mb-6">Nuestra Tienda</h3>
            <p className="text-gray-600 mb-10 text-lg font-light leading-relaxed">
              Selecciona "Recoger en Sucursal" al finalizar tu compra. También contamos con envíos exprés en toda el área metropolitana.
            </p>
            
            <div className="space-y-8">
              <div className="flex items-start gap-6">
                <div className="text-2xl pt-1">📍</div>
                <div>
                  <p className="font-bold text-gray-900 uppercase tracking-wide">Dirección</p>
                  <p className="text-gray-600 mt-1">Av Vicente Rivera 131 A, Colonia Nuevo Paseo<br/>San Luis Potosí, México.</p>
                </div>
              </div>
              <div className="flex items-start gap-6">
                <div className="text-2xl pt-1">📱</div>
                <div>
                  <p className="font-bold text-gray-900 uppercase tracking-wide">Contacto Directo</p>
                  <p className="text-gray-600 mt-1">+52 444 316 6595 (WhatsApp)</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-200 aspect-square md:aspect-[4/3] relative overflow-hidden filter grayscale hover:grayscale-0 transition-all duration-700 shadow-xl">
            <iframe 
              src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3695.539794354763!2d-100.9715!3d22.13!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zMjLCsDA3JzQ4LjAiTiAxMDDCsDU4JzE3LjQiVw!5e0!3m2!1ses-419!2smx!4v1600000000000!5m2!1ses-419!2smx" 
              className="w-full h-full absolute inset-0" 
              loading="lazy"
            ></iframe>
          </div>
        </div>
      </section>

    </div>
  );
}
