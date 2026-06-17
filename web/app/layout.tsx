import type { Metadata } from "next";
import "./globals.css";

const siteUrl = "https://f-inancial-analysis-project.vercel.app";
const ogImage = `${siteUrl}/og-image.png`;

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: "Tesla Financial Analysis | Darren Ye",
  description:
    "Corporate Finance FP&A dashboard for Tesla (TSLA) — P&L, cash flow, working capital, DuPont analysis, budgeting, forecasting, and sensitivity.",
  openGraph: {
    title: "Tesla Financial Analysis Dashboard",
    description: "Corp Fin FP&A — Cash Flow · DuPont · Working Capital · Budgeting · Forecasting",
    type: "website",
    url: siteUrl,
    siteName: "Darren Ye — Financial Analytics",
    images: [
      {
        url: ogImage,
        width: 1200,
        height: 627,
        alt: "Tesla Financial Analysis Project Cover",
        type: "image/png",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Tesla Financial Analysis Dashboard",
    description: "P&L · Budgeting · Forecasting · Sensitivity Analysis",
    images: [ogImage],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <meta property="og:image" content={ogImage} />
        <meta property="og:image:width" content="1200" />
        <meta property="og:image:height" content="627" />
        <meta property="og:image:type" content="image/png" />
        <meta name="twitter:image" content={ogImage} />
      </head>
      <body>{children}</body>
    </html>
  );
}
