import { describe, expect, it } from 'vitest';
import {
    buildProfilePayload,
    buildPlanRequest,
    mapGoal,
    sanitizeEquipment,
    sanitizeInjuries,
    humanizeGoal,
    type FitGenUser,
} from './profilePayload';

describe('buildProfilePayload', () => {
    it('forwards equipment_available and injuries collected during onboarding', () => {
        const user: FitGenUser = {
            age: 30,
            gender: 'male',
            weight_kg: 82,
            height_cm: 180,
            equipment_available: ['dumbbell', 'barbell'],
            injuries: ['knee'],
        };

        const payload = buildProfilePayload(user);

        expect(payload.equipment_available).toEqual(['dumbbell', 'barbell']);
        expect(payload.injuries).toEqual(['knee']);
    });

    it('forwards physical_activity_hours_per_day collected during onboarding', () => {
        const user: FitGenUser = { physical_activity_hours_per_day: 0.5 };

        const payload = buildProfilePayload(user);

        expect(payload.physical_activity.physical_activity_hours_per_day).toBe(0.5);
    });

    it('defaults equipment to bodyweight-only when the user selected nothing', () => {
        const user: FitGenUser = { equipment_available: [] };

        const payload = buildProfilePayload(user);

        expect(payload.equipment_available).toEqual(['bodyweight']);
    });

    it('defaults injuries to an empty list when the user selected nothing', () => {
        const user: FitGenUser = { injuries: [] };

        const payload = buildProfilePayload(user);

        expect(payload.injuries).toEqual([]);
    });

    it('drops equipment/injury values that are not valid backend enum members', () => {
        const user: FitGenUser = {
            equipment_available: ['dumbbell', 'not_a_real_equipment'],
            injuries: ['knee', 'not_a_real_injury'],
        };

        const payload = buildProfilePayload(user);

        expect(payload.equipment_available).toEqual(['dumbbell']);
        expect(payload.injuries).toEqual(['knee']);
    });

    it('falls back to sane defaults for a null user', () => {
        const payload = buildProfilePayload(null);

        expect(payload.biometrics).toEqual({ age: 25, weight_kg: 70, height_cm: 175, gender: 'male' });
        expect(payload.equipment).toEqual(['bodyweight']);
        expect(payload.injuries).toEqual([]);
    });

    it('maps onboarding goal ids to the backend FitnessGoal enum', () => {
        expect(mapGoal('hypertrophy')).toBe('muscle_gain');
        expect(mapGoal('strength')).toBe('strength_gain');
        expect(mapGoal('totally_unknown_goal')).toBe('general_fitness');
    });
});

describe('sanitizeEquipment / sanitizeInjuries', () => {
    it('sanitizeEquipment falls back to bodyweight for undefined input', () => {
        expect(sanitizeEquipment(undefined)).toEqual(['bodyweight']);
    });

    it('sanitizeInjuries falls back to an empty list for undefined input', () => {
        expect(sanitizeInjuries(undefined)).toEqual([]);
    });
});

describe('buildPlanRequest', () => {
    it('nests the profile payload under user_profile and passes body_composition through', () => {
        const user: FitGenUser = { age: 25, body_composition: { body_fat_pct: 15 } };

        const request = buildPlanRequest(user);

        expect(request.user_profile.biometrics.age).toBe(25);
        expect(request.body_composition).toEqual({ body_fat_pct: 15 });
    });
});

describe('humanizeGoal', () => {
    it('title-cases a snake_case goal', () => {
        expect(humanizeGoal('muscle_gain')).toBe('Muscle Gain');
    });

    it('returns an em dash for a missing goal', () => {
        expect(humanizeGoal(undefined)).toBe('—');
        expect(humanizeGoal(null)).toBe('—');
    });
});
