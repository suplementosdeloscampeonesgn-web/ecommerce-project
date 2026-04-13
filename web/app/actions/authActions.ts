"use server";

import bcrypt from "bcryptjs";
import { signIn } from "@/auth";
import { prisma } from "@/app/lib/prisma"; // Import respetado al 100%

export type AuthActionResult =
  | { ok: true }
  | { ok: false; error: string };

export async function registerUser(
  formData: FormData,
): Promise<AuthActionResult> {
  const name = String(formData.get("name") ?? "").trim();
  const email = String(formData.get("email") ?? "")
    .trim()
    .toLowerCase();
  const password = String(formData.get("password") ?? "");

  if (!email || !password) {
    return { ok: false, error: "El correo y la contraseña son obligatorios." };
  }

  if (password.length < 8) {
    return {
      ok: false,
      error: "La contraseña debe tener al menos 8 caracteres para asegurar el búnker.",
    };
  }

  try {
    const existing = await prisma.user.findUnique({ 
      where: { email },
      select: { id: true } // Optimización de consulta
    });
    
    if (existing) {
      return {
        ok: false,
        error: "Este correo ya pertenece a un recluta activo. Intenta iniciar sesión.",
      };
    }

    const hashed_password = await bcrypt.hash(password, 12);

    await prisma.user.create({
      data: {
        email,
        name: name || null,
        hashed_password,
        provider: "local",
        role: "customer",
        is_active: true,
      },
    });

    return { ok: true };
  } catch (error) {
    console.error("[AUTH_REGISTER_ERROR]", error);
    return {
      ok: false,
      error: "Fallo en la base de datos central. Intenta de nuevo más tarde.",
    };
  }
}

export async function loginUser(
  formData: FormData,
): Promise<AuthActionResult> {
  const email = String(formData.get("email") ?? "").trim().toLowerCase();
  const password = String(formData.get("password") ?? "");

  if (!email || !password) {
    return { ok: false, error: "Completa el correo y la contraseña." };
  }

  try {
    const url = await signIn("credentials", {
      email,
      password,
      redirect: false,
      redirectTo: "/profile",
    });

    if (typeof url !== "string") {
      return { ok: false, error: "Las credenciales rebotaron. Intenta de nuevo." };
    }

    let parsed: URL;
    try {
      // CORRECCIÓN VITAL PARA PRODUCCIÓN: 
      // Se utiliza tu dominio real como base para evitar fallos de parseo en Vercel/Render
      parsed = new URL(url, "https://suplementosdeloscampeonesgn.shop");
    } catch {
      return { ok: false, error: "Error interno de redirección." };
    }

    if (parsed.searchParams.get("error")) {
      return {
        ok: false,
        error: "Correo o contraseña incorrectos. Acceso denegado.",
      };
    }

    return { ok: true };
  } catch (error) {
    console.error("[AUTH_LOGIN_ERROR]", error);
    return {
      ok: false,
      error: "Correo o contraseña incorrectos. Acceso denegado.",
    };
  }
}
