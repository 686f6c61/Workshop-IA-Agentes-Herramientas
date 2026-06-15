# Checks de recuperación RAG

| Escenario | Documento | Fuente | Confianza | Estado | Decisión | Notas |
|---|---|---|---|---|---|---|
| S01 | DOC-001 | internal_policy | trusted_policy | active | allow | sin notas |
| S02 | DOC-002 | committee_note | internal_restricted | active | block | rol sin ACL para documento |
| S03 | DOC-003 | external_web | untrusted_external | active | block | contenido externo sin bloque delimitado de no confianza; contenido externo contiene texto con forma de orden |
| S04 | DOC-001 | internal_policy | trusted_policy | active | allow | sin notas |
| S05 | DOC-001 | internal_policy | trusted_policy | active | allow | sin notas |
| S06 | DOC-001 | internal_policy | trusted_policy | active | allow | sin notas |
| S07 | DOC-001 | internal_policy | trusted_policy | active | allow | sin notas |
