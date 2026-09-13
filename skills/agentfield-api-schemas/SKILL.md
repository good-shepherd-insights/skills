---
name: agentfield-api-schemas
version: 1.0.0
description: "Schema document for the Good Shepherd Insights AgentField fleet URLs (agents/swe/research/pr/sec.goodshepherdinsights.com) — every reasoner endpoint with its full input schema, so agents know how to use them."
---

# Agent API Schema Reference — goodshepherdinsights.com

Generated from live control-plane registry 2026-09-13.
Every endpoint: POST <url>/api/v1/execute/<node_id>.<reasoner_id> with {"input": {...}}.
Sync: use /execute/ (blocks). Async: /execute/async/ returns {execution_id}; poll
GET <url>/api/v1/execution/<execution_id>/result.
Bot Fight Mode is OFF + Browser Integrity Check OFF — any programmatic UA works.
Node-level health: GET /health on each host.

## sec-af — Codebase security QA
- Base: https://sec.goodshepherdinsights.com (public) | http://localhost:8005 (local)
- Reasoners: 34
### sec-af.audit
  
  input_schema:
      - repo_url: string *REQUIRED*
      - depth: string
      - branch: string
      - commit_sha: any
      - base_commit_sha: any
      - severity_threshold: string
      - scan_types: any
      - output_formats: any
      - compliance_frameworks: any
      - max_cost_usd: any
      - max_provers: any
      - max_duration_seconds: any
      - include_paths: any
      - exclude_paths: any
      - is_pr: boolean
      - pr_id: any
      - post_pr_comments: boolean
      - fail_on_findings: boolean
      - enable_dast: boolean
      - resume_from_checkpoint: any

### sec-af.run_architecture_mapper
  
  input_schema:
      - repo_path: string *REQUIRED*

### sec-af.run_dependency_auditor
  
  input_schema:
      - repo_path: string *REQUIRED*

### sec-af.run_config_scanner
  
  input_schema:
      - repo_path: string *REQUIRED*

### sec-af.run_data_flow_mapper
  
  input_schema:
      - repo_path: string *REQUIRED*
      - architecture: any *REQUIRED*

### sec-af.run_security_context_profiler
  
  input_schema:
      - repo_path: string *REQUIRED*
      - architecture: any *REQUIRED*

### sec-af.run_injection_hunter
  
  input_schema:
      - repo_path: string *REQUIRED*
      - recon_context: any *REQUIRED*
      - depth: string *REQUIRED*
      - max_files_without_signal: integer

### sec-af.run_dos_hunter
  
  input_schema:
      - repo_path: string *REQUIRED*
      - recon_context: any *REQUIRED*
      - depth: string *REQUIRED*
      - max_files_without_signal: integer

### sec-af.run_ssrf_hunter
  
  input_schema:
      - repo_path: string *REQUIRED*
      - recon_context: any *REQUIRED*
      - depth: string *REQUIRED*
      - max_files_without_signal: integer

### sec-af.run_auth_hunter
  
  input_schema:
      - repo_path: string *REQUIRED*
      - recon_context: any *REQUIRED*
      - depth: string *REQUIRED*
      - max_files_without_signal: integer

### sec-af.run_xss_hunter
  
  input_schema:
      - repo_path: string *REQUIRED*
      - recon_context: any *REQUIRED*
      - depth: string *REQUIRED*
      - max_files_without_signal: integer

### sec-af.run_crypto_hunter
  
  input_schema:
      - repo_path: string *REQUIRED*
      - recon_context: any *REQUIRED*
      - depth: string *REQUIRED*
      - max_files_without_signal: integer

### sec-af.run_business_logic_hunter
  
  input_schema:
      - repo_path: string *REQUIRED*
      - recon_context: any *REQUIRED*
      - depth: string *REQUIRED*
      - max_files_without_signal: integer

### sec-af.run_logic_bugs_hunter
  
  input_schema:
      - repo_path: string *REQUIRED*
      - recon_context: any *REQUIRED*
      - depth: string *REQUIRED*
      - max_files_without_signal: integer

### sec-af.run_data_exposure_hunter
  
  input_schema:
      - repo_path: string *REQUIRED*
      - recon_context: any *REQUIRED*
      - depth: string *REQUIRED*
      - max_files_without_signal: integer

### sec-af.run_supply_chain_hunter
  
  input_schema:
      - repo_path: string *REQUIRED*
      - recon_context: any *REQUIRED*
      - depth: string *REQUIRED*
      - max_files_without_signal: integer

### sec-af.run_config_secrets_hunter
  
  input_schema:
      - repo_path: string *REQUIRED*
      - recon_context: any *REQUIRED*
      - depth: string *REQUIRED*
      - max_files_without_signal: integer

### sec-af.run_api_security_hunter
  
  input_schema:
      - repo_path: string *REQUIRED*
      - recon_context: any *REQUIRED*
      - depth: string *REQUIRED*
      - max_files_without_signal: integer

### sec-af.run_deduplicator
  
  input_schema:
      - findings: array *REQUIRED*
      - recon_context: any *REQUIRED*
      - repo_path: string *REQUIRED*

### sec-af.run_dep_reachability
  
  input_schema:
      - repo_path: string *REQUIRED*
      - finding: any *REQUIRED*
      - depth: string *REQUIRED*

### sec-af.run_verifier
  
  input_schema:
      - repo_path: string *REQUIRED*
      - finding: any *REQUIRED*
      - depth: string *REQUIRED*

### sec-af.run_tracer
  
  input_schema:
      - repo_path: string *REQUIRED*
      - finding: any *REQUIRED*
      - depth: string *REQUIRED*

### sec-af.run_sanitization_analyzer
  
  input_schema:
      - repo_path: string *REQUIRED*
      - finding: any *REQUIRED*
      - data_flow: any *REQUIRED*
      - depth: string *REQUIRED*

### sec-af.run_exploit_hypothesizer
  
  input_schema:
      - repo_path: string *REQUIRED*
      - finding: any *REQUIRED*
      - data_flow: any *REQUIRED*
      - sanitization: any *REQUIRED*
      - depth: string *REQUIRED*

### sec-af.run_verdict_agent
  
  input_schema:
      - finding: any *REQUIRED*
      - data_flow: any *REQUIRED*
      - sanitization: any *REQUIRED*
      - exploit: any *REQUIRED*

### sec-af.run_remediation
  
  input_schema:
      - repo_path: string *REQUIRED*
      - finding: any *REQUIRED*

### sec-af.run_remediation_agent
  
  input_schema:
      - repo_path: string *REQUIRED*
      - finding: any *REQUIRED*
      - verdict: string *REQUIRED*
      - rationale: string *REQUIRED*

### sec-af.run_dast_verifier
  
  input_schema:
      - repo_path: string *REQUIRED*
      - finding: any *REQUIRED*
      - exploit_payload: string *REQUIRED*
      - depth: string *REQUIRED*

### sec-af.run_cross_service_analyzer
  
  input_schema:
      - repo_path: string *REQUIRED*
      - services: array *REQUIRED*
      - findings_summary: string *REQUIRED*
      - depth: string *REQUIRED*

### sec-af.run_cwe_expansion
  
  input_schema:
      - recon_summary: string *REQUIRED*
      - strategies: array *REQUIRED*

### sec-af.recon_phase
  
  input_schema:
      - repo_path: string *REQUIRED*
      - depth: string

### sec-af.hunt_phase
  
  input_schema:
      - repo_path: string *REQUIRED*
      - recon_context: any *REQUIRED*
      - depth: string
      - ai_gate: any
      - max_concurrent_hunters: integer
      - early_stop_file_threshold: integer

### sec-af.prove_phase
  
  input_schema:
      - repo_path: string *REQUIRED*
      - hunt_result: any *REQUIRED*
      - depth: string
      - max_provers: any
      - max_concurrent_provers: integer

### sec-af.remediation_phase
  Run remediation for confirmed/likely findings in parallel via app.call().
  input_schema:
      - repo_path: string *REQUIRED*
      - verified_findings: array *REQUIRED*
      - max_concurrent_remediations: integer


## pr-af — AI pull-request reviewer
- Base: https://pr.goodshepherdinsights.com (public) | http://localhost:8004 (local)
- Reasoners: 17
### pr-af.review
  
  input_schema:
      - pr_url: any
      - diff_text: any
      - repo_path: any
      - base_ref: any
      - head_ref: any
      - depth: string
      - max_cost_usd: any
      - max_duration_seconds: any
      - focus: string
      - ignore_paths: any
      - hints: any
      - models: any
      - max_concurrent_agents: any
      - max_concurrent_reviewers: any
      - max_coverage_iterations: any
      - max_review_depth: integer
      - output_format: string
      - dry_run: boolean
      - post_pr_number: any
      - suggestion_mode: string

### pr-af.intake_phase
  
  input_schema:
      - pr_data: any *REQUIRED*
      - depth: string

### pr-af.anatomy_phase
  
  input_schema:
      - pr_data: any *REQUIRED*
      - intake: any *REQUIRED*
      - repo_path: string

### pr-af.planning_phase
  
  input_schema:
      - intake: any *REQUIRED*
      - anatomy: any *REQUIRED*
      - depth: string
      - hints: any

### pr-af.meta_semantic
  Semantic lens: What does this code DO differently?
  input_schema:
      - intake: any *REQUIRED*
      - anatomy: any *REQUIRED*
      - depth: string
      - repo_path: string
      - diff_patches: any
      - reviewer_feedback: string

### pr-af.meta_mechanical
  Mechanical lens: Does this code WORK correctly at the language level?
  input_schema:
      - intake: any *REQUIRED*
      - anatomy: any *REQUIRED*
      - depth: string
      - repo_path: string
      - diff_patches: any
      - reviewer_feedback: string

### pr-af.meta_systemic
  Systemic lens: How does this code FIT the codebase?
  input_schema:
      - intake: any *REQUIRED*
      - anatomy: any *REQUIRED*
      - depth: string
      - repo_path: string
      - diff_patches: any
      - reviewer_feedback: string

### pr-af.review_dimension
  
  input_schema:
      - review_prompt: string *REQUIRED*
      - target_files: array *REQUIRED*
      - context_files: any
      - repo_path: string
      - current_depth: integer
      - max_depth: integer
      - pr_narrative: string
      - risk_surfaces: any
      - intake_summary: string
      - pr_description: string
      - diff_patches: any
      - all_dimension_names: any
      - reviewer_feedback: string
      - primed_code: string

### pr-af.compound_finder_phase
  
  input_schema:
      - cluster_findings: array *REQUIRED*
      - repo_path: string
      - evidence_map: any

### pr-af.post_worthiness_gate
  Calibrated post-worthiness gate (precision lever; recall-preserving).
  input_schema:
      - findings: array *REQUIRED*

### pr-af.compound_dedup_phase
  Deduplicate compound findings via a single harness call.
  input_schema:
      - compound_findings: array *REQUIRED*
      - individual_findings_summary: string

### pr-af.evidence_verifier
  
  input_schema:
      - findings: array *REQUIRED*
      - evidence_packages: any
      - pr_context: string
      - repo_path: string

### pr-af.adversary_phase
  
  input_schema:
      - findings: array *REQUIRED*
      - ai_generated_confidence: number
      - pr_context: string
      - repo_path: string
      - evidence_packages: any

### pr-af.deepen_findings
  Literal ground-truth verification of the changed code (the meticulous pass).
  input_schema:
      - diff_patches: any
      - existing_titles: any
      - repo_path: string
      - pr_context: string

### pr-af.extract_obligations
  Enumerate the cross-location consistency obligations the changed code creates.
  input_schema:
      - diff_patches: any
      - repo_path: string
      - pr_context: string

### pr-af.verify_obligation
  Verify ONE consistency obligation by reading BOTH ends in the repo.
  input_schema:
      - obligation: any *REQUIRED*
      - repo_path: string

### pr-af.coverage_gate
  
  input_schema:
      - anatomy: any *REQUIRED*
      - reviewed_clusters: array *REQUIRED*
      - dimension_names_reviewed: any


## meta_deep_research — Deep research engine (~10k invocations/query)
- Base: https://research.goodshepherdinsights.com (public) | http://localhost:8003 (local)
- Reasoners: 22
### meta_deep_research.merge_entity_pair
  Merges two specific entities into one.
  input_schema:
      - entity1: any *REQUIRED* — Represents a person, organization, concept, or other key noun.
      - entity2: any *REQUIRED* — Represents a person, organization, concept, or other key noun.
      - model: string
      - api_key: string

### meta_deep_research.detect_entity_duplicates_batch
  Detects potential duplicate entities in a batch.
  input_schema:
      - entities_batch: array *REQUIRED*
      - model: string
      - api_key: string

### meta_deep_research.detect_relationship_duplicates_batch
  Detects potential duplicate relationships in a batch.
  input_schema:
      - relationships_batch: array *REQUIRED*
      - model: string
      - api_key: string

### meta_deep_research.merge_relationship_pair
  Merges two specific relationships into one.
  input_schema:
      - rel1: any *REQUIRED* — Describes a connection between two entities.
      - rel2: any *REQUIRED* — Describes a connection between two entities.
      - model: string
      - api_key: string

### meta_deep_research.check_evidence_duplication
  Checks if two pieces of evidence are duplicates.
  input_schema:
      - evidence1: any *REQUIRED* — Contains structured data extracted from a single source article.
      - evidence2: any *REQUIRED* — Contains structured data extracted from a single source article.
      - model: string
      - api_key: string

### meta_deep_research.generate_adaptive_hypothesis
  Generates adaptive hypothesis based on query type and domain.
  input_schema:
      - query: string *REQUIRED*
      - query_type: string *REQUIRED*
      - key_discoveries: array *REQUIRED*
      - entities: array *REQUIRED*
      - relationships: array *REQUIRED*
      - model: string
      - api_key: string

### meta_deep_research.assess_research_completeness
  Evaluates the completeness and quality of current research state.
  input_schema:
      - query: string *REQUIRED*
      - entities: array *REQUIRED*
      - relationships: array *REQUIRED*
      - key_discoveries: array *REQUIRED*
      - hypothesis_confidence: string *REQUIRED*
      - model: string
      - api_key: string

### meta_deep_research.identify_knowledge_gaps_batch
  Identifies specific knowledge gaps that need investigation.
  input_schema:
      - query: string *REQUIRED*
      - entities: array *REQUIRED*
      - relationships: array *REQUIRED*
      - current_evidence_summary: string *REQUIRED*
      - batch_focus: string *REQUIRED*
      - model: string
      - api_key: string

### meta_deep_research.generate_targeted_search_queries
  Generates specific search queries to address identified gaps.
  input_schema:
      - gaps: array *REQUIRED*
      - original_query: string *REQUIRED*
      - current_entities: array *REQUIRED*
      - model: string
      - api_key: string

### meta_deep_research.decide_iteration_continuation
  Decides whether to continue with another research iteration.
  input_schema:
      - quality_score: any *REQUIRED* — Simple quality assessment of current research state.
      - gaps_identified: array *REQUIRED*
      - current_iteration: integer *REQUIRED*
      - max_iterations: integer *REQUIRED*
      - query: string *REQUIRED*
      - model: string
      - api_key: string

### meta_deep_research.generate_adaptive_search_streams
  Generates adaptive search streams based on query type and domain.
  input_schema:
      - core_subject: string *REQUIRED*
      - key_question: string *REQUIRED*
      - query_type: string *REQUIRED*
      - num_parallel_streams: integer
      - model: string
      - api_key: string

### meta_deep_research.execute_intelligence_stream_comprehensive
  Comprehensive intelligence stream execution with full article/evidence collection.
  input_schema:
      - stream_name: string *REQUIRED*
      - search_queries: array *REQUIRED*
      - analysis_focus: string *REQUIRED*
      - subject: string *REQUIRED*
      - key_question: string *REQUIRED*
      - start_article_id: integer *REQUIRED*
      - model: string
      - api_key: string

### meta_deep_research.prepare_research_package
  Iterative research orchestrator with multi-stream intelligence gathering.
  input_schema:
      - query: string *REQUIRED*
      - mode: string
      - research_focus: integer
      - research_scope: integer
      - max_research_loops: integer
      - num_parallel_streams: integer
      - model: string
      - api_key: string

### meta_deep_research.continue_research
  Continues research from a previous package with additional queries.
  input_schema:
      - previous_package: any *REQUIRED*
      - sub_query: string *REQUIRED*
      - mode: string
      - research_focus: integer
      - research_scope: integer
      - max_research_loops: integer
      - num_parallel_streams: integer
      - model: string
      - api_key: string

### meta_deep_research.generate_adaptive_inquiry_probes
  Generates targeted inquiry probes based on hypothesis gaps and network analysis.
  input_schema:
      - query: string *REQUIRED*
      - hypothesis: any *REQUIRED* — A structured research hypothesis based on synthesized intelligence.
      - entities: array *REQUIRED*
      - relationships: array *REQUIRED*
      - model: string
      - api_key: string

### meta_deep_research.classify_query_adaptive
  Adaptive query classification that determines optimal research approach for any domain.
  input_schema:
      - query: string *REQUIRED*
      - model: string
      - api_key: string

### meta_deep_research.extract_entities_from_evidence_comprehensive
  Meta-level entity extraction that adapts to any domain, not just VC.
  input_schema:
      - all_evidence: array *REQUIRED*
      - subject: string *REQUIRED*
      - query: string *REQUIRED*
      - existing_entities: array
      - model: string
      - api_key: string

### meta_deep_research.extract_relationships_comprehensive
  Meta-level relationship extraction with iterative discovery.
  input_schema:
      - all_evidence: array *REQUIRED*
      - entities: array *REQUIRED*
      - query: string *REQUIRED*
      - model: string
      - api_key: string

### meta_deep_research.synthesize_key_discoveries_meta
  Meta-level discovery synthesis that adapts to any domain.
  input_schema:
      - query: string *REQUIRED*
      - all_evidence: array *REQUIRED*
      - entities: array *REQUIRED*
      - relationships: array *REQUIRED*
      - model: string
      - api_key: string

### meta_deep_research.generate_research_briefing
  Generates an interactive research briefing from a research package. Uses parallel AI calls to generate briefing components.
  input_schema:
      - package: any *REQUIRED*
      - main_query: string *REQUIRED*
      - model: string
      - api_key: string

### meta_deep_research.generate_document_from_package
  Delegates to the original intelligent publishing pipeline with identical prompts and logic.
  input_schema:
      - package: any *REQUIRED*
      - main_query: string *REQUIRED*
      - tension_lens: string
      - source_strictness: string
      - evidence_style: string
      - analysis_depth: string
      - model: string
      - api_key: string

### meta_deep_research.execute_deep_research
  End-to-end deep research pipeline that orchestrates the complete flow: 1. Prepares a comprehensive research package (iterative multi-stream research) 2. Generates a formatted document from the research findings
  input_schema:
      - query: string *REQUIRED*
      - mode: string
      - research_focus: integer
      - research_scope: integer
      - max_research_loops: integer
      - num_parallel_streams: integer
      - tension_lens: string
      - source_strictness: string
      - evidence_style: string
      - analysis_depth: string
      - model: string
      - api_key: string


## swe-planner — SWE-AF autonomous engineering fleet
- Base: https://swe.goodshepherdinsights.com (public) | http://localhost:8002 (local)
- Reasoners: 31
### swe-planner.implement_issue
  Issue-level build (sub-harness entry): implements ONE fully-scoped issue on an isolated branch of a local repo — no planning agents, ~4-8 LLM calls, minutes not hours. Give it issue{title, description, acceptance_criteria, files_to_*} plus repo_path; returns the deliverable branch. Prefer this over build when you already know exactly what to change.
  input_schema:
      - issue: any *REQUIRED*
      - repo_path: string *REQUIRED*
      - base_branch: string
      - artifacts_dir: string
      - additional_context: string
      - config: any

### swe-planner.build
  Feature-level build: plans a PRD → architecture → issue DAG, then codes, reviews, merges and verifies end-to-end. Give it a goal plus repo_path or repo_url; returns a verified feature branch (optionally a draft PR). Typical wall-clock 25-60 min. For one well-scoped change with known files, prefer implement_issue.
  input_schema:
      - goal: string *REQUIRED*
      - repo_path: string
      - repo_url: string
      - artifacts_dir: string
      - additional_context: string
      - config: any
      - execute_fn_target: string
      - max_turns: integer
      - permission_mode: string
      - enable_learning: boolean

### swe-planner.plan
  Run the full planning pipeline.
  input_schema:
      - goal: string *REQUIRED*
      - repo_path: string *REQUIRED*
      - artifacts_dir: string
      - additional_context: string
      - max_review_iterations: integer
      - pm_model: any
      - architect_model: any
      - tech_lead_model: any
      - sprint_planner_model: any
      - issue_writer_model: any
      - permission_mode: string
      - ai_provider: any
      - workspace_manifest: any

### swe-planner.execute
  Execute a planned DAG with self-healing replanning. Input plan_result comes from a prior plan call — not a hand-written object; prefer build unless you are resuming a custom pipeline.
  input_schema:
      - plan_result: any *REQUIRED*
      - repo_path: string *REQUIRED*
      - execute_fn_target: string
      - config: any
      - git_config: any
      - resume: boolean
      - build_id: string
      - workspace_manifest: any

### swe-planner.resolve
  Update an existing PR: merge base, fix CI, address review comments, push.
  input_schema:
      - pr_url: string *REQUIRED*
      - pr_number: integer *REQUIRED*
      - repo_url: string *REQUIRED*
      - head_branch: string *REQUIRED*
      - base_branch: string
      - ci_failures: any
      - review_comments: any
      - goal: string
      - additional_context: string
      - config: any

### swe-planner.resume_build
  Resume a crashed build from the last checkpoint.
  input_schema:
      - repo_path: string *REQUIRED*
      - artifacts_dir: string
      - config: any
      - git_config: any

  [internal, don't call: generate_fix_issues, run_architect, run_ci_fixer, run_ci_watcher, run_code_reviewer, run_coder, run_environment_scout, run_git_init, run_github_pr, run_integration_tester, run_issue_advisor, run_issue_writer, run_merger, run_pr_resolver, run_product_manager, run_qa, run_qa_synthesizer, run_replanner, run_repo_finalize, run_retry_advisor, run_sprint_planner, run_tech_lead, run_verifier, run_workspace_cleanup, run_workspace_setup]
