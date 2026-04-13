"use server";

import type { Product } from "@/app/generated/prisma/client";
import { prisma } from "../lib/prisma";

export async function getProducts(): Promise<Product[]> {
  try {
    const products = await prisma.product.findMany({
      where: { is_active: true },
      orderBy: [{ created_at: "desc" }, { name: "asc" }],
    });
    return products;
  } catch (error) {
    console.error("[getProducts]", error);
    return [];
  }
}
