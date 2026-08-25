export interface FitGenUser {
    id?: number;
    name?: string;
    email?: string;
    age?: number;
    gender?: string;
    weight_kg?: number;
    height_cm?: number;
    goals?: string | string[];
    fitness_goal?: string;
    fitness_level?: string;
    experience_level?: string;
    body_fat_pct?: string | number | null;
    v_taper?: string | number | null;
    pushups_max?: number;
    squats_max?: number;
    pushup_count?: number;
    squat_count?: number;
    swr_category?: string | null;
    equipment_available?: string[];
    injuries?: string[];
    physical_activity_hours_per_day?: number;
    body_composition?: Record<string, unknown> | null;
}

const GOAL_MAP: Record<string, string> = {
    hypertrophy: 'muscle_gain',
    strength: 'strength_gain',
    endurance: 'endurance_gain',
    flexibility: 'flexibility_gain',
    general: 'general_fitness',
    weight_loss: 'weight_loss',
    muscle_gain: 'muscle_gain',
    strength_gain: 'strength_gain',
    endurance_gain: 'endurance_gain',
};

export function mapGoal(goal: string): string {
    return GOAL_MAP[goal] ?? 'general_fitness';
}

// Valid enum values from backend schemas/common.py
const VALID_EQUIPMENT = ['bodyweight', 'dumbbell', 'barbell', 'resistance_band', 'machine'] as const;
const VALID_INJURIES = ['shoulder', 'knee', 'back', 'wrist', 'ankle', 'none'] as const;

export function sanitizeEquipment(list: string[] | undefined): string[] {
    if (!list || list.length === 0) return ['bodyweight'];
    const valid = list.filter(e => (VALID_EQUIPMENT as readonly string[]).includes(e));
    return valid.length > 0 ? valid : ['bodyweight'];
}

export function sanitizeInjuries(list: string[] | undefined): string[] {
    if (!list || list.length === 0) return [];
    return list.filter(e => (VALID_INJURIES as readonly string[]).includes(e));
}

export function humanizeGoal(goal: string | undefined | null): string {
    if (!goal) return '—';
    return goal
        .replace(/_/g, ' ')
        .replace(/\b\w/g, c => c.toUpperCase());
}

export function buildProfilePayload(user: FitGenUser | null) {
    if (!user) {
        return {
            biometrics: { age: 25, weight_kg: 70, height_cm: 175, gender: 'male' },
            metrics: { pushup_count: 0, situp_count: 0, squat_count: 0 },
            injuries: [],
            equipment: ['bodyweight'],
            experience_level: 'beginner',
            fitness_goal: 'general_fitness',
        };
    }
    return {
        biometrics: {
            age: user.age ?? 25,
            weight_kg: user.weight_kg ?? 70,
            height_cm: user.height_cm ?? 175,
            gender: user.gender ?? 'male',
        },
        metrics: {
            pushup_count: user.pushups_max ?? user.pushup_count ?? 0,
            situp_count: 0,
            squat_count: user.squats_max ?? user.squat_count ?? 0,
        },
        physical_activity: {
            physical_activity_hours_per_day: user.physical_activity_hours_per_day ?? 1.0,
        },
        injuries: sanitizeInjuries(user.injuries),
        equipment_available: sanitizeEquipment(user.equipment_available),
        experience_level: user.experience_level ?? user.fitness_level ?? 'beginner',
        fitness_goal: mapGoal(user.fitness_goal ?? (Array.isArray(user.goals) ? user.goals[0] : user.goals) ?? 'general_fitness')
    };
}

export function buildPlanRequest(user: FitGenUser | null) {
    return {
        user_profile: buildProfilePayload(user),
        body_composition: user?.body_composition ?? null,
    };
}
