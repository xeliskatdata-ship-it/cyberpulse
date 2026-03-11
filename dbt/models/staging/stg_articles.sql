-- CyberPulse — Modèle staging
-- Nettoie et normalise les articles bruts de raw_articles
-- À compléter en Sprint 3

{
{ config
(materialized='view') }}

SELECT
    id,
    title,
    LOWER(TRIM(source))          AS source,
    LOWER(TRIM(category))        AS category,
    published_at::date           AS published_date,
    published_at::time           AS published_time,
    url,
    content,
    LENGTH(content)              AS content_length,
    created_at

FROM {{ source
('raw', 'raw_articles') }}

-- Exclure les articles sans titre ni contenu
WHERE title IS NOT NULL
  AND title != ''
