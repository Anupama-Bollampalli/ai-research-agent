"""
Mock tools for the AI Research Agent.
Each tool returns realistic, detailed responses based on detected keywords.
"""
from __future__ import annotations

import math
import re


# ---------------------------------------------------------------------------
# Topic knowledge base
# ---------------------------------------------------------------------------

_TOPIC_DB: dict[str, list[dict]] = {
    "ai_ml": [
        {
            "title": "Advances in Large Language Models: GPT-4, Claude, and Beyond",
            "url": "https://arxiv.org/abs/2303.08774",
            "snippet": (
                "Large language models (LLMs) have demonstrated remarkable capabilities across "
                "a wide range of tasks, from code generation to scientific reasoning. Recent "
                "scaling studies show emergent abilities appear at certain parameter thresholds, "
                "suggesting qualitative phase transitions in model behaviour rather than smooth "
                "interpolation."
            ),
        },
        {
            "title": "Transformer Architecture Deep Dive: Attention Mechanisms Explained",
            "url": "https://towardsdatascience.com/transformer-architecture-attention-2024",
            "snippet": (
                "Self-attention allows transformers to weigh the importance of each token "
                "relative to every other token in a sequence. Multi-head attention runs "
                "several attention operations in parallel, each focusing on different "
                "representation subspaces, enabling richer contextual understanding."
            ),
        },
        {
            "title": "AI Safety and Alignment: Current Research Directions",
            "url": "https://www.alignmentforum.org/posts/ai-safety-overview-2024",
            "snippet": (
                "Constitutional AI, RLHF, and debate-based alignment are among the most "
                "actively researched safety techniques. Key open problems include reward "
                "hacking, distributional shift, and scalable oversight — ensuring that "
                "human evaluators can reliably assess model outputs as AI capabilities grow."
            ),
        },
    ],
    "rag": [
        {
            "title": "Retrieval-Augmented Generation: Techniques and Best Practices",
            "url": "https://research.google/pubs/rag-survey-2024",
            "snippet": (
                "RAG combines dense retrieval with generative language models to ground "
                "responses in external knowledge. Typical pipelines chunk documents into "
                "256–512 token segments, embed them with models like text-embedding-3-large, "
                "index them in vector stores such as Pinecone or pgvector, and retrieve "
                "top-k passages at query time before generation."
            ),
        },
        {
            "title": "Vector Database Comparison: Pinecone vs. Weaviate vs. Chroma",
            "url": "https://towardsdatascience.com/vector-db-comparison-2024",
            "snippet": (
                "Pinecone offers fully managed hosting with sub-10 ms p99 latency at scale; "
                "Weaviate supports hybrid BM25 + vector search natively; Chroma excels for "
                "local development with a simple Python API. HNSW indexing is the de-facto "
                "standard for approximate nearest-neighbour search across all major vendors."
            ),
        },
        {
            "title": "Chunking Strategies for RAG Pipelines",
            "url": "https://www.llamaindex.ai/blog/chunking-strategies-rag",
            "snippet": (
                "Choosing the right chunking strategy significantly impacts retrieval quality. "
                "Fixed-size chunking is simple but ignores semantic boundaries; "
                "sentence-window retrieval preserves context around matched sentences; "
                "hierarchical chunking stores both paragraph and document-level summaries "
                "to answer both fine-grained and broad queries."
            ),
        },
    ],
    "data_engineering": [
        {
            "title": "Modern Data Stack 2024: dbt, Airflow, and the Lakehouse Pattern",
            "url": "https://www.databricks.com/blog/modern-data-stack-2024",
            "snippet": (
                "The lakehouse architecture unifies the flexibility of data lakes with the "
                "ACID transactions and schema enforcement of data warehouses. Apache Iceberg "
                "and Delta Lake provide the open table formats, while dbt Core handles "
                "SQL-based transformations and Airflow orchestrates pipeline DAGs."
            ),
        },
        {
            "title": "Apache Spark vs. DuckDB for Analytical Workloads",
            "url": "https://duckdb.org/2024/comparison-spark-duckdb",
            "snippet": (
                "DuckDB's vectorised execution engine processes analytical queries up to "
                "10× faster than Spark on single-node workloads under 100 GB. For distributed "
                "petabyte-scale processing, Spark remains the industry standard, especially "
                "when combined with Delta Lake for transactional consistency."
            ),
        },
        {
            "title": "Real-Time Data Pipelines with Apache Kafka and Flink",
            "url": "https://kafka.apache.org/documentation/streams",
            "snippet": (
                "Kafka Streams and Apache Flink enable sub-second latency event-driven "
                "architectures. Flink's watermark mechanism handles out-of-order events "
                "gracefully, while exactly-once semantics ensure no duplicate processing — "
                "critical for financial transactions and operational analytics."
            ),
        },
    ],
    "cloud": [
        {
            "title": "AWS vs. GCP vs. Azure: 2024 Comparison for ML Workloads",
            "url": "https://cloud.google.com/blog/compare-cloud-providers-ml-2024",
            "snippet": (
                "Google Cloud's TPU v4 pods deliver the highest throughput for large model "
                "training; AWS SageMaker offers the most mature MLOps ecosystem; "
                "Azure ML integrates tightly with Microsoft 365 and Active Directory. "
                "Spot/preemptible instances can cut training costs by 60–80%."
            ),
        },
        {
            "title": "Kubernetes Cost Optimisation Strategies at Scale",
            "url": "https://kubernetes.io/blog/cost-optimization-2024",
            "snippet": (
                "Cluster autoscaling, right-sizing with Vertical Pod Autoscaler, and "
                "workload bin-packing are the top three cost levers in Kubernetes. Teams "
                "combining node auto-provisioning with spot instance pools report average "
                "infrastructure savings of 45% without degrading availability SLAs."
            ),
        },
        {
            "title": "Serverless vs. Containers: Choosing the Right Compute Model",
            "url": "https://aws.amazon.com/blogs/architecture/serverless-vs-containers",
            "snippet": (
                "Serverless functions excel for event-driven workloads with spiky traffic "
                "patterns — cold start latency has dropped to under 100 ms for most runtimes. "
                "Containers remain preferable for long-running services, stateful workloads, "
                "and applications requiring consistent sub-millisecond tail latencies."
            ),
        },
    ],
    "python": [
        {
            "title": "Python 3.12 Performance Improvements and New Features",
            "url": "https://docs.python.org/3.12/whatsnew/3.12.html",
            "snippet": (
                "Python 3.12 delivers a 5% average speedup over 3.11 through specialised "
                "bytecode and improved comprehension inlining. New features include "
                "f-string nesting, per-interpreter GIL (PEP 684), and improved error "
                "messages that point directly to the offending token."
            ),
        },
        {
            "title": "Async Python in Production: asyncio, httpx, and FastAPI",
            "url": "https://fastapi.tiangolo.com/async/",
            "snippet": (
                "Async Python enables handling thousands of concurrent I/O-bound requests "
                "with a single thread. FastAPI leverages Starlette's ASGI internals, "
                "delivering OpenAPI docs generation, Pydantic validation, and dependency "
                "injection out of the box — often matching Go performance for API workloads."
            ),
        },
        {
            "title": "Python Packaging in 2024: uv, Poetry, and pyproject.toml",
            "url": "https://packaging.python.org/en/latest/",
            "snippet": (
                "The Astral `uv` tool written in Rust resolves and installs packages "
                "10–100× faster than pip. Poetry remains popular for its lockfile and "
                "virtualenv management, while pyproject.toml is now the single source "
                "of truth for project metadata per PEP 621."
            ),
        },
    ],
    "web_dev": [
        {
            "title": "React 19 Features: Server Components, Actions, and Compiler",
            "url": "https://react.dev/blog/2024/react-19",
            "snippet": (
                "React 19 stabilises Server Components for zero-bundle-size server-rendered "
                "primitives, introduces the new Actions API for async state transitions, and "
                "ships the React Compiler (formerly React Forget) which automatically memoises "
                "components — eliminating most manual useMemo and useCallback calls."
            ),
        },
        {
            "title": "Next.js 14 App Router: Performance and Caching Deep Dive",
            "url": "https://nextjs.org/blog/next-14",
            "snippet": (
                "Next.js 14 defaults to static rendering where possible and introduces Partial "
                "Pre-rendering (PPR), combining static shells with streaming dynamic content. "
                "The new cache() API enables fine-grained request deduplication and "
                "time-based revalidation without manual SWR logic."
            ),
        },
        {
            "title": "Web Performance 2024: Core Web Vitals and INP Optimisation",
            "url": "https://web.dev/performance-2024",
            "snippet": (
                "Interaction to Next Paint (INP) replaced First Input Delay as a Core Web "
                "Vital in March 2024. Optimising INP requires minimising long tasks on the "
                "main thread, yielding to the browser with scheduler.yield(), and deferring "
                "non-critical JavaScript via dynamic import()."
            ),
        },
    ],
    "machine_learning": [
        {
            "title": "Diffusion Models Explained: From DDPM to Stable Diffusion",
            "url": "https://lilianweng.github.io/posts/diffusion-models-2024",
            "snippet": (
                "Diffusion models iteratively denoise Gaussian noise to generate high-fidelity "
                "images. The key insight of DDIM sampling is that the reverse process can be "
                "made deterministic, reducing inference steps from 1000 to 20–50 without "
                "quality loss. LoRA fine-tuning allows adapting Stable Diffusion to new "
                "styles with as few as 10–20 example images."
            ),
        },
        {
            "title": "Gradient Descent Optimisers: Adam, AdamW, and Lion Compared",
            "url": "https://arxiv.org/abs/2302.06675",
            "snippet": (
                "AdamW decouples weight decay from gradient updates, improving generalisation "
                "for transformer training. Google's Lion optimiser uses sign descent and "
                "achieves comparable accuracy to AdamW with 2–3× smaller memory footprint, "
                "making it attractive for large-scale model training."
            ),
        },
        {
            "title": "Model Evaluation Benchmarks: MMLU, HumanEval, and HELM",
            "url": "https://crfm.stanford.edu/helm/latest/",
            "snippet": (
                "MMLU tests knowledge across 57 academic domains; HumanEval measures code "
                "generation on 164 programming problems; HELM provides holistic evaluation "
                "across accuracy, calibration, robustness, and fairness dimensions. "
                "No single benchmark captures real-world performance — multi-benchmark "
                "suites are now the research community standard."
            ),
        },
    ],
    "nlp": [
        {
            "title": "Named Entity Recognition with SpaCy and Transformers in 2024",
            "url": "https://spacy.io/usage/training",
            "snippet": (
                "Modern NER combines rule-based gazetteer matching with transformer-based "
                "contextual embeddings. SpaCy v3's component architecture allows stacking "
                "a Roberta-based tok2vec with CRF decoding, achieving F1 > 0.92 on CoNLL-2003. "
                "Active learning loops cut annotation cost by 50% by selecting high-uncertainty "
                "examples for human review."
            ),
        },
        {
            "title": "Sentiment Analysis at Scale: From VADER to LLM-based Classifiers",
            "url": "https://huggingface.co/blog/sentiment-analysis-2024",
            "snippet": (
                "Fine-tuned DistilBERT achieves 0.94 F1 on SST-2 at 20k inferences/second "
                "on a single A100. For aspect-level sentiment (e.g. 'battery life' sentiment "
                "in product reviews), instruction-tuned LLMs outperform discriminative models "
                "by 8–12 F1 points with no labelled data."
            ),
        },
        {
            "title": "Machine Translation: NLLB-200 and the State of Low-Resource Languages",
            "url": "https://ai.meta.com/research/no-language-left-behind/",
            "snippet": (
                "Meta's NLLB-200 covers 200 languages, including 55 African languages with "
                "previously no MT support. Sparsely gated mixture-of-experts allows the model "
                "to scale to 54B parameters while keeping inference cost comparable to a 1.3B "
                "dense model through conditional computation."
            ),
        },
    ],
    "databases": [
        {
            "title": "PostgreSQL 16 Features: Logical Replication, MERGE, and Performance",
            "url": "https://www.postgresql.org/docs/16/release-16.html",
            "snippet": (
                "PostgreSQL 16 introduces bidirectional logical replication, allowing "
                "multi-primary write topologies for the first time. The MERGE command now "
                "fully conforms to SQL:2023, and query parallelism improvements deliver "
                "up to 30% speedup on aggregation-heavy analytical queries."
            ),
        },
        {
            "title": "ClickHouse vs. BigQuery for Analytical Queries",
            "url": "https://clickhouse.com/blog/clickhouse-vs-bigquery-2024",
            "snippet": (
                "ClickHouse processes billions of rows per second on commodity hardware using "
                "its columnar MergeTree storage engine and vectorised execution. BigQuery "
                "excels for ad-hoc queries on managed petabyte datasets with its serverless "
                "model, while ClickHouse is preferred for latency-sensitive dashboards "
                "requiring sub-second query response."
            ),
        },
        {
            "title": "Redis 7.2: Redis Functions, Sharded Pub/Sub, and ACL Improvements",
            "url": "https://redis.io/blog/redis-7-2-release/",
            "snippet": (
                "Redis Functions replace Lua scripting with a library-based model that persists "
                "across server restarts. Sharded Pub/Sub distributes subscription load across "
                "cluster nodes, enabling horizontal scaling of real-time messaging. The new "
                "ACL selector syntax allows fine-grained per-command permissions."
            ),
        },
    ],
    "devops": [
        {
            "title": "GitOps with ArgoCD: Declarative Kubernetes Deployments",
            "url": "https://argo-cd.readthedocs.io/en/stable/",
            "snippet": (
                "GitOps treats Git as the single source of truth for cluster state. ArgoCD "
                "continuously reconciles desired state (Helm charts, Kustomize overlays) with "
                "live cluster state, auto-syncing or alerting on drift. Progressive delivery "
                "with Argo Rollouts enables canary deployments with automated metric-based "
                "promotion gates."
            ),
        },
        {
            "title": "Observability in 2024: OpenTelemetry, Grafana Stack, and eBPF",
            "url": "https://opentelemetry.io/blog/observability-2024",
            "snippet": (
                "OpenTelemetry has become the vendor-neutral standard for traces, metrics, and "
                "logs. eBPF-based agents like Grafana Beyla auto-instrument services without "
                "code changes by hooking into kernel syscalls. The LGTM stack — Loki, Grafana, "
                "Tempo, Mimir — provides a cost-effective open-source alternative to Datadog."
            ),
        },
        {
            "title": "Platform Engineering: Internal Developer Platforms and Backstage",
            "url": "https://backstage.io/blog/platform-engineering-2024",
            "snippet": (
                "Platform engineering shifts infrastructure complexity to a dedicated team "
                "that builds golden paths for application developers. Spotify's Backstage "
                "provides a service catalog, TechDocs, and scaffolder plugins that reduce "
                "onboarding time from weeks to hours. Key metrics include deployment frequency, "
                "change failure rate, and time-to-restore."
            ),
        },
    ],
    "business_analytics": [
        {
            "title": "Business Intelligence in 2024: Looker, Metabase, and Embedded Analytics",
            "url": "https://looker.com/blog/bi-trends-2024",
            "snippet": (
                "Self-service BI adoption has accelerated with natural language query interfaces "
                "powered by LLMs. Looker's semantic layer abstracts SQL complexity, enabling "
                "business users to ask questions in plain English. Embedded analytics — "
                "surfacing charts directly in operational tools — is growing faster than "
                "standalone BI dashboards."
            ),
        },
        {
            "title": "A/B Testing at Scale: Causal Inference and Experimentation Platforms",
            "url": "https://netflixtechblog.com/experimentation-platform-2024",
            "snippet": (
                "Modern experimentation platforms handle metric variance reduction via CUPED "
                "(Controlled-experiment Using Pre-Experiment Data), cutting required sample "
                "sizes by 30–50%. Switchback experiments handle interference in marketplace "
                "settings where user actions affect other users."
            ),
        },
        {
            "title": "Revenue Forecasting with ML: ARIMA, Prophet, and Neural Forecasters",
            "url": "https://unit8.com/resources/forecasting-comparison-2024",
            "snippet": (
                "Meta's Prophet handles seasonality and holidays out of the box with minimal "
                "tuning. Neural forecasters like N-BEATS and PatchTST outperform statistical "
                "baselines on long-horizon predictions. Probabilistic forecasting — outputting "
                "prediction intervals rather than point estimates — is increasingly required "
                "for financial planning."
            ),
        },
    ],
}

# Keyword → topic mapping (order matters: check more specific topics first)
_KEYWORD_MAP: list[tuple[list[str], str]] = [
    (["rag", "retrieval", "vector", "embedding", "chunk", "pinecone", "weaviate", "chroma"], "rag"),
    (["llm", "gpt", "claude", "transformer", "language model", "attention", "bert", "openai", "anthropic"], "ai_ml"),
    (["spark", "kafka", "flink", "airflow", "dbt", "pipeline", "lakehouse", "etl", "data engineering"], "data_engineering"),
    (["aws", "gcp", "azure", "kubernetes", "k8s", "cloud", "serverless", "docker", "container"], "cloud"),
    (["python", "asyncio", "fastapi", "pip", "poetry", "uv"], "python"),
    (["react", "next.js", "typescript", "javascript", "css", "html", "frontend", "web dev"], "web_dev"),
    (["diffusion", "neural network", "gradient", "training", "fine-tune", "lora", "cnn", "rnn", "lstm", "reinforcement"], "machine_learning"),
    (["nlp", "sentiment", "ner", "translation", "tokeniz", "spacy", "hugging face", "bert", "text classification"], "nlp"),
    (["postgres", "mysql", "redis", "clickhouse", "database", "sql", "nosql", "mongodb", "cassandra"], "databases"),
    (["devops", "gitops", "ci/cd", "argocd", "helm", "terraform", "ansible", "observability", "monitoring"], "devops"),
    (["analytics", "dashboard", "bi ", "looker", "tableau", "forecast", "a/b test", "revenue", "metric"], "business_analytics"),
    (["machine learning", "ml ", " ml", "model", "algorithm", "predict"], "machine_learning"),
    (["artificial intelligence", " ai ", "deep learning", "neural", "inference"], "ai_ml"),
]


def _detect_topic(query: str) -> str:
    """Return the most relevant topic key for the given query string."""
    q = query.lower()
    for keywords, topic in _KEYWORD_MAP:
        if any(kw in q for kw in keywords):
            return topic
    # Default fallback
    return "ai_ml"


# ---------------------------------------------------------------------------
# Tool 1: web_search
# ---------------------------------------------------------------------------

def web_search(query: str) -> list[dict]:
    """Return 3 realistic search results relevant to the query."""
    topic = _detect_topic(query)
    results = _TOPIC_DB[topic]
    # Inject the actual query into the first snippet for realism
    query_preview = query[:60] + ("..." if len(query) > 60 else "")
    enriched = []
    for i, r in enumerate(results):
        entry = dict(r)
        if i == 0:
            entry["snippet"] = (
                f"Top result for '{query_preview}': " + entry["snippet"]
            )
        enriched.append(entry)
    return enriched


# ---------------------------------------------------------------------------
# Tool 2: calculator
# ---------------------------------------------------------------------------

# Allowed names for safe eval
_SAFE_MATH_NAMES = {
    name: getattr(math, name)
    for name in dir(math)
    if not name.startswith("_")
}
_SAFE_MATH_NAMES.update({"abs": abs, "round": round, "pow": pow, "min": min, "max": max})
_ALLOWED_CHARS = re.compile(r"^[\d\s\+\-\*/\(\)\.\^eE,]+$")


def _is_safe_expression(expr: str) -> bool:
    # Allow math function names + standard operators/digits
    cleaned = expr.strip()
    # Remove known math function names for the character check
    temp = cleaned
    for name in _SAFE_MATH_NAMES:
        temp = temp.replace(name, "")
    return bool(_ALLOWED_CHARS.match(temp)) or bool(
        re.match(r"^[\w\s\+\-\*/\(\)\.\^,]+$", cleaned)
        and not any(kw in cleaned for kw in ["import", "exec", "eval", "open", "__", "os", "sys"])
    )


def calculator(expression: str) -> dict:
    """Safely evaluate a mathematical expression and return the result."""
    expr = expression.strip()
    # Block obviously dangerous patterns
    dangerous = ["import", "exec", "eval", "open", "__", "os", "sys", "subprocess", "globals", "locals"]
    if any(kw in expr.lower() for kw in dangerous):
        return {"error": "Expression contains disallowed keywords.", "expression": expr}
    try:
        result = eval(expr, {"__builtins__": {}}, _SAFE_MATH_NAMES)  # noqa: S307
        if isinstance(result, complex):
            return {"result": str(result), "expression": expr}
        rounded = round(float(result), 10) if isinstance(result, float) else result
        return {"result": rounded, "expression": expr}
    except ZeroDivisionError:
        return {"error": "Division by zero.", "expression": expr}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc), "expression": expr}


# ---------------------------------------------------------------------------
# Tool 3: text_summarizer
# ---------------------------------------------------------------------------

def text_summarizer(text: str) -> dict:
    """Summarise text by extracting the first 2 sentences and the last sentence."""
    text = text.strip()
    if not text:
        return {"summary": "", "original_length": 0, "summary_length": 0}

    # Split on sentence-ending punctuation followed by whitespace or end-of-string
    sentence_pattern = re.compile(r"(?<=[.!?])\s+")
    sentences = [s.strip() for s in sentence_pattern.split(text) if s.strip()]

    if len(sentences) <= 3:
        summary = text
    elif len(sentences) == 4:
        summary = " ".join(sentences[:2]) + " ... " + sentences[-1]
    else:
        summary = " ".join(sentences[:2]) + " ... " + sentences[-1]

    return {
        "summary": summary,
        "original_length": len(text),
        "summary_length": len(summary),
    }


# ---------------------------------------------------------------------------
# Tool 4: fact_checker
# ---------------------------------------------------------------------------

_VERDICT_EXPLANATIONS: list[tuple[str, str, str]] = [
    # (verdict, base_explanation_template, confidence_range)
    (
        "Likely True",
        (
            "This claim is consistent with widely-accepted information in the field. "
            "Multiple reputable sources corroborate the core assertion, though specific "
            "numerical figures may vary by study or measurement methodology."
        ),
        "high",
    ),
    (
        "Partially True",
        (
            "The claim contains accurate elements but oversimplifies a nuanced picture. "
            "Context-dependent factors and exceptions exist that the statement does not "
            "acknowledge, which could lead to misinterpretation without additional detail."
        ),
        "medium",
    ),
    (
        "Unverified",
        (
            "Insufficient peer-reviewed or authoritative evidence exists to confirm or "
            "refute this claim with high confidence. The assertion may be based on "
            "preliminary research, anecdotal reports, or rapidly evolving circumstances "
            "where consensus has not yet formed."
        ),
        "low",
    ),
]


def fact_checker(claim: str) -> dict:
    """Assess the plausibility of a claim and return a confidence score and verdict."""
    claim = claim.strip()
    length = len(claim)
    word_count = len(claim.split())

    # Heuristic: longer, more specific claims with numbers get higher confidence
    has_numbers = bool(re.search(r"\d+", claim))
    has_specific_terms = bool(
        re.search(
            r"\b(percent|%|billion|million|study|research|published|journal|university|institute)\b",
            claim,
            re.IGNORECASE,
        )
    )
    is_absolute = bool(re.search(r"\b(always|never|all|none|every|only)\b", claim, re.IGNORECASE))

    # Build confidence score
    base_confidence = 70
    if word_count > 15:
        base_confidence += 8
    if has_numbers:
        base_confidence += 7
    if has_specific_terms:
        base_confidence += 5
    if is_absolute:
        base_confidence -= 20  # Absolute claims are harder to fully verify
    if length < 40:
        base_confidence -= 10  # Very short claims are vague

    # Clamp between 50–95
    confidence = max(50, min(95, base_confidence))

    # Select verdict
    if confidence >= 75:
        verdict_entry = _VERDICT_EXPLANATIONS[0]  # Likely True
    elif confidence >= 60:
        verdict_entry = _VERDICT_EXPLANATIONS[1]  # Partially True
    else:
        verdict_entry = _VERDICT_EXPLANATIONS[2]  # Unverified

    verdict, explanation, _ = verdict_entry

    return {
        "claim": claim,
        "confidence": confidence,
        "verdict": verdict,
        "explanation": explanation,
    }
