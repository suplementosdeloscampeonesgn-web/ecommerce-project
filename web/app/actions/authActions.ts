"use server";

import bcrypt from "bcryptjs";
import { signIn } from "@/auth";
import { prisma } from "@/app/lib/prisma";

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
      error: "La contraseña debe tener al menos 8 caracteres.",
    };
  }

  try {
    const existing = await prisma.user.findUnique({ where: { email } });
    if (existing) {
      return {
        ok: false,
        error: "Ya existe una cuenta con este correo electrónico.",
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
  } catch {
    return {
      ok: false,
      error: "No se pudo crear la cuenta. Intenta de nuevo más tarde.",
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
      return { ok: false, error: "No se pudo iniciar sesión." };
    }

    let parsed: URL;
    try {
      parsed = new URL(url, "http://localhost");
    } catch {
      return { ok: false, error: "No se pudo iniciar sesión." };
    }

    if (parsed.searchParams.get("error")) {
      return {
        ok: false,
        error: "Correo o contraseña incorrectos.",
      };
    }

    return { ok: true };
  } catch {
    return {
      ok: false,
      error: "Correo o contraseña incorrectos.",
    };
  }
}
