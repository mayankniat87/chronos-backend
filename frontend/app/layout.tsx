import type { Metadata } from 'next';
import './globals.css';
import Providers from '@/components/layout/Providers';
import AppShell from '@/components/layout/AppShell';
import { Inter, Outfit, JetBrains_Mono } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const outfit = Outfit({
  subsets: ['latin'],
  variable: '--font-outfit',
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
});

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
};

export const metadata: Metadata = {
  title: 'Chronos - Explainable Business Time Machine',
  description: 'The World\'s First Explainable Business Time Machine for SMEs. Run future simulations and analyze knowledge graphs to see the impact of business decisions.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${outfit.variable} ${jetbrainsMono.variable} h-full bg-[#05070B] dark`}>
      <body className="h-full antialiased text-slate-100 select-none">
        <Providers>
          <AppShell>
            {children}
          </AppShell>
        </Providers>
      </body>
    </html>
  );
}
