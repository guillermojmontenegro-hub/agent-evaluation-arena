import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "Agent Evaluation Arena",
  description: "Reproducible evaluation infrastructure for AI agents.",
};

export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
