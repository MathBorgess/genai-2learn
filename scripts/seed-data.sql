-- Seed data for development/testing

-- Insert test athletes
INSERT INTO athletes (id, email, name) VALUES
    ('a0000000-0000-0000-0000-000000000001', 'alice@example.com', 'Alice Trainer'),
    ('a0000000-0000-0000-0000-000000000002', 'bob@example.com', 'Bob Lifter')
ON CONFLICT (email) DO NOTHING;

-- Insert test workout sessions
INSERT INTO workout_sessions (id, athlete_id, status, planned_workout, readiness_score) VALUES
    (
        's0000000-0000-0000-0000-000000000001',
        'a0000000-0000-0000-0000-000000000001',
        'active',
        '{"exercises": ["squat", "bench_press", "deadlift"]}',
        7.5
    )
ON CONFLICT DO NOTHING;
