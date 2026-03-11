-- CyberPulse — Modèle mart KPIs
-- Table analytique finale pour le dashboard Streamlit
-- À compléter en Sprint 3

{
{ config
(materialized='table') }}

SELECT
    published_date,
    source,
    category,
    COUNT(*)                     AS nb_articles,
    AVG(content_length)          AS avg_content_length,
    MIN(published_date)          AS first_seen,
    MAX(published_date)          AS last_seen

FROM {{ ref
('stg_articles') }}

GROUP BY
    published_date,
    source,
    category

ORDER BY
    published_date DESC,
    nb_articles DESC
