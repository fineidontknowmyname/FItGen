'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import Header from '@/components/layout/Header';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

// Age must be 15–60 and gender must be male|female to match the backend UserMetrics schema

export default function SignupPage() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [age, setAge] = useState('');
    const [gender, setGender] = useState<'male' | 'female'>('male');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const router = useRouter();

    const validate = (): string => {
        const a = Number(age);
        if (!age || isNaN(a) || a < 15 || a > 60) return 'Age must be between 15 and 60.';
        if (!name.trim()) return 'Full name is required.';
        if (!email.includes('@')) return 'Please enter a valid email.';
        if (password.length < 8) return 'Password must be at least 8 characters.';
        return '';
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const err = validate();
        if (err) { setError(err); return; }
        setError('');
        setLoading(true);

        try {
            await api.post('/users/', {
                name,
                email,
                password,
                age: Number(age),
                gender,
                height_cm: 175,
                weight_kg: 70,
                fitness_level: 'beginner',
                goals: ['general_fitness'],
            });

            const loginRes = await api.post('/users/login', { email, password });
            const loginData = loginRes.data as {
                access_token: string;
                user_id: string;
                name: string;
                email: string;
            };

            localStorage.setItem('fitgen_token', loginData.access_token);
            localStorage.setItem('fitgen_user', JSON.stringify({
                user_id: loginData.user_id,
                name: loginData.name,
                email: loginData.email,
                gender,
                age,
            }));
            router.push('/onboarding');
        } catch (err) {
            console.error('Signup error:', err);
            const axiosErr = err as { response?: { status?: number } };
            if (axiosErr?.response?.status === 409) {
                setError('An account with this email already exists.');
            } else {
                setError('Signup failed — please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    const inputCls = 'w-full px-4 py-3 rounded-lg bg-zinc-950 border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-yellow-500/50 focus:border-yellow-500/50 transition-all';
    const labelCls = 'block text-sm font-medium text-zinc-300 mb-2';

    return (
        <div className="min-h-screen bg-black text-white flex flex-col">
            <Header />

            <main className="flex-1 flex items-center justify-center px-6 pt-20">
                <div className="w-full max-w-md p-8 rounded-2xl bg-zinc-900/50 border border-white/5">
                    <div className="text-center mb-8">
                        <h1 className="text-3xl font-bold mb-2">Create Account</h1>
                        <p className="text-zinc-400">Join the fitness revolution</p>
                    </div>

                    {error && (
                        <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-5">
                        {/* Name */}
                        <div>
                            <label className={labelCls}>Full Name</label>
                            <input type="text" value={name} onChange={e => setName(e.target.value)}
                                className={inputCls} placeholder="John Doe" required />
                        </div>

                        {/* Email */}
                        <div>
                            <label className={labelCls}>Email</label>
                            <input type="email" value={email} onChange={e => setEmail(e.target.value)}
                                className={inputCls} placeholder="you@example.com" required />
                        </div>

                        {/* Password */}
                        <div>
                            <label className={labelCls}>Password</label>
                            <input type="password" value={password} onChange={e => setPassword(e.target.value)}
                                className={inputCls} placeholder="••••••••" minLength={8} required />
                            <p className="text-xs text-zinc-600 mt-1">Minimum 8 characters</p>
                        </div>

                        {/* Age + Gender in a grid */}
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className={labelCls}>
                                    Age <span className="text-zinc-500 text-xs">(15–60)</span>
                                </label>
                                <input type="number" value={age} min={15} max={60}
                                    onChange={e => { setAge(e.target.value); setError(''); }}
                                    className={inputCls} placeholder="25" required />
                            </div>
                            <div>
                                <label className={labelCls}>Gender</label>
                                <select value={gender} onChange={e => setGender(e.target.value as 'male' | 'female')}
                                    className={inputCls + ' cursor-pointer'}>
                                    <option value="male">Male</option>
                                    <option value="female">Female</option>
                                </select>
                            </div>
                        </div>

                        <Button type="submit" className="w-full" size="lg" disabled={loading}>
                            {loading ? 'Creating account…' : 'Create Account'}
                        </Button>
                    </form>

                    <p className="mt-6 text-center text-sm text-zinc-400">
                        Already have an account?{' '}
                        <Link href="/login" className="text-yellow-500 hover:text-yellow-400 font-medium">
                            Log in
                        </Link>
                    </p>
                </div>
            </main>
        </div>
    );
}
