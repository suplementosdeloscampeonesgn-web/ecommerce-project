import { useEffect, useState } from "react";
import axios from "axios";
import { useCart } from "../context/CartContext";
import ProductCard from "../components/ProductCard";
import HeroSlider from "../components/HeroSlider"; // Importa el nuevo componente
import { LuDumbbell, LuFlame, LuHeartPulse } from "react-icons/lu";

// Array de banners promocionales, aquí lo puedes controlar/fetch o personalizar
const banners = [
  {
    image: "/assets/banner1.jpg",
    headline: "Potencia tu cuerpo con GN",
    subline: "Suplementos de los Campeones GN - Resultados reales para atletas reales",
    cta: "Ver tienda",
    link: "/shop"
  },
  {
    image: "/assets/banner2.jpg",
    headline: "Fuerza, energía y salud",
    subline: "El mejor surtido de proteínas, vitaminas y más.",
    cta: "Descubre promociones",
    link: "/shop"
  }
];

// Tarjetas informativas fijas
const infoCards = [
  {
    id: "proteinas",
    title: "¡Proteínas premium!",
    description: "El mejor surtido en whey, caseína y proteínas veganas para cualquier meta.",
    link: "/categoria/proteinas",
    button: "Ver más",
    Icon: LuDumbbell
  },
  {
    id: "preentrenos",
    title: "Energía al máximo",
    description: "Pre-entrenos y estimulantes para enfoque, resistencia y rendimiento.",
    link: "/categoria/preentrenos",
    button: "Explorar",
    Icon: LuFlame
  },
  {
    id: "vitaminas",
    title: "Salud total",
    description: "Vitaminas, minerales y antioxidantes para bienestar y recuperación.",
    link: "/categoria/vitaminas",
    button: "Nuestra selección",
    Icon: LuHeartPulse
  }
];

function QuickInfoCard({ title, description, link, button, Icon }) {
  return (
    <div className="bg-dark rounded-4 shadow-lg d-flex flex-column align-items-center justify-content-between p-4 min-card-height w-100">
      <Icon style={{ width: 48, height: 48 }} className="text-warning mb-3" />
      <div className="fw-bold fs-4 text-warning mb-2 text-center">{title}</div>
      <div className="text-white-50 small mb-4 text-center">{description}</div>
      <a href={link} className="btn btn-warning text-dark fw-bold rounded-pill px-4 py-2">{button}</a>
    </div>
  );
}

export default function Home() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const { dispatch } = useCart();

  useEffect(() => {
    setLoading(true);
    axios.get("http://localhost:8000/api/products")
      .then(res => setProducts(res.data.products || res.data))
      .catch(() => setProducts([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="home-bg-gradient min-vh-100 pt-5">
      {/* HERO SLIDER CONTROLADO DESDE APARTE */}
      <HeroSlider banners={banners} />

      {/* TRES RECUADROS FIJOS */}
      <div className="container mb-5">
        <div className="row g-4">
          {infoCards.map(card => (
            <div className="col-12 col-md-4" key={card.id}>
              <QuickInfoCard {...card} />
            </div>
          ))}
        </div>
      </div>

      {/* DESTACADOS */}
      <div className="container px-3">
        <h2 className="fs-2 fw-bold mb-4 text-primary">Productos destacados</h2>
        {loading ? (
          <div className="text-primary fw-bold py-5 text-center">Cargando productos...</div>
        ) : (
          <div className="row g-3 animate-fade-in">
            {products.slice(0, 8).map(product =>
              <div className="col-12 col-sm-6 col-md-4 col-lg-3" key={product.id}>
                <ProductCard
                  product={product}
                  onAddToCart={() => dispatch({ type: "ADD_ITEM", payload: { product, quantity: 1 } })}
                />
              </div>
            )}
          </div>
        )}
      </div>

      {/* TESTIMONIOS (opcional) */}
      <section className="container my-5">
        <div className="bg-white rounded-3 shadow-lg p-5 d-flex flex-column flex-md-row align-items-center">
          <img src="/assets/user-champion.jpg" alt="" className="rounded-circle object-fit-cover mb-3 mb-md-0 me-md-4 border border-4 border-warning" style={{ height: "96px", width: "96px" }} />
          <blockquote className="fs-4 text-primary fw-semibold fst-italic flex-grow-1 m-0 text-center text-md-start">
            “Los productos GN mejoraron mi resistencia y mi salud. Realmente son suplementos de campeones.”
            <br />
            <span className="d-block text-warning fw-bold mt-2">— Brenda G., atleta nacional</span>
          </blockquote>
        </div>
      </section>
    </div>
  );
}