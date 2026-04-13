"use server";

import { auth } from "../../auth";
import { prisma } from "../lib/prisma";

async function requireAdmin() {
  const session = await auth();
  if (!session || session?.user?.role !== "admin") {
    throw new Error("Acceso denegado: No eres administrador");
  }
}

export async function getAdminDashboardData() {
  await requireAdmin();
  
  const totalUsers = await prisma.user.count();
  const totalOrders = await prisma.order.count();
  
  const revenueResult = await prisma.order.aggregate({
    _sum: { total_amount: true },
    where: { status: { not: "CANCELLED" } }
  });

  return {
    totalUsers,
    totalOrders,
    totalRevenue: revenueResult._sum.total_amount || 0,
  };
}

export async function getAdminOrders() {
  await requireAdmin();
  
  return await prisma.order.findMany({
    orderBy: { created_at: "desc" },
    include: {
      user: true, 
      order_items: true 
    }
  });
}