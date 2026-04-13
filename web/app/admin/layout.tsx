import Link from "next/link";
import { ReactNode } from "react";

export default function AdminLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <aside className="w-64 bg-gray-900 text-white flex flex-col shadow-xl sticky top-0 h-screen">
        <div className="p-6 border-b border-gray-800">
          <h2 className="text-xl font-black tracking-wider text-green-400">EL BÚNKER</h2>
          <p className="text-xs text-gray-400 mt-1">Panel de Administración</p>
        </div>
        <nav className="flex-1 p-4 space-y-2 mt-4">
          <Link href="/admin" className="block px-4 py-3 rounded-lg hover:bg-gray-800 transition font-medium">📊 Resumen General</Link>
          <Link href="/admin/orders" className="block px-4 py-3 rounded-lg hover:bg-gray-800 transition font-medium">📦 Pedidos</Link>
          <Link href="/" className="block px-4 py-3 rounded-lg hover:bg-gray-800 transition text-gray-400 mt-12 border border-gray-800">⬅ Volver a la Tienda</Link>
        </nav>
      </aside>
      <main className="flex-1 p-8 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}