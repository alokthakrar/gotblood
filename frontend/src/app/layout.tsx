import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";

const inter = Inter({ 
  subsets: ["latin"],
  display: 'swap',
});

export const metadata: Metadata = {
  title: "Got Blood? - Blood Management Platform",
  description: "Centralized blood management platform for hospitals and donors",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav className="bg-white shadow-lg fixed w-full z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <Link href="/" className="flex items-center">
                  <span className="text-2xl font-bold text-primary-red">Got Blood?</span>
                </Link>
              </div>
              <div className="flex items-center space-x-8">
                <Link href="/map" className="text-dark-gray hover:text-primary-red font-semibold transition-colors">
                  Interactive Map
                </Link>
                <Link href="/statistics" className="text-dark-gray hover:text-primary-red font-semibold transition-colors">
                  Blood Statistics
                </Link>
                <Link href="/account" className="text-dark-gray hover:text-primary-red font-semibold transition-colors">
                  Account
                </Link>
                <button className="btn-primary">
                  Donate Now
                </button>
              </div>
            </div>
          </div>
        </nav>
        <main className="pt-16">
          {children}
        </main>
        <footer className="bg-dark-gray text-white py-8 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div>
                <h3 className="text-xl font-bold mb-4">Got Blood?</h3>
                <p className="text-gray-300">Making blood donation and management efficient and accessible.</p>
              </div>
              <div>
                <h3 className="text-xl font-bold mb-4">Quick Links</h3>
                <ul className="space-y-2">
                  <li><Link href="/about" className="text-gray-300 hover:text-white">About Us</Link></li>
                  <li><Link href="/contact" className="text-gray-300 hover:text-white">Contact</Link></li>
                  <li><Link href="/faq" className="text-gray-300 hover:text-white">FAQ</Link></li>
                </ul>
              </div>
              <div>
                <h3 className="text-xl font-bold mb-4">Connect With Us</h3>
                <div className="flex space-x-4">
                  <a href="#" className="text-gray-300 hover:text-white">Twitter</a>
                  <a href="#" className="text-gray-300 hover:text-white">Facebook</a>
                  <a href="#" className="text-gray-300 hover:text-white">Instagram</a>
                </div>
              </div>
            </div>
            <div className="mt-8 pt-8 border-t border-gray-700 text-center text-gray-300">
              <p>&copy; 2024 Got Blood?. All rights reserved.</p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
