-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Athletes table
CREATE TABLE IF NOT EXISTS athletes (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email       VARCHAR(255) UNIQUE NOT NULL,
    name        VARCHAR(255) NOT NULL,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Workout sessions table
CREATE TABLE IF NOT EXISTS workout_sessions (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    athlete_id       UUID NOT NULL REFERENCES athletes(id) ON DELETE CASCADE,
    started_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status           VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
    planned_workout  JSONB,
    readiness_score  FLOAT CHECK (readiness_score >= 0 AND readiness_score <= 10),
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_workout_sessions_athlete_id ON workout_sessions(athlete_id);
CREATE INDEX IF NOT EXISTS idx_workout_sessions_started_at ON workout_sessions(started_at);

-- Exercise sets table
CREATE TABLE IF NOT EXISTS exercise_sets (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id      UUID NOT NULL REFERENCES workout_sessions(id) ON DELETE CASCADE,
    exercise_id     VARCHAR(255) NOT NULL,
    load_kg         FLOAT NOT NULL CHECK (load_kg >= 0 AND load_kg <= 1000),
    reps            INTEGER NOT NULL CHECK (reps >= 0 AND reps <= 100),
    rir_reported    FLOAT CHECK (rir_reported >= 0 AND rir_reported <= 10),
    rpe_reported    FLOAT CHECK (rpe_reported >= 0 AND rpe_reported <= 10),
    bpm_avg         FLOAT CHECK (bpm_avg >= 30 AND bpm_avg <= 250),
    bpm_peak        FLOAT CHECK (bpm_peak >= 30 AND bpm_peak <= 250),
    rest_seconds    INTEGER CHECK (rest_seconds >= 0),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_exercise_sets_session_id ON exercise_sets(session_id);
CREATE INDEX IF NOT EXISTS idx_exercise_sets_exercise_id ON exercise_sets(exercise_id);
CREATE INDEX IF NOT EXISTS idx_exercise_sets_created_at ON exercise_sets(created_at);

-- Effort estimates table
CREATE TABLE IF NOT EXISTS effort_estimates (
    id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    set_id                UUID NOT NULL REFERENCES exercise_sets(id) ON DELETE CASCADE,
    effort_score          FLOAT NOT NULL CHECK (effort_score >= 0 AND effort_score <= 100),
    rir_estimate          FLOAT CHECK (rir_estimate >= 0),
    confidence            FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    feature_contributions JSONB,
    created_at            TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_effort_estimates_set_id ON effort_estimates(set_id);

-- Recommendations table
CREATE TABLE IF NOT EXISTS recommendations (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    set_id              UUID NOT NULL REFERENCES exercise_sets(id) ON DELETE CASCADE,
    action_type         VARCHAR(50) NOT NULL CHECK (action_type IN ('INCREASE_LOAD', 'DECREASE_LOAD', 'MAINTAIN', 'ADJUST_TECHNIQUE')),
    load_delta_pct      FLOAT DEFAULT 0.0,
    cue_list            JSONB DEFAULT '[]'::jsonb,
    safety_reason_codes JSONB DEFAULT '[]'::jsonb,
    rationale           TEXT,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_recommendations_set_id ON recommendations(set_id);

-- Recommendation outcomes table
CREATE TABLE IF NOT EXISTS recommendation_outcomes (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recommendation_id       UUID NOT NULL REFERENCES recommendations(id) ON DELETE CASCADE,
    set_id                  UUID NOT NULL REFERENCES exercise_sets(id) ON DELETE CASCADE,
    accepted                BOOLEAN,
    completed_reps          INTEGER,
    resulting_rir_reported  FLOAT,
    pain_flag               BOOLEAN DEFAULT FALSE,
    notes                   TEXT,
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_recommendation_outcomes_recommendation_id ON recommendation_outcomes(recommendation_id);
