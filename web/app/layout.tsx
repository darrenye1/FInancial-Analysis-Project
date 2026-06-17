import type { Metadata } from "next";
import "./globals.css";

const siteUrl = "https://f-inancial-analysis-project.vercel.app";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: "Tesla Financial Analysis | Darren Ye",
  description:
    "Comprehensive financial analysis of Tesla (TSLA) — P&L, budgeting, forecasting, and sensitivity analysis with real Yahoo Finance data.",
  openGraph: {
    title: "Tesla Financial Analysis Dashboard",
    description: "P&L · Budgeting · Forecasting · Sensitivity Analysis by Darren Ye",
    type: "website",
    url: siteUrl,
    images: [
      {
        url: "/cover/tesla-cover-linkedin.png",
        width: 1200,
        height: 675,
        alt: "Tesla Financial Analysis Project Cover",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Tesla Financial Analysis Dashboard",
    description: "P&L · Budgeting · Forecasting · Sensitivity Analysis",
    images: ["/cover/tesla-cover-linkedin.png"],
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
