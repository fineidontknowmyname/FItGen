'use client';

import { useState, useEffect, useCallback } from 'react';
import { Activity, X, RefreshCw } from 'lucide-react';

interface ServiceState {
    name: string;
    status: 'online' | 'offline' | 'degraded' | 'checking';
    detail: string;
    latency_ms: number | null;
    last_checked: Date | null;
}

const SERVICES = [
    { name: 'Backend', url: '/health' },
    { name: 'Database', url: '/health/db' },
    { name: 'Redis', url: '/health/redis' },
    { name: 'Celery', url: '/health/celery' },
    { name: 'Ollama', url: 'http://localhost:11434/api/tags', external: true },
];

export default function ServiceStatus() {
    const [isOpen, setIsOpen] = useState(false);
    const [services, setServices] = useState<ServiceState[]>(
        SERVICES.map(s => ({
            name: s.name,
            status: 'checking',
            detail: 'Initializing...',
            latency_ms: null,
            last_checked: null,
        }))
    );
    const [isRefreshing, setIsRefreshing] = useState(true);

    const checkServices = useCallback(async () => {
        setIsRefreshing(true);
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';

        const updatedServices = await Promise.all(
            SERVICES.map(async (service): Promise<ServiceState> => {
                const url = service.external ? service.url : `${baseUrl}${service.url}`;
                const start = Date.now();

                try {
                    const res = await fetch(url, { method: 'GET', cache: 'no-store' });
                    const latency = Date.now() - start;

                    if (res.ok) {
                        return {
                            name: service.name,
                            status: latency > 2000 ? 'degraded' : 'online',
                            detail: latency > 2000 ? 'High latency' : 'Operational',
                            latency_ms: latency,
                            last_checked: new Date()
                        };
                    } else {
                        return {
                            name: service.name,
                            status: 'offline',
                            detail: `HTTP ${res.status}`,
                            latency_ms: latency,
                            last_checked: new Date()
                        };
                    }
                } catch {
                    return {
                        name: service.name,
                        status: 'offline',
                        detail: 'Unreachable',
                        latency_ms: null,
                        last_checked: new Date()
                    };
                }
            })
        );

        setServices(updatedServices);
        setIsRefreshing(false);
    }, []);

    useEffect(() => {
        const run = async () => { await checkServices(); };
        run();
        const interval = setInterval(() => { run(); }, 30000); // 30s
        return () => clearInterval(interval);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // Derived states
    const offlineCount = services.filter(s => s.status === 'offline').length;
    const degradedCount = services.filter(s => s.status === 'degraded').length;
    const isChecking = services.some(s => s.status === 'checking');

    let overallColor = 'bg-stone-500 text-white'; // default/unknown
    let pulseClass = '';

    if (!isChecking) {
        if (offlineCount > 0) {
            overallColor = 'bg-red-500 text-white';
            pulseClass = 'animate-pulse';
        } else if (degradedCount > 0) {
            overallColor = 'bg-yellow-500 text-yellow-950';
        } else {
            overallColor = 'bg-emerald-500 text-white';
        }
    }

    const getStatusColor = (status: ServiceState['status']) => {
        switch (status) {
            case 'online': return 'bg-emerald-500';
            case 'offline': return 'bg-red-500';
            case 'degraded': return 'bg-yellow-500';
            default: return 'bg-stone-400';
        }
    };

    return (
        <div className="fixed bottom-4 right-4 z-50 font-sans">
            {/* Panel */}
            {isOpen && (
                <div className="absolute bottom-16 right-0 w-80 bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-2xl p-4 mb-2 backdrop-blur-xl bg-opacity-95 dark:bg-opacity-95 text-sm">
                    <div className="flex justify-between items-center mb-4 pb-2 border-b border-zinc-100 dark:border-zinc-800">
                        <h3 className="font-semibold flex items-center gap-2 dark:text-zinc-100">
                            <Activity className="w-4 h-4" /> System Status
                        </h3>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={checkServices}
                                disabled={isRefreshing}
                                className={`p-1.5 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-900 transition-colors ${isRefreshing ? 'opacity-50' : ''}`}
                                title="Refresh"
                            >
                                <RefreshCw className={`w-4 h-4 dark:text-zinc-400 ${isRefreshing ? 'animate-spin' : ''}`} />
                            </button>
                            <button
                                onClick={() => setIsOpen(false)}
                                className="p-1.5 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-900 transition-colors"
                            >
                                <X className="w-4 h-4 dark:text-zinc-400" />
                            </button>
                        </div>
                    </div>

                    <div className="space-y-3">
                        {services.map((service, idx) => (
                            <div key={idx} className="flex items-center justify-between group">
                                <div className="flex items-center gap-3">
                                    <div className={`w-2.5 h-2.5 rounded-full ${getStatusColor(service.status)}`} />
                                    <div>
                                        <p className="font-medium text-zinc-900 dark:text-zinc-200 leading-tight">{service.name}</p>
                                        <p className="text-xs text-zinc-500 dark:text-zinc-500">{service.detail}</p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    {service.status !== 'checking' && service.latency_ms !== null ? (
                                        <p className="text-xs font-mono text-zinc-500 dark:text-zinc-400">{service.latency_ms}ms</p>
                                    ) : (
                                        <p className="text-xs text-zinc-400">--</p>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Floating Toggle Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-full shadow-lg transition-all hover:scale-105 active:scale-95 border border-black/5 dark:border-white/5 font-medium text-sm ${overallColor}`}
            >
                <div className="flex items-center gap-1.5">
                    <span className={pulseClass}>⚡</span>
                    <span className="hidden sm:inline">Services</span>
                </div>
                {offlineCount > 0 && (
                    <span className="flex items-center justify-center bg-white/20 px-1.5 py-0.5 rounded-md text-xs font-bold leading-none">
                        🔴 {offlineCount}
                    </span>
                )}
            </button>
        </div>
    );
}
