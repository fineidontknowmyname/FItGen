'use client';

import { useState, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import Header from '@/components/layout/Header';
import { Button } from '@/components/ui/Button';
import { Label } from '@/components/ui/Label';
import { submitPlanJob } from '@/lib/api';
import api from '@/lib/api';
import JobStatusPoller from '@/components/JobStatusPoller';
import { Loader2, FileDown, Youtube, Plus, X, Moon, Sun } from 'lucide-react';
import {
    type FitGenUser,
    humanizeGoal,
    buildPlanRequest,
} from '@/lib/profilePayload';

const STORAGE_KEY = 'fitgen_user';

// ---------------------------------------------------------------------------
// Dashboard page
// ---------------------------------------------------------------------------

export default function DashboardPage() {
    const router = useRouter();
    const [workoutUrls, setWorkoutUrls] = useState<string[]>(['']);
    const [dietUrls, setDietUrls] = useState<string[]>(['']);
    const [submitting, setSubmitting] = useState(false);
    const [activeJobId, setActiveJobId] = useState<string | null>(null);

    // User state
    const [user, setUser] = useState<FitGenUser | null>(null);
    const [loading, setLoading] = useState(true);

    // Dark mode state
    const [darkMode, setDarkMode] = useState(true);

    // ── Load user data on mount ──────────────────────────────────────────
    useEffect(() => {
        if (!localStorage.getItem('fitgen_token')) {
            router.push('/login');
            return;
        }

        const savedTheme = localStorage.getItem('fitgen_theme');
        if (savedTheme === 'light') setDarkMode(false);

        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored && stored !== 'true') {
            try {
                setUser(JSON.parse(stored));
            } catch {
                // corrupted data — fall through to API
            }
        }

        // Always attempt to enrich from API (silent fail is OK)
        api.get('/users/me')
            .then(res => {
                const merged = { ...(stored && stored !== 'true' ? JSON.parse(stored) : {}), ...res.data };
                setUser(merged);
                localStorage.setItem(STORAGE_KEY, JSON.stringify(merged));
            })
            .catch(() => {
                // API not available — use localStorage data only
            })
            .finally(() => setLoading(false));
    }, []);

    // ── Dark mode toggle ─────────────────────────────────────────────────
    const toggleDarkMode = () => {
        setDarkMode(prev => {
            const next = !prev;
            localStorage.setItem('fitgen_theme', next ? 'dark' : 'light');
            return next;
        });
    };

    // Multi-URL helpers
    const addUrl = (setter: React.Dispatch<React.SetStateAction<string[]>>) =>
        setter(prev => [...prev, '']);
    const removeUrl = (setter: React.Dispatch<React.SetStateAction<string[]>>, i: number) =>
        setter(prev => prev.filter((_, idx) => idx !== i));
    const updateUrl = (setter: React.Dispatch<React.SetStateAction<string[]>>, i: number, val: string) =>
        setter(prev => prev.map((u, idx) => (idx === i ? val : u)));

    const cleanUrls = (urlList: string[]) =>
        urlList.map(u => u.trim()).filter(u => u.length > 0);

    const handleGenerate = useCallback(async () => {
        setSubmitting(true);
        try {
            const job = await submitPlanJob({
                ...buildPlanRequest(user),
                workout_youtube_urls: cleanUrls(workoutUrls),
                diet_youtube_urls: cleanUrls(dietUrls),
                youtube_urls: [
                    ...cleanUrls(workoutUrls),
                    ...cleanUrls(dietUrls)
                ],   // empty array → backend uses Mode A
            });
            setActiveJobId(job.job_id);
            router.push(`/status/${job.job_id}`);
        } catch (err) {
            // Log the full API error detail so the 422 body is visible in console
            const axiosErr = err as { response?: { status?: number; data?: unknown } };
            if (axiosErr?.response) {
                console.error('API error', axiosErr.response.status, axiosErr.response.data);
                alert(`Plan generation failed (${axiosErr.response.status}). Check console for details.`);
            } else {
                console.error('Network error:', err);
                alert('Network error — is the API running at localhost:8000?');
            }
        } finally {
            setSubmitting(false);
        }
    }, [workoutUrls, dietUrls, router, user]);

    // ── Derived display values ───────────────────────────────────────────
    const displayName = user?.name ?? user?.email ?? 'User';
    const displayGoal = humanizeGoal(
        user?.fitness_goal ?? (Array.isArray(user?.goals) ? user?.goals?.[0] : user?.goals as string | undefined)
    );
    const displayLevel = humanizeGoal(user?.experience_level ?? user?.fitness_level);
    const displayWeight = user?.weight_kg ? `${user.weight_kg} kg` : '— kg';
    const displayHeight = user?.height_cm ? `${user.height_cm} cm` : '— cm';
    const displayFat = user?.body_fat_pct ? `${user.body_fat_pct}%` : '— %';
    const displayVTaper = user?.v_taper ?? user?.swr_category ?? '—';
    const pushups = user?.pushups_max ?? user?.pushup_count ?? 0;
    const squats = user?.squats_max ?? user?.squat_count ?? 0;

    // ── Theme classes ────────────────────────────────────────────────────
    const bg = darkMode ? 'bg-black' : 'bg-gray-50';
    const text = darkMode ? 'text-white' : 'text-gray-900';
    const textMuted = darkMode ? 'text-zinc-400' : 'text-gray-500';
    const textDim = darkMode ? 'text-zinc-500' : 'text-gray-400';
    const cardBg = darkMode ? 'bg-zinc-900/30' : 'bg-white';
    const cardBorder = darkMode ? 'border-white/5' : 'border-gray-200';
    const heroCard = darkMode
        ? 'bg-gradient-to-br from-zinc-900 to-black border-white/10'
        : 'bg-gradient-to-br from-white to-gray-50 border-gray-200 shadow-lg';
    const inputBg = darkMode ? '' : 'bg-white border-gray-300 text-gray-900';
    const barBg = darkMode ? 'bg-zinc-800' : 'bg-gray-200';
    const dividerBg = darkMode ? 'bg-white/10' : 'bg-gray-200';
    const dashedBorder = darkMode ? 'border-zinc-800' : 'border-gray-300';
    const headerBg = darkMode ? 'bg-zinc-900/50' : 'bg-white shadow-sm';

    return (
        <div className={`min-h-screen ${bg} ${text} selection:bg-yellow-500/30 transition-colors duration-300`}>
            <Header />

            <main className="pt-24 px-6 max-w-7xl mx-auto pb-20">
                {/* Title row */}
                <div className="flex flex-col md:flex-row gap-8 items-start justify-between mb-12">
                    <div>
                        <h1 className="font-heading text-3xl font-semibold mb-2">My Dashboard</h1>
                        <p className={textMuted}>
                            {loading ? (
                                <span className={`inline-block w-48 h-5 ${barBg} rounded animate-pulse`} />
                            ) : (
                                `Welcome back, ${displayName}`
                            )}
                        </p>
                    </div>
                    <div className="flex items-center gap-4">
                        {/* Dark mode toggle */}
                        <button
                            onClick={toggleDarkMode}
                            className={`p-2.5 rounded-xl border transition-all duration-200 ${darkMode
                                ? 'bg-zinc-900/50 border-white/10 text-yellow-500 hover:bg-zinc-800'
                                : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-100 shadow-sm'
                                }`}
                            title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
                        >
                            {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                        </button>

                        <div className={`${headerBg} p-4 rounded-xl border ${cardBorder} flex gap-6 text-sm`}>
                            {loading ? (
                                <>
                                    <div className={`w-28 h-10 ${barBg} rounded animate-pulse`} />
                                    <div className={`w-px ${dividerBg}`} />
                                    <div className={`w-24 h-10 ${barBg} rounded animate-pulse`} />
                                </>
                            ) : (
                                <>
                                    <div>
                                        <span className={`block ${textDim} mb-1`}>Current Goal</span>
                                        <span className="font-semibold text-yellow-500">{displayGoal}</span>
                                    </div>
                                    <div className={`w-px ${dividerBg}`} />
                                    <div>
                                        <span className={`block ${textDim} mb-1`}>Level</span>
                                        <span className="font-semibold">{displayLevel}</span>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                </div>

                <div className="grid md:grid-cols-3 gap-8">
                    {/* Main action card */}
                    <div className="md:col-span-2 space-y-8">
                        <section className={`p-8 rounded-2xl ${heroCard} border relative overflow-hidden group`}>
                            <div className="absolute top-0 right-0 w-64 h-64 bg-yellow-500/5 rounded-full blur-[80px] -z-10 group-hover:bg-yellow-500/10 transition-all duration-500" />

                            <div className="mb-6">
                                <div className="w-12 h-12 bg-yellow-500/20 rounded-xl flex items-center justify-center mb-4 text-yellow-500">
                                    <FileDown className="w-6 h-6" />
                                </div>
                                <h2 className="text-2xl font-bold mb-2">Generate New Plan</h2>
                                <p className={`${textMuted} max-w-lg mb-4`}>
                                    Create a fully customised 4-week PDF workout routine and meal plan. Add YouTube
                                    videos below to blend specific training styles or dietary principles.
                                </p>
                                <p className={`text-xs ${textDim}`}>
                                    <span className="text-yellow-500/80 font-medium">Optional</span> — leave empty to generate a standard plan from your profile.
                                </p>
                            </div>

                            {/* Dual URL inputs */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 max-w-4xl">
                                {/* Workout Videos Section */}
                                <div className="space-y-4">
                                    <div>
                                        <Label className="text-base flex items-center gap-2">💪 Workout Videos</Label>
                                        <p className={`text-xs ${textMuted} mt-1`}>YouTube links for exercise & training</p>
                                    </div>
                                    <div className="space-y-3">
                                        {workoutUrls.map((url, i) => (
                                            <div key={i} className="flex gap-2 items-center">
                                                <div className="relative flex-1">
                                                    <div className={`absolute left-3 top-1/2 -translate-y-1/2 ${textDim}`}>
                                                        <Youtube className="w-4 h-4 text-red-500" />
                                                    </div>
                                                    <input
                                                        type="url"
                                                        value={url}
                                                        onChange={e => updateUrl(setWorkoutUrls, i, e.target.value)}
                                                        placeholder="https://youtube.com/watch?v=..."
                                                        className={`w-full pl-10 pr-3 py-2 rounded-lg ${inputBg} border ${cardBorder} focus:outline-none focus:ring-2 focus:ring-yellow-500/50 transition-all text-sm`}
                                                    />
                                                </div>
                                                <button
                                                    onClick={() => removeUrl(setWorkoutUrls, i)}
                                                    className="text-zinc-500 hover:text-red-400 transition-colors p-1"
                                                    title="Remove URL"
                                                >
                                                    <X className="w-4 h-4" />
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                    <button
                                        onClick={() => addUrl(setWorkoutUrls)}
                                        className={`flex items-center gap-1.5 text-xs ${textMuted} hover:text-yellow-500 transition-colors mt-2`}
                                    >
                                        <Plus className="w-3.5 h-3.5" /> Add Video
                                    </button>
                                </div>

                                {/* Diet Videos Section */}
                                <div className="space-y-4">
                                    <div>
                                        <Label className="text-base flex items-center gap-2">🥗 Diet & Nutrition Videos</Label>
                                        <p className={`text-xs ${textMuted} mt-1`}>YouTube links for meal plans & nutrition</p>
                                    </div>
                                    <div className="space-y-3">
                                        {dietUrls.map((url, i) => (
                                            <div key={i} className="flex gap-2 items-center">
                                                <div className="relative flex-1">
                                                    <div className={`absolute left-3 top-1/2 -translate-y-1/2 ${textDim}`}>
                                                        <Youtube className="w-4 h-4 text-red-500" />
                                                    </div>
                                                    <input
                                                        type="url"
                                                        value={url}
                                                        onChange={e => updateUrl(setDietUrls, i, e.target.value)}
                                                        placeholder="https://youtube.com/watch?v=..."
                                                        className={`w-full pl-10 pr-3 py-2 rounded-lg ${inputBg} border ${cardBorder} focus:outline-none focus:ring-2 focus:ring-yellow-500/50 transition-all text-sm`}
                                                    />
                                                </div>
                                                <button
                                                    onClick={() => removeUrl(setDietUrls, i)}
                                                    className="text-zinc-500 hover:text-red-400 transition-colors p-1"
                                                    title="Remove URL"
                                                >
                                                    <X className="w-4 h-4" />
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                    <button
                                        onClick={() => addUrl(setDietUrls)}
                                        className={`flex items-center gap-1.5 text-xs ${textMuted} hover:text-yellow-500 transition-colors mt-2`}
                                    >
                                        <Plus className="w-3.5 h-3.5" /> Add Video
                                    </button>
                                </div>
                            </div>

                            <div className="space-y-4 max-w-xl">
                                <Button
                                    size="lg"
                                    className="w-full sm:w-auto min-w-[200px]"
                                    onClick={handleGenerate}
                                    disabled={submitting}
                                >
                                    {submitting ? (
                                        <>
                                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                            Queuing job…
                                        </>
                                    ) : (
                                        'Generate Plan PDF'
                                    )}
                                </Button>
                            </div>

                            {/* Inline poller (appears briefly before navigation) */}
                            {activeJobId && (
                                <div className={`mt-8 p-6 ${darkMode ? 'bg-black/30' : 'bg-gray-50'} rounded-xl border ${cardBorder}`}>
                                    <JobStatusPoller
                                        jobId={activeJobId}
                                        onReset={() => { setActiveJobId(null); setWorkoutUrls(['']); setDietUrls(['']); }}
                                    />
                                </div>
                            )}
                        </section>

                        {/* Recent Activity */}
                        <section className={`p-6 rounded-2xl ${cardBg} border ${cardBorder}`}>
                            <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
                            <div className={`flex items-center justify-center h-32 ${textDim} text-sm italic border-dashed border ${dashedBorder} rounded-lg`}>
                                No recent workouts logged.
                            </div>
                        </section>
                    </div>

                    {/* Stats sidebar */}
                    <aside className="space-y-6">
                        <div className={`p-6 rounded-2xl ${cardBg} border ${cardBorder}`}>
                            <h3 className={`font-semibold mb-4 text-sm uppercase tracking-wider ${textDim}`}>My Stats</h3>
                            <div className="space-y-4">
                                {loading ? (
                                    <>
                                        <SkeletonRow dark={darkMode} />
                                        <SkeletonRow dark={darkMode} />
                                        <SkeletonRow dark={darkMode} />
                                        <SkeletonRow dark={darkMode} />
                                    </>
                                ) : (
                                    <>
                                        <StatRow label="Weight" value={displayWeight} muted={textMuted} />
                                        <StatRow label="Height" value={displayHeight} muted={textMuted} />
                                        <StatRow label="Body Fat" value={displayFat} muted={textMuted} />
                                        <StatRow label="V-Taper" value={String(displayVTaper)} muted={textMuted} />
                                    </>
                                )}
                            </div>
                            <Button
                                variant="outline"
                                size="sm"
                                className="w-full mt-6 text-xs"
                                onClick={() => router.push('/onboarding')}
                            >
                                Update Biometrics
                            </Button>
                        </div>

                        <div className={`p-6 rounded-2xl ${cardBg} border ${cardBorder}`}>
                            <h3 className={`font-semibold mb-4 text-sm uppercase tracking-wider ${textDim}`}>Progression</h3>
                            <div className="space-y-4">
                                {loading ? (
                                    <>
                                        <SkeletonBar dark={darkMode} />
                                        <SkeletonBar dark={darkMode} />
                                    </>
                                ) : (
                                    <>
                                        <ProgressBar label="Pushups" current={pushups} max={50} barBg={barBg} />
                                        <ProgressBar label="Squats" current={squats} max={100} barBg={barBg} />
                                    </>
                                )}
                            </div>
                        </div>
                    </aside>
                </div>
            </main>
        </div>
    );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function StatRow({ label, value, muted }: { label: string; value: string; muted: string }) {
    return (
        <div className="flex justify-between items-center text-sm">
            <span className={muted}>{label}</span>
            <span className="font-heading font-semibold text-base">{value}</span>
        </div>
    );
}

function ProgressBar({ label, current, max, barBg }: { label: string; current: number; max: number; barBg: string }) {
    const pct = Math.min(100, (current / max) * 100);
    return (
        <div>
            <div className="flex justify-between text-xs mb-1">
                <span>{label}</span>
                <span className="opacity-60">{current}/{max}</span>
            </div>
            <div className={`h-1.5 ${barBg} rounded-full overflow-hidden`}>
                <motion.div
                    className="h-full bg-yellow-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${pct}%` }}
                    transition={{ type: 'spring', stiffness: 60, damping: 15, delay: 0.1 }}
                />
            </div>
        </div>
    );
}

function SkeletonRow({ dark }: { dark: boolean }) {
    const bg = dark ? 'bg-zinc-800' : 'bg-gray-200';
    return (
        <div className="flex justify-between items-center">
            <div className={`w-16 h-4 ${bg} rounded animate-pulse`} />
            <div className={`w-12 h-4 ${bg} rounded animate-pulse`} />
        </div>
    );
}

function SkeletonBar({ dark }: { dark: boolean }) {
    const bg = dark ? 'bg-zinc-800' : 'bg-gray-200';
    return (
        <div>
            <div className="flex justify-between mb-1">
                <div className={`w-14 h-3 ${bg} rounded animate-pulse`} />
                <div className={`w-8 h-3 ${bg} rounded animate-pulse`} />
            </div>
            <div className={`h-1.5 ${bg} rounded-full animate-pulse`} />
        </div>
    );
}
