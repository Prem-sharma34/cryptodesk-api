import "./globals.css";

export const metadata = {
  title: "CryptoDesk",
  description: "Your personal crypto watchlist",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-gray-950 antialiased">{children}</body>
    </html>
  );
}