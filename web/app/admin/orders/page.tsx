import { getAdminOrders } from "../../actions/adminActions";

export const dynamic = "force-dynamic";

export default async function AdminOrders() {
  const orders = await getAdminOrders();

  return (
    <div>
      <h1 className="text-3xl font-extrabold text-gray-900 mb-8">Gestión de Pedidos</h1>
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-100">
              <th className="p-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Orden #</th>
              <th className="p-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Cliente</th>
              <th className="p-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Método</th>
              <th className="p-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Total</th>
              <th className="p-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Estado</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {orders.map((order) => (
              <tr key={order.id} className="hover:bg-gray-50 transition-colors">
                <td className="p-4 text-sm font-bold text-gray-900">{order.order_number}</td>
                <td className="p-4 text-sm text-gray-600">{order.user?.name || order.user?.email || 'Anónimo'}</td>
                <td className="p-4 text-sm text-gray-600">{order.shipping_type}</td>
                <td className="p-4 text-sm font-bold text-gray-900">${order.total_amount.toFixed(2)}</td>
                <td className="p-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-black tracking-wide ${
                    order.status === 'PAID' ? 'bg-green-100 text-green-800' :
                    order.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {order.status || 'PENDING'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}