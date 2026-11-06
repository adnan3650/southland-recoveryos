# Resource provenance and refresh

The initial dataset contains 11 official/established nonprofit references in `data/resources.json`. Records include ID, category, description, coverage, eligibility/prerequisites, contact, source URL, review date, verification note, availability and limitations. They describe references, never open beds, active funding, current application windows or confirmed declarations.

Source content was reviewed using web retrieval on November 6, 2026. Retrieval can return indexed content; review date is not a guarantee that the remote site was updated that day. The local resident incident is fictional and must never be attributed to an actual declared disaster.

- Emergency contact: https://www.911.gov/calling-911/
- Flood safety reference (retrieval blocked; unverified): https://www.ready.gov/floods
- Cook County referrals: https://211metrochicago.org/
- Shelter locator reference, no capacity claim: https://www.redcross.org/get-help/disaster-relief-and-recovery-services/find-an-open-shelter.html
- Food directory: https://www.chicagosfoodbank.org/find-food-2/
- County flood recovery/documentation: https://www.cookcountyil.gov/floods
- Illinois agency directory: https://ready.illinois.gov/after/marc.html
- Municipal reporting contact: https://www.southholland.org/departments/public-works (refresh timed out in this run; marked unverified)
- Municipal prevention rebate: https://www.southholland.org/news/flood-prevention-and-protection
- FEMA reference (retrieval blocked; no current availability): https://www.fema.gov/assistance/individual
- County recovery planning: https://www.cookcountyil.gov/service/disaster-recovery-and-resilience (specified prior disasters; no inference for fictional September 2026 event)

South Holland's current news source describes prequalification and project-based prevention rebates. Owner occupancy/two-bid prerequisites were rechecked in the official 2017 Floodplain Management Plan, page 7-22 (PDF page 84): https://southholland.org/wp-content/uploads/2025/06/SouthHollandFMP2017Final.pdf . This historical plan does not establish current terms; confirm them with the Village. No amounts/deadlines are used by the matching engine. Program statuses distinguish mismatch, missing information, potentially relevant and unverified availability; none determines eligibility.

## Ingestion pipeline

Curator retrieves official pages, extracts only supportable statements, records checked date and limitations, and creates JSON records. `scripts/validate_sources.py INPUT --output NEW_FILE` parses, normalizes URLs, schema validates, identifies duplicate IDs/name+URL pairs and writes a new file exclusively. Reviewer inspects diff before replacing the production dataset. ResourceService loads validated records and performs category/text/geographic search. Updates require restart. No scheduled live scraping, automatic authoritative verification or availability integration exists.

Refresh municipal and program requirements before each demonstration and before any real deployment. Treat HTTP success as transport evidence only. If content cannot be fetched, retain an official link with verified_at null, remove unsupported claims, and request direct agency confirmation. Never invent fictional resources to fill gaps.

Claude model and structured outputs references: https://platform.claude.com/docs/en/models/overview and https://platform.claude.com/docs/en/build-with-claude/structured-outputs . Default model ID `claude-sonnet-5-5` appears in the official model table. Live SDK/account acceptance remains required.
