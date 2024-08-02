CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    password TEXT,
    admin BOOLEAN
);

CREATE TABLE discussion_areas (
    id SERIAL PRIMARY KEY,
    topic TEXT,
    confidential BOOLEAN
);

CREATE TABLE discussion_chains (
    id SERIAL PRIMARY KEY,
    header TEXT,
    discussion_area_id INTEGER REFERENCES discussion_areas ON DELETE CASCADE,
    creator_id INTEGER REFERENCES users
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    content TEXT,
    discussion_chain_id INTEGER REFERENCES discussion_chains ON DELETE CASCADE,
    creator_id INTEGER REFERENCES users,
    sent_at TIMESTAMP
);

CREATE TABLE users_of_confidential_discussion_areas (
    id SERIAL PRIMARY KEY,
    discussion_area_id INTEGER REFERENCES discussion_areas ON DELETE CASCADE,
    user_id INTEGER REFERENCES users
);