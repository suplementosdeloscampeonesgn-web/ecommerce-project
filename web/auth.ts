import NextAuth from "next-auth";
import type { NextAuthConfig } from "next-auth";
import Credentials from "next-auth/providers/credentials";

const authConfig = {
  providers: [
    Credentials({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }
        const email = String(credentials.email).toLowerCase().trim();
        const password = String(credentials.password);

        const { prisma } = await import("@/app/lib/prisma");
        const bcryptjs = (await import("bcryptjs")).default;

        const user = await prisma.user.findUnique({
          where: { email },
        });

        if (!user?.hashed_password) {
          return null;
        }
        if (user.is_active === false) {
          return null;
        }

        const valid = await bcryptjs.compare(password, user.hashed_password);
        if (!valid) {
          return null;
        }

        const role = user.role?.trim() || "customer";

        return {
          id: String(user.id),
          email: user.email,
          name: user.name ?? undefined,
          role,
        };
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.role = user.role ?? "customer";
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = (token.id as string) ?? "";
        session.user.role = (token.role as string) ?? "customer";
      }
      return session;
    },
  },
  pages: {
    signIn: "/login",
  },
  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60,
  },
  trustHost: true,
} satisfies NextAuthConfig;

export const { handlers, auth, signIn, signOut } = NextAuth(authConfig);
