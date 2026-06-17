import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Tesla Financial Analysis | FP&A Portfolio Project",
  description:
    "Comprehensive financial analysis of Tesla (TSLA) — P&L, budgeting, forecasting, and sensitivity analysis with real Yahoo Finance data.",
  openGraph: {
    title: "Tesla Financial Analysis Dashboard",
    description: "P&L · Budgeting · Forecasting · Sensitivity Analysis",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
      </head>
      <body>{children}</body>
    </html>
  );
}
