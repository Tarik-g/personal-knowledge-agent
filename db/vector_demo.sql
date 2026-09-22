-- A temporary three-dimensional example. These numbers are illustrative,
-- not embeddings generated from the labels.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TEMP TABLE vector_demo (
    label text NOT NULL,
    embedding vector(3) NOT NULL
);

INSERT INTO vector_demo (label, embedding) VALUES
    ('Auto und Motor', '[0.9,0.1,0.0]'),
    ('Fahrzeug reparieren', '[0.8,0.2,0.0]'),
    ('Kochen und Rezepte', '[0.0,0.1,0.9]');

SELECT
    label,
    round((embedding <=> '[0.85,0.15,0.0]'::vector)::numeric, 4) AS cosine_distance
FROM vector_demo
ORDER BY embedding <=> '[0.85,0.15,0.0]'::vector;
