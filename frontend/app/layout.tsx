import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PressPulse AI | PR intelligence desk",
  description: "Generate sharper PR pitches and audit claims before you send.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
