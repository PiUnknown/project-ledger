import type { Metadata } from "next";
import type { ReactNode } from "react";
import { DM_Sans, Manrope } from "next/font/google";
import "./globals.css";

const bodyFont = DM_Sans({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-body",
});

const displayFont = Manrope({
  subsets: ["latin"],
  display: "swap",
  weight: ["600", "700"],
  variable: "--font-display",
});

export const metadata: Metadata = {
  title: "Factory Item Agent",
  description: "Demo chat interface for the factory item agent.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html className={`${bodyFont.variable} ${displayFont.variable}`} lang="en">
      <body>{children}</body>
    </html>
  );
}
