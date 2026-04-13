"use server";

import { auth } from "../../auth";
import { prisma } from "../lib/prisma";

export async function createOrder(checkoutData: any, cartItems: any[]) {
  const session = await auth();
  
  if (!session?.user?.id) {
    throw new Error("Debes iniciar sesión para comprar");
  }

  // Generamos un número de orden único para SLP
  const orderNumber = `SLP-${Date.now()}`;
  const totalAmount = cartItems.reduce((acc, item) => acc + (item.price * item.quantity), 0);
  
  // Determinamos la dirección final según lo que eligió
  const finalAddress = checkoutData.shipping_type === 'Uber' 
    ? checkoutData.address 
    : `Recoger en Sucursal - Horario: ${checkoutData.pickup_time}`;

  // Usamos una transacción para guardar la orden y sus items al mismo tiempo
  const order = await prisma.order.create({
    data: {
      user_id: parseInt(session.user.id),
      order_number: orderNumber,
      status: "PENDING",
      total_amount: totalAmount,
      shipping_address: finalAddress,
      shipping_type: checkoutData.shipping_type,
      payment_method: "CLABE",
      order_items: {
        create: cartItems.map((item) => ({
          product_id: item.id,
          product_name: item.name,
          product_price: item.price,
          quantity: item.quantity,
          line_total: item.price * item.quantity
        }))
      }
    }
  });

  return { success: true, orderId: order.id, orderNumber: order.order_number };
}