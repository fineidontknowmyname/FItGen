import axios from 'axios';

// ── Local Storage Migration (koda -> fitgen) ──────────────────────────────
if (typeof window !== 'undefined') {
    const oldUser = localStorage.getItem('koda_user');
    if (oldUser && !localStorage.getItem('fitgen_user')) {
        localStorage.setItem('fitgen_user', oldUser);
        localStorage.removeItem('koda_user');
    }

    const oldToken = localStorage.getItem('koda_token');
    if (oldToken && !localStorage.getItem('fitgen_token')) {
        localStorage.setItem('fitgen_token', oldToken);
        localStorage.removeItem('koda_token');
    }

    const oldOnboarded = localStorage.getItem('koda_onboarded');
    if (oldOnboarded && !localStorage.getItem('fitgen_onboarded')) {
        localStorage.setItem('fitgen_onboarded', oldOnboarded);
        localStorage.removeItem('koda_onboarded');
    }

    const oldTheme = localStorage.getItem('koda_theme');
    if (oldTheme && !localStorage.getItem('fitgen_theme')) {
        localStorage.setItem('fitgen_theme', oldTheme);
        localStorage.removeItem('koda_theme');
    }
}

// ---------------------------------------------------------------------------
// Axios instance
// ---------------------------------------------------------------------------

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
    if (typeof window !== 'undefined') {
        const token = localStorage.getItem('fitgen_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
    }
    return config;
});

api.interceptors.response.use(
    (res) => res,
    (err) => {
        if (typeof window !== 'undefined' && axios.isAxiosError(err) && err.response?.status === 401) {
            localStorage.removeItem('fitgen_token');
            localStorage.removeItem('fitgen_user');
            localStorage.removeItem('fitgen_onboarded');
        }
        return Promise.reject(err);
    }
);

export default api;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type JobStatus = 'pending' | 'running' | 'done' | 'failed';

export interface JobResponse {
    job_id: string;
    status: JobStatus;
    message?: string;
}

export interface JobStatusResponse {
    job_id: string;
    status: JobStatus;
    result?: Record<string, unknown> | null;
    error?: string | null;
}

export interface PlanJobPayload {
    user_profile: Record<string, unknown>;
    workout_youtube_urls?: string[];
    diet_youtube_urls?: string[];
    youtube_urls: string[];
    transcript_text?: string;
}

export interface UploadPhotosResult {
    body_fat_percentage?: number | null;
    v_taper_ratio?: number | null;
    posture_assessment?: string | null;
    is_valid_person?: boolean;
    pose_detected?: boolean;
    confidence?: number;
    [key: string]: unknown;
}

// ---------------------------------------------------------------------------
// Plan job — async Celery dispatch
// ---------------------------------------------------------------------------

export async function submitPlanJob(payload: PlanJobPayload): Promise<JobResponse> {
    try {
        const res = await api.post<JobResponse>('/api/v1/plans/generate', payload);
        return res.data;
    } catch (err) {
        if (axios.isAxiosError(err)) {
            console.error(
                '[submitPlanJob] API error',
                err.response?.status,
                err.response?.data,
                '\nPayload sent:', JSON.stringify(payload, null, 2),
            );
        } else {
            console.error('[submitPlanJob] Network error — is the backend running at', api.defaults.baseURL, err);
        }
        throw err;
    }
}

export async function pollJobStatus(jobId: string): Promise<JobStatusResponse> {
    const res = await api.get<JobStatusResponse>(`/api/v1/plans/job/${jobId}`);
    return res.data;
}

export async function downloadPlanPdf(jobId: string): Promise<Blob> {
    const res = await api.get(`/api/v1/plans/job/${jobId}/pdf`, { responseType: 'blob' });
    return res.data as Blob;
}

// ---------------------------------------------------------------------------
// Vision — 3-photo body composition upload
// ---------------------------------------------------------------------------

export async function uploadPhotos(
    front: File,
    side?: File | null,
    back?: File | null,
    heightCm: number = 175,
    gender: string = 'male',
): Promise<UploadPhotosResult> {
    const form = new FormData();
    form.append('front', front);
    if (side) form.append('side', side);
    if (back) form.append('back', back);
    form.append('consent', 'true');
    form.append('user_height_cm', String(heightCm));
    form.append('gender', gender);

    // Create a separate axios instance without the default Content-Type
    // so axios can set multipart/form-data with the correct boundary automatically
    const res = await axios.post<UploadPhotosResult>(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/vision/analyze-body`,
        form,
        {
            headers: { 'X-Vision-Consent': 'true' },
        }
    );
    return res.data;
}