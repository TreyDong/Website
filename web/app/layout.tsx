import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
    title: '微信读书自动签到',
    description: '微信读书自动签到服务',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
    return (
        <html lang="zh">
            <body>
                {children}
            </body>
        </html>
    );
}
