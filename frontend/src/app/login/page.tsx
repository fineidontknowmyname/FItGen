'use client';
import { Button } from '@/components/ui/Button';
import Header from '@/components/layout/Header';
import { useState } from 'react';
import Link from 'next/link';
import api from '@/lib/api';

export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const res = await api.post('/api/v1/users/login', { email, password });
            const data = res.data as {
                access_token: string;
                token_type: string;
                user_id: string;
                name: string;
                email: string;
            };

            // Save token and user data to localStorage
            localStorage.setItem('fitgen_token', data.access_token);
            const userData = {
                user_id: data.user_id,
                name: data.name,
                email: data.email,
            };
            // Merge with existing profile data if present
            const existing = (() => {
                try { return JSON.parse(localStorage.getItem('fitgen_user') || '{}'); }
                catch { return {}; }
            })();
            localStorage.setItem('fitgen_user', JSON.stringify({ ...existing, ...userData }));

            // Redirect to dashboard (or onboarding if first time)
            const hasOnboarded = localStorage.getItem('fitgen_onboarded');
            window.location.href = hasOnboarded ? '/dashboard' : '/onboarding';
        } catch (err: unknown) {
            const axiosErr = err as { response?: { status?: number } };
            if (axiosErr?.response?.status === 401) {
                setError('Invalid email or password');
            } else {
                setError('Login failed. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-black text-white flex flex-col">
            <Header />

            <main className="flex-1 flex items-center justify-center px-6 pt-20">
                <div className="w-full max-w-md p-8 rounded-2xl bg-zinc-900/50 border border-white/5">
                    <div className="text-center mb-8">
                        <h1 className="font-heading text-3xl font-semibold mb-2">Welcome Back</h1>
                        <p className="text-zinc-400">Sign in to continue your progress</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-zinc-300 mb-2">Email</label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full px-4 py-3 rounded-lg bg-zinc-950 border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-yellow-500/50 focus:border-yellow-500/50 transition-all"
                                placeholder="you@example.com"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-zinc-300 mb-2">Password</label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full px-4 py-3 rounded-lg bg-zinc-950 border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-yellow-500/50 focus:border-yellow-500/50 transition-all"
                                placeholder="••••••••"
                                required
                            />
                        </div>

                        {error && (
                            <p className="text-red-400 text-sm text-center">{error}</p>
                        )}

                        <Button type="submit" className="w-full" size="lg" disabled={loading}>
                            {loading ? 'Signing in…' : 'Sign In'}
                        </Button>
                    </form>

                    <p className="mt-6 text-center text-sm text-zinc-400">
                        Don&apos;t have an account?{' '}
                        <Link href="/signup" className="text-yellow-500 hover:text-yellow-400 font-medium">
                            Sign up
                        </Link>
                    </p>
                </div>
            </main>
        </div>
    );
}
