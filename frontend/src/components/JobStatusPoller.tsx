'use client';

import { useCallback } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Loader2, CheckCircle2, XCircle, Download } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useJobStatus } from '@/hooks/useJobStatus';
import { downloadPlanPdf } from '@/lib/api';
import type { JobStatus } from '@/lib/api';

// ---------------------------------------------------------------------------
// Step labels shown alongside the progress bar
// ---------------------------------------------------------------------------

const PIPELINE_STEPS = [
    { label: 'Queued', statuses: ['pending'] as JobStatus[] },
    { label: 'Fetching transcript', statuses: ['running'] as JobStatus[] },
    { label: 'Analysing content', statuses: ['running'] as JobStatus[] },
    { label: 'Building plan', statuses: ['running'] as JobStatus[] },
    { label: 'Rendering PDF', statuses: ['done', 'failed'] as JobStatus[] },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function statusToProgress(status: JobStatus | null): number {
    switch (status) {
        case 'pending': return 15;
        case 'running': return 55;
        case 'done': return 100;
        case 'failed': return 100;
        default: return 0;
    }
}

function activeStepIndex(status: JobStatus | null): number {
    switch (status) {
        case 'pending': return 0;
        case 'running': return 2;   // middle of running steps
        case 'done':
        case 'failed': return PIPELINE_STEPS.length - 1;
        default: return -1;
    }
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface Props {
    jobId: string;
    /** Called when the user clicks "Generate Another" after a terminal state. */
    onReset?: () => void;
}

export default function JobStatusPoller({ jobId, onReset }: Props) {
    const { status, error, isPolling, pollCount, stop } = useJobStatus(jobId);
    const progress = statusToProgress(status);
    const activeStep = activeStepIndex(status);
    const isTerminal = status === 'done' || status === 'failed';

    const handleDownload = useCallback(async () => {
        try {
            const blob = await downloadPlanPdf(jobId);
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `fitgen_plan_${jobId.slice(0, 8)}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
        } catch (err) {
            console.error('PDF download failed:', err);
            alert('PDF download failed. The plan may still be processing.');
        }
    }, [jobId]);

    return (
        <div className="space-y-6">
            {/* Progress bar */}
            <div className="space-y-2">
                <div className="flex justify-between text-xs text-zinc-400">
                    <motion.span
                        key={status ?? 'waiting'}
                        initial={{ opacity: 0, y: -4 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.2 }}
                    >
                        {status === 'done' ? 'Complete!' :
                            status === 'failed' ? 'Failed' :
                                isPolling ? `Processing… (${pollCount} checks)` :
                                    'Waiting…'}
                    </motion.span>
                    <span>{progress}%</span>
                </div>
                <div className="h-2 w-full bg-zinc-800 rounded-full overflow-hidden relative">
                    <motion.div
                        className={`h-full rounded-full ${status === 'failed'
                            ? 'bg-red-500'
                            : 'bg-gradient-to-r from-yellow-500 to-yellow-400'
                            }`}
                        initial={{ width: 0 }}
                        animate={{ width: `${progress}%` }}
                        transition={{ type: 'spring', stiffness: 80, damping: 20 }}
                    />
                    {!isTerminal && isPolling && (
                        <motion.div
                            className="absolute inset-y-0 left-0 w-1/3 bg-white/20 rounded-full"
                            animate={{ x: ['-100%', '300%'] }}
                            transition={{ duration: 1.6, repeat: Infinity, ease: 'linear' }}
                        />
                    )}
                </div>
            </div>

            {/* Step indicators */}
            <ol className="space-y-2">
                {PIPELINE_STEPS.map((step, i) => {
                    const done = isTerminal ? status === 'done' && i < PIPELINE_STEPS.length
                        : i < activeStep;
                    const current = !isTerminal && i === activeStep;
                    const failed = status === 'failed' && i === activeStep;

                    return (
                        <li key={step.label} className="flex items-center gap-3 text-sm">
                            <span className={`flex-shrink-0 w-5 h-5 flex items-center justify-center rounded-full text-xs font-bold ${failed ? 'bg-red-500/20 text-red-400' :
                                done ? 'bg-yellow-500/20 text-yellow-400' :
                                    current ? 'bg-zinc-700 text-white' :
                                        'bg-zinc-800 text-zinc-500'
                                }`}>
                                <AnimatePresence mode="wait" initial={false}>
                                    <motion.span
                                        key={failed ? 'failed' : done ? 'done' : current ? 'current' : 'pending'}
                                        initial={{ scale: 0, opacity: 0 }}
                                        animate={{ scale: 1, opacity: 1 }}
                                        transition={{ type: 'spring', stiffness: 500, damping: 25 }}
                                    >
                                        {failed ? '✕' :
                                            done ? '✓' :
                                                current ? '…' :
                                                    i + 1}
                                    </motion.span>
                                </AnimatePresence>
                            </span>
                            <span className={`${done ? 'text-zinc-300' : current ? 'text-white' : 'text-zinc-500'}`}>
                                {step.label}
                                {current && (
                                    <Loader2 className="inline-block w-3 h-3 ml-2 animate-spin text-yellow-500" />
                                )}
                            </span>
                        </li>
                    );
                })}
            </ol>

            {/* Terminal state actions */}
            <AnimatePresence mode="wait">
                {status === 'done' && (
                    <motion.div
                        key="done"
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3 }}
                        className="space-y-3 pt-2"
                    >
                        <div className="flex items-center gap-2 text-green-400 text-sm font-medium">
                            <motion.span
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                transition={{ type: 'spring', stiffness: 400, damping: 15, delay: 0.1 }}
                            >
                                <CheckCircle2 className="w-5 h-5" />
                            </motion.span>
                            Your plan is ready!
                        </div>
                        <Button
                            size="lg"
                            className="w-full gap-2 bg-yellow-500 hover:bg-yellow-400 text-black font-semibold"
                            onClick={handleDownload}
                        >
                            <Download className="w-4 h-4" />
                            Download PDF Plan
                        </Button>
                        {onReset && (
                            <Button variant="ghost" size="sm" className="w-full text-zinc-400" onClick={() => { stop(); onReset(); }}>
                                Generate Another
                            </Button>
                        )}
                    </motion.div>
                )}

                {status === 'failed' && (
                    <motion.div
                        key="failed"
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3 }}
                        className="space-y-3 pt-2"
                    >
                        <div className="flex items-center gap-2 text-red-400 text-sm">
                            <XCircle className="w-5 h-5" />
                            <span>{error ?? 'An error occurred during plan generation.'}</span>
                        </div>
                        {onReset && (
                            <Button variant="outline" size="sm" className="w-full" onClick={() => { stop(); onReset(); }}>
                                Try Again
                            </Button>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
