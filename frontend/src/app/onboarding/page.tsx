'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/Label';
import { Select } from '@/components/ui/Select';
import Header from '@/components/layout/Header';
import { ArrowLeft, ArrowRight, Upload, Brain, Plus, X } from 'lucide-react';
import { uploadPhotos } from '@/lib/api';
import type { UploadPhotosResult } from '@/lib/api';

const STEPS = [
    { id: 'biometrics', title: 'Biometrics', description: "Let's get to know your physical stats." },
    { id: 'activity', title: 'Activity', description: 'Tell us how active you already are.' },
    { id: 'metrics', title: 'Baseline', description: 'What can you do right now?' },
    { id: 'goals', title: 'Goals', description: 'What are you aiming for?' },
    { id: 'equipment', title: 'Equipment & Injuries', description: 'What do you have access to, and anything we should avoid?' },
    { id: 'videos', title: 'Videos', description: 'Add YouTube videos to build your plan from.' },
    { id: 'photos', title: 'Analysis', description: 'Upload photos for AI body composition analysis.' },
];

const EQUIPMENT_OPTIONS = [
    { value: 'bodyweight', label: 'Bodyweight only' },
    { value: 'dumbbell', label: 'Dumbbells' },
    { value: 'barbell', label: 'Barbell' },
    { value: 'resistance_band', label: 'Resistance bands' },
    { value: 'machine', label: 'Gym machines' },
] as const;

const INJURY_OPTIONS = [
    { value: 'shoulder', label: 'Shoulder' },
    { value: 'knee', label: 'Knee' },
    { value: 'back', label: 'Back' },
    { value: 'wrist', label: 'Wrist' },
    { value: 'ankle', label: 'Ankle' },
] as const;

interface FormData {
    age: string; weight: string; height: string; gender: 'male' | 'female';
    activityHoursPerWeek: number; activityLevel: string;
    pushups: string; situps: string; squats: string;
    goal: string; experience: string;
    youtubeUrls: string[];
    equipment: string[]; injuries: string[];
    frontPhoto: File | null; sidePhoto: File | null; backPhoto: File | null;
}

const DEFAULT: FormData = {
    age: '', weight: '', height: '', gender: 'male',
    activityHoursPerWeek: 3, activityLevel: 'moderately_active',
    pushups: '', situps: '', squats: '',
    goal: 'muscle_gain', experience: 'beginner',
    youtubeUrls: [''],
    equipment: [], injuries: [],
    frontPhoto: null, sidePhoto: null, backPhoto: null,
};

export default function OnboardingPage() {
    const [step, setStep] = useState(0);
    const [form, setForm] = useState<FormData>(DEFAULT);
    const [analyzing, setAnalyzing] = useState(false);
    const [result, setResult] = useState<UploadPhotosResult | null>(null);
    const [ageError, setAgeError] = useState('');
    const [analysisWarning, setAnalysisWarning] = useState<string | null>(null);

    const set = (f: keyof FormData, v: unknown) => setForm(p => ({ ...p, [f]: v }));

    const toggleEquipment = (value: string) => setForm(p => ({
        ...p,
        equipment: p.equipment.includes(value)
            ? p.equipment.filter(e => e !== value)
            : [...p.equipment, value],
    }));

    const toggleInjury = (value: string) => setForm(p => ({
        ...p,
        injuries: p.injuries.includes(value)
            ? p.injuries.filter(i => i !== value)
            : [...p.injuries, value],
    }));

    const addUrl = () => set('youtubeUrls', [...form.youtubeUrls, '']);
    const removeUrl = (i: number) => set('youtubeUrls', form.youtubeUrls.filter((_, x) => x !== i));
    const updateUrl = (i: number, v: string) => set('youtubeUrls', form.youtubeUrls.map((u, x) => x === i ? v : u));

    const handleNext = () => {
        if (step === 0) {
            const age = Number(form.age);
            if (!form.age || isNaN(age) || age < 15 || age > 60) {
                setAgeError('Age must be between 15 and 60.'); return;
            }
            setAgeError('');
        }
        if (step < STEPS.length - 1) { setStep(p => p + 1); }
        else {
            // ── Persist all collected data to localStorage ────────────────
            const existing = (() => {
                try { return JSON.parse(localStorage.getItem('fitgen_user') || '{}'); }
                catch { return {}; }
            })();

            const userData = {
                ...existing,
                age: Number(form.age) || existing.age,
                gender: form.gender,
                weight_kg: Number(form.weight) || existing.weight_kg,
                height_cm: Number(form.height) || existing.height_cm,
                fitness_goal: form.goal,
                experience_level: form.experience,
                pushups_max: Number(form.pushups) || 0,
                squats_max: Number(form.squats) || 0,
                // FIX 7: persist activity hours (convert weekly → daily)
                physical_activity_hours_per_day: (form.activityHoursPerWeek ?? 7) / 7,
                // FIX 8: persist equipment and injuries
                equipment_available: form.equipment ?? [],
                injuries: form.injuries ?? [],
                // Body composition from vision analysis (if completed)
                ...(result ? {
                    body_fat_pct: result.body_fat_percentage != null
                        ? `${result.body_fat_percentage}`
                        : existing.body_fat_pct,
                    v_taper: result.v_taper_ratio ?? existing.v_taper,
                    swr_category: (result as Record<string, unknown>).swr_category ?? existing.swr_category,
                } : {}),
            };

            localStorage.setItem('fitgen_user', JSON.stringify(userData));
            localStorage.setItem('fitgen_onboarded', 'true');
            window.location.href = '/dashboard';
        }
    };

    const handleAnalyze = async () => {
        if (!form.frontPhoto) { alert('Please select a front-view photo.'); return; }
        setAnalyzing(true);
        setAnalysisWarning(null);
        try {
            const heightCm = Number(form.height) || 175;
            const res = await uploadPhotos(
                form.frontPhoto,
                form.sidePhoto,
                form.backPhoto,
                heightCm,
                form.gender,
            );
            setResult(res);
            // FIX 3: warn user if pose was not detected
            if (!res.pose_detected || res.confidence === 0) {
                setAnalysisWarning(
                    'Could not detect body pose from photo. Estimated values will be used. ' +
                    'Try a clear full-body photo with good lighting and a plain background.'
                );
            }
        } catch (err: unknown) {
            const axiosErr = err as { response?: { status?: number; data?: unknown } };
            if (axiosErr?.response) {
                const status = axiosErr.response.status;
                const detail = axiosErr.response.data;
                console.error('[Vision] API error', status, detail);
                if (status === 451) {
                    alert('Consent required. Please tick the consent checkbox before uploading.');
                } else if (status === 400) {
                    alert('Invalid image — please use a JPEG/PNG/WebP file, min 200×200px, max 10MB.');
                } else {
                    alert(`Analysis failed (${status}). Check console for details.`);
                }
            } else {
                console.error('[Vision] Network error:', err);
                alert('Could not reach the analysis server — is the API running?');
            }
        } finally { setAnalyzing(false); }
    };

    const hoursLabel = (h: number) =>
        h === 0 ? 'Sedentary' : h <= 3 ? 'Lightly active' : h <= 6 ? 'Moderately active' : h <= 10 ? 'Very active' : 'Extremely active';

    return (
        <div className="min-h-screen bg-black text-white flex flex-col">
            <Header />
            <main className="flex-1 max-w-2xl mx-auto w-full px-6 py-20">
                {/* Progress */}
                <div className="mb-12">
                    <span className="text-yellow-500 font-medium text-sm block mb-1">Step {step + 1} of {STEPS.length}</span>
                    <h1 className="text-2xl font-bold">{STEPS[step].title}</h1>
                    <p className="text-zinc-400 mt-1">{STEPS[step].description}</p>
                    <div className="h-1 w-full bg-zinc-900 rounded-full overflow-hidden mt-4">
                        <motion.div className="h-full bg-yellow-500"
                            animate={{ width: `${((step + 1) / STEPS.length) * 100}%` }}
                            transition={{ duration: 0.3 }} />
                    </div>
                </div>

                <div className="bg-zinc-900/30 border border-white/5 rounded-2xl p-8">
                    <AnimatePresence mode="wait">
                        <motion.div key={step}
                            initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }} transition={{ duration: 0.2 }}>

                            {/* Step 1 — Biometrics */}
                            {step === 0 && (
                                <div className="space-y-6">
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-2">
                                            <Label>Age <span className="text-xs text-zinc-500">(15–60)</span></Label>
                                            <Input type="number" placeholder="25" min={15} max={60}
                                                value={form.age} onChange={e => { set('age', e.target.value); setAgeError(''); }} />
                                            {ageError && <p className="text-red-400 text-xs">{ageError}</p>}
                                        </div>
                                        <div className="space-y-2">
                                            <Label>Gender</Label>
                                            <Select value={form.gender} onChange={e => set('gender', e.target.value as 'male' | 'female')}>
                                                <option value="male">Male</option>
                                                <option value="female">Female</option>
                                            </Select>
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-2">
                                            <Label>Weight (kg)</Label>
                                            <Input type="number" placeholder="70" value={form.weight} onChange={e => set('weight', e.target.value)} />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>Height (cm)</Label>
                                            <Input type="number" placeholder="175" value={form.height} onChange={e => set('height', e.target.value)} />
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Step 2 — Activity */}
                            {step === 1 && (
                                <div className="space-y-6">
                                    <div className="space-y-3">
                                        <Label>Weekly training hours: <span className="text-yellow-500 font-semibold">{form.activityHoursPerWeek} hr{form.activityHoursPerWeek !== 1 ? 's' : ''}</span></Label>
                                        <input type="range" min={0} max={20} step={1}
                                            value={form.activityHoursPerWeek}
                                            onChange={e => set('activityHoursPerWeek', Number(e.target.value))}
                                            className="w-full accent-yellow-500 cursor-pointer" />
                                        <div className="flex justify-between text-xs text-zinc-500"><span>0</span><span>10</span><span>20</span></div>
                                        <p className="text-sm text-zinc-300 font-medium">{hoursLabel(form.activityHoursPerWeek)}</p>
                                    </div>
                                    <div className="space-y-2">
                                        <Label>Activity Level</Label>
                                        <Select value={form.activityLevel} onChange={e => set('activityLevel', e.target.value)}>
                                            <option value="sedentary">Sedentary</option>
                                            <option value="lightly_active">Light (1–3 days/week)</option>
                                            <option value="moderately_active">Moderate (3–5 days/week)</option>
                                            <option value="very_active">Active (6–7 days/week)</option>
                                            <option value="extra_active">Extra active</option>
                                        </Select>
                                    </div>
                                </div>
                            )}

                            {/* Step 3 — Baseline */}
                            {step === 2 && (
                                <div className="space-y-6">
                                    <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                                        <p className="text-sm text-yellow-500">Be honest — FitGen needs accurate data to build a safe plan.</p>
                                    </div>
                                    {(['pushups', 'squats', 'situps'] as const).map(k => (
                                        <div key={k} className="space-y-2">
                                            <Label>Max {k.charAt(0).toUpperCase() + k.slice(1)} (in one go)</Label>
                                            <Input type="number" placeholder="20" value={form[k]} onChange={e => set(k, e.target.value)} />
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Step 4 — Goals */}
                            {step === 3 && (
                                <div className="space-y-6">
                                    <div className="space-y-2">
                                        <Label>Primary Goal</Label>
                                        <Select value={form.goal} onChange={e => set('goal', e.target.value)}>
                                            <option value="muscle_gain">Hypertrophy (Build Muscle)</option>
                                            <option value="strength_gain">Strength (Get Stronger)</option>
                                            <option value="endurance_gain">Endurance</option>
                                            <option value="weight_loss">Weight Loss</option>
                                            <option value="flexibility_gain">Flexibility</option>
                                            <option value="general_fitness">General Fitness</option>
                                        </Select>
                                    </div>
                                    <div className="space-y-2">
                                        <Label>Experience Level</Label>
                                        <Select value={form.experience} onChange={e => set('experience', e.target.value)}>
                                            <option value="beginner">Beginner (0–1 years)</option>
                                            <option value="intermediate">Intermediate (1–3 years)</option>
                                            <option value="advanced">Advanced (3+ years)</option>
                                        </Select>
                                    </div>
                                </div>
                            )}

                            {/* Step 5 — Equipment & Injuries */}
                            {step === 4 && (
                                <div className="space-y-8">
                                    <div className="space-y-3">
                                        <Label>Available Equipment</Label>
                                        <div className="grid grid-cols-2 gap-2">
                                            {EQUIPMENT_OPTIONS.map(opt => (
                                                <label key={opt.value}
                                                    className="flex items-center gap-2 px-3 py-2 rounded-lg bg-zinc-950 border border-white/10 text-sm cursor-pointer hover:border-yellow-500/30 transition-colors">
                                                    <input type="checkbox"
                                                        checked={form.equipment.includes(opt.value)}
                                                        onChange={() => toggleEquipment(opt.value)}
                                                        className="accent-yellow-500" />
                                                    {opt.label}
                                                </label>
                                            ))}
                                        </div>
                                        <p className="text-xs text-zinc-500">Leave blank if you only train with bodyweight.</p>
                                    </div>
                                    <div className="space-y-3">
                                        <Label>Injuries or Areas to Avoid Stressing</Label>
                                        <div className="grid grid-cols-2 gap-2">
                                            {INJURY_OPTIONS.map(opt => (
                                                <label key={opt.value}
                                                    className="flex items-center gap-2 px-3 py-2 rounded-lg bg-zinc-950 border border-white/10 text-sm cursor-pointer hover:border-yellow-500/30 transition-colors">
                                                    <input type="checkbox"
                                                        checked={form.injuries.includes(opt.value)}
                                                        onChange={() => toggleInjury(opt.value)}
                                                        className="accent-yellow-500" />
                                                    {opt.label}
                                                </label>
                                            ))}
                                        </div>
                                        <p className="text-xs text-zinc-500">FitGen will filter out exercises that stress these areas.</p>
                                    </div>
                                </div>
                            )}

                            {/* Step 6 — YouTube videos */}
                            {step === 5 && (
                                <div className="space-y-4">
                                    <p className="text-sm text-zinc-400">Add YouTube workout videos. FitGen extracts exercises from captions.</p>
                                    <div className="space-y-3">
                                        {form.youtubeUrls.map((url, i) => (
                                            <div key={i} className="flex gap-2 items-center">
                                                <Input placeholder="https://www.youtube.com/watch?v=..." value={url}
                                                    onChange={e => updateUrl(i, e.target.value)} className="flex-1" />
                                                {form.youtubeUrls.length > 1 && (
                                                    <button onClick={() => removeUrl(i)} className="text-zinc-500 hover:text-red-400 transition-colors p-1">
                                                        <X className="w-4 h-4" />
                                                    </button>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                    <button onClick={addUrl} className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-yellow-500 transition-colors">
                                        <Plus className="w-3.5 h-3.5" /> Add another video
                                    </button>
                                </div>
                            )}

                            {/* Step 7 — Photos */}
                            {step === 6 && (
                                <div className="space-y-6">
                                    {([
                                        { key: 'frontPhoto' as const, label: 'Front view', required: true },
                                        { key: 'sidePhoto' as const, label: 'Side view', required: false },
                                        { key: 'backPhoto' as const, label: 'Back view', required: false },
                                    ]).map(({ key, label, required }) => (
                                        <div key={key} className="space-y-2">
                                            <Label>{label}{required && <span className="text-yellow-500 ml-1">*</span>}</Label>
                                            <div className="flex items-center gap-3">
                                                <input type="file" accept="image/jpeg,image/png,image/webp"
                                                    id={`photo-${key}`} className="hidden"
                                                    onChange={e => set(key, e.target.files?.[0] ?? null)} />
                                                <label htmlFor={`photo-${key}`}
                                                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 cursor-pointer text-sm transition-colors border border-white/5">
                                                    <Upload className="w-4 h-4" />
                                                    {form[key] ? (form[key] as File).name : 'Choose file'}
                                                </label>
                                                {form[key] && <span className="text-xs text-green-400">✓</span>}
                                            </div>
                                        </div>
                                    ))}
                                    {/* Image requirements hint */}
                                    <p className="text-xs text-zinc-500">
                                        JPG, PNG or WebP · Max 10 MB · Min 200×200 px · Full-body photo recommended
                                    </p>
                                    <Button variant="secondary" onClick={handleAnalyze}
                                        disabled={analyzing || !form.frontPhoto} className="w-full">
                                        {analyzing ? 'Analysing…' : 'Analyse Photos'}
                                    </Button>
                                    {/* FIX 3: pose-detection warning */}
                                    {analysisWarning && (
                                        <div className="flex gap-2 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg text-sm text-yellow-400">
                                            <span>⚠️</span>
                                            <p>{analysisWarning}</p>
                                        </div>
                                    )}
                                    {result && (
                                        <div className="bg-zinc-900/50 border border-yellow-500/20 rounded-xl p-6 space-y-4">
                                            <div className="flex items-center gap-2">
                                                <Brain className="w-5 h-5 text-yellow-500" />
                                                <h4 className="font-semibold">AI Analysis Results</h4>
                                            </div>
                                            <div className="grid grid-cols-2 gap-4">
                                                <div className="bg-black/40 p-3 rounded-lg">
                                                    <span className="text-xs text-zinc-500 block">Est. Body Fat</span>
                                                    <span className="text-xl font-bold">
                                                        {result.fat_pct_low != null && result.fat_pct_high != null
                                                            ? `${result.fat_pct_low}–${result.fat_pct_high}%`
                                                            : result.fat_pct_low != null
                                                                ? `~${result.fat_pct_low}%`
                                                                : '--'}
                                                    </span>
                                                </div>
                                                <div className="bg-black/40 p-3 rounded-lg">
                                                    <span className="text-xs text-zinc-500 block">V-Taper Ratio</span>
                                                    <span className="text-xl font-bold">{result.v_taper_ratio ?? '--'}</span>
                                                </div>
                                            </div>
                                            {result.posture_assessment && (
                                                <p className="text-sm"><span className="text-zinc-500">Posture: </span>{result.posture_assessment}</p>
                                            )}
                                        </div>
                                    )}
                                    <div className="flex gap-2 p-4 bg-zinc-950 rounded-lg text-sm text-zinc-400">
                                        <span>🔒</span>
                                        <p>Photos are processed privately on-device and never shared.</p>
                                    </div>
                                </div>
                            )}

                        </motion.div>
                    </AnimatePresence>

                    {/* Nav */}
                    <div className="mt-10 flex justify-between pt-6 border-t border-white/5">
                        <Button variant="ghost" onClick={() => setStep(p => p - 1)}
                            disabled={step === 0} className={step === 0 ? 'invisible' : ''}>
                            <ArrowLeft className="w-4 h-4 mr-2" /> Back
                        </Button>
                        <Button onClick={handleNext} className="w-32">
                            {step === STEPS.length - 1 ? 'Finish' : 'Next'}
                            {step !== STEPS.length - 1 && <ArrowRight className="w-4 h-4 ml-2" />}
                        </Button>
                    </div>
                </div>
            </main>
        </div>
    );
}
