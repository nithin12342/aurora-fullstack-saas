import type { Metadata } from 'next';
import { Inter, Cal_Sans } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });
const calSans = Cal_Sans({
  weight: '400',
  subsets: ['latin'],
  variable: '--font-cal',
});

export const metadata: Metadata = {
  title: {
    default: 'Aurora - Modern SaaS Platform',
    template: '%s | Aurora',
  },
  description: 'Modern SaaS web application with micro-frontends and BFF pattern',
  keywords: ['SaaS', 'Micro-frontends', 'Next.js', 'React', 'TypeScript'],
  authors: [{ name: 'Dulux Tech' }],
  creator: 'Dulux Tech',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://aurora.example.com',
    siteName: 'Aurora',
    title: 'Aurora - Modern SaaS Platform',
    description: 'Modern SaaS web application with micro-frontends and BFF pattern',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Aurora - Modern SaaS Platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Aurora - Modern SaaS Platform',
    description: 'Modern SaaS web application with micro-frontends and BFF pattern',
    creator: '@duluxtech',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${calSans.variable}`}>
      <body className="min-h-screen bg-white dark:bg-slate-950 font-sans antialiased">
        <div id="app-root">{children}</div>
      </body>
    </html>
  );
}
