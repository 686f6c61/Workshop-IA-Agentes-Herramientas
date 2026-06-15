# PR checklist · release multimodal

- [ ] El ZIP se ejecuta con `make run` y `make test`.
- [ ] La decisión global no depende de una media agregada.
- [ ] Cada caso sensible tiene `policy_decision`, redacción y lineage.
- [ ] Cada acción externa tiene approval card y egress policy.
- [ ] Los SLI/SLO quedan dentro de umbral en `output/sli_slo_matrix.csv`.
- [ ] Hay owner técnico, aprobadores y rollback.
- [ ] Se repitieron evals tras cambios de modelo, OCR, ASR, retrieval, prompt, tool o policy.
- [ ] La decisión final se puede defender con `output/evidence_pack.md` y `output/release_change_request.md`.
