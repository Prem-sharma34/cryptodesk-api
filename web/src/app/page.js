import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-950 text-white">
      <h1 className="text-4xl font-bold text-blue-400 mb-2">CryptoDesk</h1>
      <p className="text-gray-400 mb-8">Track your favourite crypto assets</p>
      <div className="flex gap-4">
        <Link href="/login"
          className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition">
          Login
        </Link>
        <Link href="/register"
          className="bg-gray-700 hover:bg-gray-600 px-6 py-3 rounded-lg font-semibold transition">
          Register
        </Link>
      </div>
    </div>
  );
}