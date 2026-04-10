-- ============================================================
-- CyberPulse -- SQL pur pour Neon (converti depuis dbt)
-- Ordre : stg_articles (view) → mart_k1..k6 (tables)
-- ============================================================

-- ============================================================
-- VUE stg_articles
-- ============================================================
DROP VIEW IF EXISTS stg_articles CASCADE;

CREATE VIEW stg_articles AS
WITH base AS (
    SELECT
        id,
        source,
        title,
        description,
        url,
        published_at,
        collected_at,
        inserted_at,
        LOWER(title || ' ' || COALESCE(description, '')) AS text_search
    FROM raw_articles
    WHERE title IS NOT NULL
      AND title != ''
),
parsed AS (
    SELECT
        *,
        CASE
            WHEN published_at ~ '^\d{4}-\d{2}-\d{2}'
                THEN LEFT(published_at, 10)::date
            WHEN published_at ~ '\d{1,2} \w{3} \d{4}'
                THEN TO_DATE(
                    (regexp_match(published_at, '(\d{1,2} \w{3} \d{4})'))[1],
                    'DD Mon YYYY'
                )
            ELSE NULL
        END AS published_date,
        LENGTH(description) AS content_length
    FROM base
)
SELECT
    id, source, title, description, url,
    published_at, collected_at, inserted_at,
    published_date, content_length,
    CASE
        WHEN source = 'French Breaches' THEN 'data_breach'
        WHEN text_search ~ 'ransomware|rançon|lockbit|blackcat|alphv|clop|akira|rhysida|medusa|black.?basta|royal.?ransom|hive.?ransom|double.?extortion|double.?extorsion|chiffrement.?fichier' THEN 'ransomware'
        WHEN text_search ~ 'malware|maliciel|trojan|troyen|cheval.?de.?troie|botnet|spyware|rootkit|keylogger|infostealer|stealer|wiper|backdoor|porte.?dérobée|charge.?utile|payload|remote.?access.?trojan|rat\b|remote.?access|dissecting|crashfix' THEN 'malware'
        WHEN text_search ~ 'phishing|hameçonnage|smishing|vishing|spear.?phishing|ingénierie.?sociale|social.?engineering|credential.?harvesting|faux.?site|usurpation.?identité|business.?email.?compromise|bec|scam|arnaque' THEN 'phishing'
        WHEN text_search ~ 'vulnérabilité|vulnerability|cve-\d|zero.?day|0.?day|faille|exploit|rce|remote.?code.?execution|buffer.?overflow|privilege.?escalation|élévation.?de.?privilège|patch|correctif|mise.?à.?jour.?de.?sécurité|security.?update|security.?advisory|cyberattack|cyber.?attack|hacked|hijack' THEN 'vulnerability'
        WHEN text_search ~ 'data.?breach|fuite.?de.?données|leak|données.?personnelles|données.?exposées|exposed.?data|vol.?de.?données|data.?theft|rgpd|gdpr|cnil|information.?disclosure|credentials.?leaked|password.?leak|database.?exposed|account.?takeover|fraud' THEN 'data_breach'
        WHEN text_search ~ 'apt|advanced.?persistent|état.?nation|state.?sponsored|cyberespionnage|cyber.?espionage|lazarus|fancy.?bear|cozy.?bear|volt.?typhoon|salt.?typhoon|sandworm|turla|kimsuky|charming.?kitten|mustang.?panda|threat.?actor|nation.?state' THEN 'apt'
        WHEN text_search ~ 'ddos|déni.?de.?service|denial.?of.?service|distributed.?denial|attaque.?volumétrique|flooding' THEN 'ddos'
        WHEN text_search ~ 'supply.?chain|chaîne.?d.?approvisionnement|logiciel.?compromis|dépendance.?malveillante|typosquatting|dependency.?confusion|third.?party.?risk|solarwinds|npm.?malicious|pypi.?malicious' THEN 'supply_chain'
        WHEN text_search ~ 'chiffrement|encryption|cryptograph|certificat|tls|ssl|clé.?publique|clé.?privée|aes|rsa|post.?quantum|sha-|md5' THEN 'cryptography'
        WHEN text_search ~ 'pare.?feu|firewall|siem|soc|ids|ips|endpoint|edr|xdr|mdr|antivirus|détection|security.?operations|threat.?detection|incident.?response|réponse.?à.?incident|blue.?team|forensic|cybersecurity|cyber.?security|cybercrime|cyber.?crime|dark.?web|dark.?economy|cyber.?insurance|itdr|cmmc|security.?awareness|managed.?detection|intrusion\b|password.?manag' THEN 'defense'
        WHEN text_search ~ 'pentest|red.?team|bug.?bounty|test.?d.?intrusion|offensive.?security|ethical.?hacking|penetration.?test|ctf|capture.?the.?flag' THEN 'offensive'
        WHEN text_search ~ 'compliance|conformité|réglementation|regulation|nis2|dora|iso.?27001|nist|anssi|certification|audit|gouvernance|governance|politique.?de.?sécurité|cyber.?résilience' THEN 'compliance'
        WHEN text_search ~ 'iam|identité|identity|authentification|authentication|mfa|2fa|oauth|saml|sso|single.?sign|active.?directory|ldap|zero.?trust|accès.?control|privileged.?access|pam' THEN 'identity'
        ELSE 'general'
    END AS category,
    CASE
        WHEN text_search ~ 'ransomware|zero.?day|apt|malware|vulnerability|data.?breach' THEN TRUE
        ELSE FALSE
    END AS is_critical
FROM parsed
WHERE published_date IS NULL
   OR published_date <= CURRENT_DATE;

-- ============================================================
-- MART K1 — Articles par jour et par source
-- ============================================================
DROP TABLE IF EXISTS mart_k1 CASCADE;

CREATE TABLE mart_k1 AS
SELECT
    published_date,
    source,
    COUNT(*) AS nb_articles
FROM stg_articles
WHERE published_date IS NOT NULL
GROUP BY published_date, source
ORDER BY published_date DESC, nb_articles DESC;

-- ============================================================
-- MART K2 — Mots-cles par categorie et periode glissante
-- ============================================================
DROP TABLE IF EXISTS mart_k2 CASCADE;

CREATE TABLE mart_k2 AS
WITH kw_list AS (
    SELECT keyword, category, sub_category
    FROM (VALUES
        ('zero-day','failles','Vulnérabilités'),('0-day','failles','Vulnérabilités'),
        ('cve','failles','Vulnérabilités'),('rce','failles','Vulnérabilités'),
        ('remote code execution','failles','Vulnérabilités'),('lpe','failles','Vulnérabilités'),
        ('privilege escalation','failles','Vulnérabilités'),
        ('sql injection','failles','Techniques'),('xss','failles','Techniques'),
        ('cross-site scripting','failles','Techniques'),('buffer overflow','failles','Techniques'),
        ('man-in-the-middle','failles','Techniques'),('mitm','failles','Techniques'),
        ('supply chain attack','failles','Techniques'),('supply chain','failles','Techniques'),
        ('data breach','failles','Fuites'),('database dump','failles','Fuites'),
        ('leaked credentials','failles','Fuites'),('exfiltration','failles','Fuites'),
        ('data leak','failles','Fuites'),('exposed credentials','failles','Fuites'),
        ('aws','infra','Cloud'),('s3 bucket','infra','Cloud'),
        ('azure','infra','Cloud'),('azure ad','infra','Cloud'),
        ('google cloud','infra','Cloud'),('gcp','infra','Cloud'),
        ('kubernetes','infra','Cloud'),('docker','infra','Cloud'),
        ('active directory','infra','Systèmes'),('windows server','infra','Systèmes'),
        ('linux kernel','infra','Systèmes'),('macos','infra','Systèmes'),('tcc','infra','Systèmes'),
        ('vpn','infra','Réseaux'),('firewall','infra','Réseaux'),
        ('sd-wan','infra','Réseaux'),('dns tunneling','infra','Réseaux'),
        ('firewall bypass','infra','Réseaux'),('vpn gateway','infra','Réseaux'),
        ('cisco','editeurs','Hardware'),('fortinet','editeurs','Hardware'),
        ('palo alto','editeurs','Hardware'),('check point','editeurs','Hardware'),
        ('juniper','editeurs','Hardware'),('ubiquiti','editeurs','Hardware'),('f5','editeurs','Hardware'),
        ('microsoft 365','editeurs','Software'),('exchange','editeurs','Software'),
        ('vmware','editeurs','Software'),('esxi','editeurs','Software'),
        ('citrix','editeurs','Software'),('sap','editeurs','Software'),
        ('salesforce','editeurs','Software'),('atlassian','editeurs','Software'),
        ('confluence','editeurs','Software'),('jira','editeurs','Software'),
        ('ransomware','menaces','Malware'),('infostealer','menaces','Malware'),
        ('trojan','menaces','Malware'),('rat','menaces','Malware'),
        ('botnet','menaces','Malware'),('wiper','menaces','Malware'),('malware','menaces','Malware'),
        ('apt28','menaces','Groupes APT'),('lazarus','menaces','Groupes APT'),
        ('lockbit','menaces','Groupes APT'),('revil','menaces','Groupes APT'),
        ('fancy bear','menaces','Groupes APT'),('scattered spider','menaces','Groupes APT'),
        ('volt typhoon','menaces','Groupes APT'),
        ('ioc','menaces','Indicateurs'),('indicator of compromise','menaces','Indicateurs'),
        ('ttp','menaces','Indicateurs'),('threat intelligence','menaces','Indicateurs'),
        ('threat actor','menaces','Indicateurs')
    ) AS t(keyword, category, sub_category)
),
articles_base AS (
    SELECT
        id, source, published_date,
        LOWER(COALESCE(title, '') || ' ' || COALESCE(description, '')) AS corpus
    FROM stg_articles
    WHERE published_date IS NOT NULL
),
matched AS (
    SELECT
        k.keyword, k.category, k.sub_category,
        a.id, a.source, a.published_date,
        (LENGTH(a.corpus) - LENGTH(REPLACE(a.corpus, k.keyword, '')))
            / NULLIF(LENGTH(k.keyword), 0) AS occ_in_doc
    FROM kw_list k
    JOIN articles_base a ON a.corpus LIKE '%' || k.keyword || '%'
)
SELECT
    k.keyword, k.category, k.sub_category, p.period_days,
    COALESCE(SUM(CASE WHEN m.published_date >= CURRENT_DATE - (p.period_days || ' days')::INTERVAL THEN m.occ_in_doc ELSE 0 END)::INT, 0) AS occurrences,
    COUNT(DISTINCT CASE WHEN m.published_date >= CURRENT_DATE - (p.period_days || ' days')::INTERVAL THEN m.id END) AS article_count,
    COUNT(DISTINCT CASE WHEN m.published_date >= CURRENT_DATE - (p.period_days || ' days')::INTERVAL THEN m.source END) AS source_count
FROM kw_list k
CROSS JOIN (VALUES (3), (7), (15), (30)) AS p(period_days)
LEFT JOIN matched m ON m.keyword = k.keyword
GROUP BY k.keyword, k.category, k.sub_category, p.period_days
ORDER BY p.period_days, occurrences DESC;

-- ============================================================
-- MART K3 — Repartition par type de menace x source
-- ============================================================
DROP TABLE IF EXISTS mart_k3 CASCADE;

CREATE TABLE mart_k3 AS
SELECT
    category,
    source,
    COUNT(*) AS nb_articles
FROM stg_articles
WHERE published_date IS NOT NULL
GROUP BY category, source
ORDER BY category, nb_articles DESC;

-- ============================================================
-- MART K4 — Evolution des mentions par categorie
-- ============================================================
DROP TABLE IF EXISTS mart_k4 CASCADE;

CREATE TABLE mart_k4 AS
SELECT
    published_date,
    category,
    COUNT(*) AS nb_mentions
FROM stg_articles
WHERE published_date IS NOT NULL
GROUP BY published_date, category
ORDER BY published_date DESC, nb_mentions DESC;

-- ============================================================
-- MART K5 — Alertes par semaine et categorie
-- ============================================================
DROP TABLE IF EXISTS mart_k5 CASCADE;

CREATE TABLE mart_k5 AS
SELECT
    DATE_TRUNC('week', published_date::timestamp)::date AS semaine,
    category,
    COUNT(*) AS nb_alertes
FROM stg_articles
WHERE published_date IS NOT NULL
GROUP BY 1, 2
ORDER BY semaine DESC, nb_alertes DESC;

-- ============================================================
-- MART K6 — CVE les plus mentionnees
-- ============================================================
DROP TABLE IF EXISTS mart_k6 CASCADE;

CREATE TABLE mart_k6 AS
WITH cve_extraites AS (
    SELECT
        t.cve[1] AS cve,
        id
    FROM stg_articles,
    LATERAL regexp_matches(
        COALESCE(title, '') || ' ' || COALESCE(description, ''),
        'CVE-[0-9]{4}-[0-9]{4,7}',
        'g'
    ) AS t(cve)
)
SELECT
    cve,
    COUNT(DISTINCT id) AS nb_mentions
FROM cve_extraites
GROUP BY cve
ORDER BY nb_mentions DESC
LIMIT 20;

-- ============================================================
-- Verification finale
-- ============================================================
SELECT 'stg_articles' AS objet, COUNT(*) AS lignes FROM stg_articles
UNION ALL SELECT 'mart_k1', COUNT(*) FROM mart_k1
UNION ALL SELECT 'mart_k2', COUNT(*) FROM mart_k2
UNION ALL SELECT 'mart_k3', COUNT(*) FROM mart_k3
UNION ALL SELECT 'mart_k4', COUNT(*) FROM mart_k4
UNION ALL SELECT 'mart_k5', COUNT(*) FROM mart_k5
UNION ALL SELECT 'mart_k6', COUNT(*) FROM mart_k6
ORDER BY objet;