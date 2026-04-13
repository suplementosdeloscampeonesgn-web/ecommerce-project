"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { registerUser } from "../actions/authActions";
import toast from "react-hot-toast";

export default function RegisterPage() {
  const router = useRouter();
  const [pending, setPending] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPending(true);
    
    // Disparamos la notificación de carga
    const loadingToast = toast.loading("Forjando credenciales...");

    const formData = new FormData(e.currentTarget);
    const result = await registerUser(formData);

    setPending(false);

    if (result.ok) {
      toast.success("¡Cuenta creada! Bienvenido al Búnker.", { id: loadingToast });
      router.push("/login?registered=1");
    } else {
      toast.error(result.error || "Error al crear la cuenta.", { id: loadingToast });
    }
  }

  return (
    <div className="min-h-screen bg-white flex flex-col justify-center py-12 sm:px-6 lg:px-8 selection:bg-green-500 selection:text-black pt-12">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <span className="text-green-500 font-black text-xs uppercase tracking-[0.2em] mb-2 block">
          Nuevo Recluta
        </span>
        <h1 className="text-4xl md:text-5xl font-black text-black uppercase tracking-tighter">
          Crear Cuenta
        </h1>
        <p className="mt-4 text-sm text-gray-500 font-bold tracking-wide">
          Únete y accede a suplementos de alto rendimiento.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-2xl border-2 border-black sm:px-10">
          <form className="space-y-6" onSubmit={handleSubmit}>
            
            {/* Campo: Nombre */}
            <div>
              <label htmlFor="name" className="block text-xs font-black text-black uppercase tracking-widest mb-2">
                Nombre Completo
              </label>
              <div className="mt-1">
                <input
                  id="name"
                  name="name"
                  type="text"
                  required
                  autoComplete="name"
                  placeholder="Ej. Arnold"
                  className="appearance-none block w-full px-4 py-3 border-2 border-gray-200 placeholder-gray-400 text-black font-medium focus:outline-none focus:border-black transition-colors"
                />
              </div>
            </div>

            {/* Campo: Correo */}
            <div>
              <label htmlFor="email" className="block text-xs font-black text-black uppercase tracking-widest mb-2">
                Correo Electrónico
              </label>
              <div className="mt-1">
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  autoComplete="email"
                  placeholder="tu@correo.com"
                  className="appearance-none block w-full px-4 py-3 border-2 border-gray-200 placeholder-gray-400 text-black font-medium focus:outline-none focus:border-black transition-colors"
                />
              </div>
            </div>

            {/* Campo: Contraseña */}
            <div>
              <label htmlFor="password" className="block text-xs font-black text-black uppercase tracking-widest mb-2">
                Contraseña
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  minLength={8}
                  autoComplete="new-password"
                  placeholder="Mínimo 8 caracteres"
                  className="appearance-none block w-full px-4 py-3 border-2 border-gray-200 placeholder-gray-400 text-black font-medium focus:outline-none focus:border-black transition-colors"
                />
              </div>
            </div>

            {/* Botón de Submit */}
            <div className="pt-2">
              <button
                type="submit"
                disabled={pending}
                className="w-full flex justify-center items-center py-4 px-4 border border-transparent text-sm font-black uppercase tracking-widest text-white bg-black hover:bg-green-500 hover:text-black transition-colors duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {pending ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Procesando...
                  </>
                ) : (
                  "Registrarse"
                )}
              </button>
            </div>
          </form>

          {/* Footer del Formulario */}
          <div className="mt-8 border-t-2 border-gray-100 pt-6 text-center">
            <p className="text-xs text-gray-500 font-bold uppercase tracking-wider">
              ¿Ya tienes cuenta?{" "}
              <Link href="/login" className="text-black font-black hover:text-green-600 transition-colors border-b-2 border-black hover:border-green-600 pb-0.5 ml-1">
                Iniciar Sesión
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
