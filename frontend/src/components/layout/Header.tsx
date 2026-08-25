import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { motion } from 'framer-motion';

export default function Header() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    useEffect(() => {
        const checkAuth = () => {
            setIsLoggedIn(!!localStorage.getItem('fitgen_token'));
        };
        checkAuth();
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('fitgen_token');
        localStorage.removeItem('fitgen_user');
        localStorage.removeItem('fitgen_onboarded');
        localStorage.removeItem('fitgen_theme');
        setIsLoggedIn(false);
        window.location.href = '/';
    };

    return (
        <motion.header
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            transition={{ duration: 0.5 }}
            className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4 bg-black/80 backdrop-blur-md border-b border-white/10"
        >
            <Link href="/" className="flex items-center gap-2">
                <span className="font-heading text-2xl font-semibold tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-yellow-600">
                    FITGEN
                </span>
            </Link>

            <div className="flex items-center gap-4">
                {isLoggedIn ? (
                    <>
                        <Link href="/dashboard">
                            <Button variant="ghost" size="sm">Dashboard</Button>
                        </Link>
                        <Button variant="outline" size="sm" onClick={handleLogout}>Logout</Button>
                    </>
                ) : (
                    <>
                        <Link href="/login">
                            <Button variant="ghost" size="sm">Login</Button>
                        </Link>
                        <Link href="/signup">
                            <Button variant="primary" size="sm">Get Started</Button>
                        </Link>
                    </>
                )}
            </div>
        </motion.header>
    );
}
