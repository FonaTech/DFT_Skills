# Third-Party And Copyright Boundaries

This document defines the copyright scope of `DFT_Skills`, the boundaries of the MIT license in this repository, and the non-redistribution rules for VASP-related and other third-party content.

It is a repository policy document, not legal advice.

## 1. Scope Of The MIT License In This Repository

The MIT license in [LICENSE](./LICENSE) applies only to original content contributed to this repository, including:

- original skill instructions and frontmatter
- original Markdown documentation written for this repository
- original Python and shell helper scripts written for this repository
- original JSON preset manifests, case-study templates, and packaging metadata

The MIT license here does not relicense or supersede the rights of any third-party software, website content, documentation, datasets, binaries, logos, trademarks, or user-uploaded files that may be referenced by this repository.

## 2. VASP-Specific Boundary

This repository is a workflow and orchestration layer for VASP-facing tasks. It is not VASP itself.

The following items are not included in this repository and are not redistributed by it:

- VASP source code
- VASP binaries or compiled executables
- VASP portal downloads
- PAW datasets and `POTCAR` files
- copied VASP manuals, copied wiki mirrors, or copied proprietary support material
- license keys, user credentials, or paid-access content

Repository scripts may call a local VASP executable that the user has already obtained independently. That local executable remains separately licensed software.

Repository scripts may also expect a local pseudopotential tree. If no lawful local `POTCAR` source exists, the workflow must stop rather than fabricate or bundle one.

## 3. Why The VASP Boundary Is Strict

The packaging rules above are based on official VASP pages that state, in substance:

- VASP is not public-domain software and requires an appropriate license
- access to downloads is controlled through the VASP portal and license-user registration
- `POTCAR` content comes from separately distributed templates available through the VASP portal
- VASP wiki pages are official documentation pages and remain under their own site-level terms

This repository therefore uses a link-and-paraphrase model:

- link to official pages
- summarize workflows in original wording
- avoid mirroring upstream manuals or portal assets
- keep proprietary artifacts out of git history

## 4. VASP Wiki And Documentation Handling

VASP-facing method notes in this repository are original summaries and workflow paraphrases. They are not intended as a substitute for the official VASP documentation.

The repository policy is:

- cite VASP pages by URL rather than copying them into repository files
- keep quotations short and exceptional
- do not bulk-copy official wiki pages, PDFs, tables, figures, or tutorial bodies into the repository
- do not commit scraped or mirrored copies of the VASP wiki

One official VASP wiki page consulted for pseudopotential handling explicitly notes that wiki content is available under GNU Free Documentation License 1.2 unless otherwise noted. Even so, this repository defaults to paraphrase plus URL citation rather than document copying.

## 5. Other Upstream Software, Services, And Data Sources

This repository may interoperate with or reference separately governed tools and resources, including:

- pymatgen
- ASE
- Materials Project
- Crystallography Open Database
- LAMMPS
- COMSOL

Use of those tools or services is governed by their own licenses, terms, access policies, and citation expectations. This repository does not claim ownership over them and does not relicense them.

## 6. User Data, Uploaded Files, And Local Literature

User-provided files, uploaded papers, local PDFs, CIFs, POSCARs, spreadsheets, and datasets remain owned by their original rightsholders or uploaders.

This repository only provides workflow logic for reading, organizing, analyzing, or routing such files. It does not grant redistribution rights over them.

If a user supplies third-party copyrighted material, the repository policy is:

- process locally when allowed by the active runtime and the user request
- avoid copying large copyrighted bodies into repository files
- keep provenance and source attribution in project outputs
- store only what the user is entitled to store

## 7. Systematic Copyright-Avoidance Policy

Contributors to this repository should follow these rules:

- do not commit VASP source, binaries, `POTCAR`, portal downloads, or paid materials
- do not paste large portions of official manuals, wiki pages, papers, book chapters, or tutorial PDFs into repository Markdown
- do not commit copyrighted figures, logos, screenshots, or branded assets without permission
- do not commit third-party structure files unless redistribution rights are clear
- prefer original summaries, original examples, and URL references over copied instructional content
- keep API keys, download credentials, and portal access data out of the repository
- if a file comes from another source, document the provenance and legal basis for inclusion

## 8. Recommended Contributor Checklist

Before merging or publishing, verify:

1. no proprietary VASP artifacts are present in git-tracked files
2. no `POTCAR` or pseudopotential bundle is present
3. no copied upstream manual or wiki mirror has been committed
4. examples are original, synthetic, user-owned, or openly redistributable
5. third-party references are linked, not mirrored, unless redistribution rights are documented
6. any quoted material is short, necessary, and properly attributed

## 9. Official Reference Webpages Used For These Boundaries

### VASP

- VASP home: <https://www.vasp.at/>
- VASP Wiki landing page: <https://www.vasp.at/home/wiki/>
- FAQ on software status and licensing boundary: <https://www.vasp.at/info/faq/public_domain/>
- FAQ on obtaining a license: <https://www.vasp.at/info/faq/purchase_vasp/>
- FAQ on access and registered users: <https://www.vasp.at/info/faq/vasp_access/>
- Official `POTCAR` documentation: <https://www.vasp.at/wiki/index.php/POTCAR>
- Official `POTCAR` preparation page: <https://www.vasp.at/wiki/index.php/Preparing_a_POTCAR>
- Official NEB page: <https://www.vasp.at/wiki/index.php/Nudged_elastic_bands>
- Official optical-properties page: <https://www.vasp.at/wiki/index.php/Optical_properties>
- Official Berry-phase page: <https://www.vasp.at/wiki/Berry_phases_and_finite_electric_fields>
- Official molecular-dynamics page: <https://www.vasp.at/wiki/Molecular_dynamics_calculations?redirect=no&title=Molecular_dynamics_calculations>

### Other upstream references

- pymatgen: <https://pymatgen.org/>
- ASE: <https://ase-lib.org/>
- Materials Project API and documentation: <https://docs.materialsproject.org/downloading-data/using-the-api/querying-data>
- Materials Project website notes: <https://docs.materialsproject.org/changes>
- Crystallography Open Database: <https://www.crystallography.net/cod/>
- LAMMPS: <https://www.lammps.org/>
- COMSOL: <https://www.comsol.com/>

## 10. Trademarks And Affiliation

Product names, company names, and service names mentioned in this repository belong to their respective owners.

This repository does not claim endorsement by, partnership with, or ownership of:

- VASP Software GmbH
- Materials Project
- ASE developers
- pymatgen developers
- LAMMPS developers
- COMSOL

Any mention of those names is purely for compatibility, workflow integration, or reference purposes.
