import { getAdminDashboardData } from "../actions/adminActions";

export const dynamic = "force-dynamic";

export default async function AdminDashboard() {
  const data = await getAdminDashboardData();

  return (
    <div>
      <h1 className="text-3xl font-extrabold text-gray-900 mb-8">Vista General</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500 font-semibold uppercase tracking-wider">Usuarios Registrados</p>
          <p className="text-4xl font-black text-gray-900 mt-2">{data.totalUsers}</p>
        </div>
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500 font-semibold uppercase tracking-wider">Pedidos Totales</p>
          <p className="text-4xl font-black text-gray-900 mt-2">{data.totalOrders}</p>
        </div>
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 bg-gradient-to-br from-green-50 to-white">
          <p className="text-sm text-green-700 font-semibold uppercase tracking-wider">Ingresos Totales</p>
          <p className="text-4xl font-black text-green-600 mt-2">${data.totalRevenue.toFixed(2)} mxn</p>
        </div>
      </div>
    </div>
  );
}