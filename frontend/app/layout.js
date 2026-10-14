import "./globals.css";

export const metadata = {
  title: "BookNook shelf assistant",
  description: "Demo chat over the BookNook reading-room notes",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
