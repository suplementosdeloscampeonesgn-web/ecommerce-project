import { auth } from "@/auth";

export default async function ProfilePage() {
  const session = await auth();

  if (!session?.user) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center px-4">
        <div className="max-w-md rounded-2xl border border-gray-200 bg-white p-10 text-center shadow-sm">
          <h1 className="text-xl font-bold text-gray-900">Acceso denegado</h1>
          <p className="mt-3 text-gray-600">
            Debes iniciar sesión para ver tu perfil.
          </p>
        </div>
      </div>
    );
  }

  const displayName =
    session.user.name?.trim() ||
    session.user.email?.split("@")[0] ||
    "usuario";

  return (
    <div className="min-h-[60vh] flex items-center justify-center px-4 py-16">
      <div className="w-full max-w-lg rounded-2xl border border-gray-100 bg-white p-10 shadow-sm">
        <p className="text-sm font-medium uppercase tracking-wide text-gray-500">
          Tu cuenta
        </p>
        <h1 className="mt-2 text-3xl font-extrabold tracking-tight text-gray-900">
          Hola, {displayName}
        </h1>
        <p className="mt-4 text-gray-600">
          Sesión activa como{" "}
          <span className="font-semibold text-gray-900">
            {session.user.email}
          </span>
          .
        </p>
        <p className="mt-2 text-sm text-gray-500">
          Rol:{" "}
          <span className="font-medium text-gray-800">
            {session.user.role}
          </span>
        </p>
      </div>
    </div>
  );
}
