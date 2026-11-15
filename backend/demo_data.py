"""
AgentProof AI — Demo Data
Pre-prepared sample evaluation for Demo Mode.

IMPORTANT:
- This data is CLEARLY LABELLED as demo/sample data throughout
- It NEVER mixes with live evaluation results
- It was NOT produced by real Bifrost or Tavily API calls
- It demonstrates the product concept for judges when APIs are unavailable
"""

DEMO_EVALUATION = {
    "id": "demo-evaluation-001",
    "task": "What is the current interest rate set by the US Federal Reserve, and how has it changed over the past year?",
    "task_category": "Research",
    "status": "completed",
    "demo_mode": True,
    "created_at": "2025-01-15T10:00:00Z",
    "completed_at": "2025-01-15T10:03:42Z",
    "note": "⚠️ DEMO MODE — All data below is pre-prepared sample data. No real API calls were made.",
    "models": [
        {
            "model_id": "openai/gpt-4o-mini",
            "display_name": "GPT-4o Mini",
            "provider": "openai",
            "status": "completed",
            "response_text": (
                "The Federal Reserve's target federal funds rate is currently set at 4.25% to 4.50%, "
                "as of January 2025. This represents a significant decline from the peak of 5.25%–5.50% "
                "maintained through most of 2023 and 2024. The Fed began cutting rates in September 2024 "
                "with a 50 basis point reduction, followed by additional cuts in November and December 2024. "
                "The Federal Reserve uses interest rate adjustments as its primary monetary policy tool to "
                "control inflation and support employment. As inflation has moderated toward the 2% target, "
                "the Fed has signaled a gradual easing cycle. However, economists are divided on how many "
                "additional cuts to expect in 2025, with some forecasting two to three cuts and others "
                "expecting the Fed to hold rates steady for longer."
            ),
            "latency_ms": 1842.5,
            "prompt_tokens": 85,
            "completion_tokens": 148,
            "total_tokens": 233,
            "estimated_cost_usd": 0.0001,
            "finish_reason": "stop",
            "trust_score": 72.5,
            "efficiency_score": 81.6,
            "task_completion_score": 0.78,
            "trust_score_explanation": "Trust Score: 3/5 verified claims × 100 − 1 contradicted × 15 − 1 outdated × 8 − 0 unverifiable × 3 + 0.78 × 20 = 72.5",
            "efficiency_score_explanation": "Latency 1842ms → 81.6pts (50%), 233 tokens → 95.3pts (30%), $0.0001 → 99.0pts (20%) = 81.6",
            "claims": [
                {
                    "text": "The Federal Reserve's target federal funds rate is currently 4.25% to 4.50%",
                    "type": "time_sensitive_factual",
                    "claim_index": 0,
                    "verification": {
                        "status": "SUPPORTED",
                        "explanation": "Multiple current sources confirm the Fed funds rate target was set at 4.25–4.50% at the December 2024 FOMC meeting.",
                        "evidence_summary": "Federal Reserve official statements and financial news sources confirm this rate range.",
                        "sources": [
                            {
                                "title": "Federal Reserve Press Release - December 2024",
                                "url": "https://www.federalreserve.gov/newsevents/pressreleases/monetary20241218a.htm",
                                "snippet": "The Federal Open Market Committee decided to lower the target range for the federal funds rate to 4-1/4 to 4-1/2 percent.",
                                "published_date": "2024-12-18",
                                "relevance_score": 0.98,
                            }
                        ],
                        "retrieved_at": "2025-01-15T10:01:30Z",
                    },
                },
                {
                    "text": "The Fed maintained a peak rate of 5.25%–5.50% through most of 2023 and 2024",
                    "type": "historical_factual",
                    "claim_index": 1,
                    "verification": {
                        "status": "SUPPORTED",
                        "explanation": "Historical records confirm the Fed maintained this peak rate range from July 2023 until September 2024.",
                        "evidence_summary": "Federal Reserve historical data confirms the rate was 5.25–5.50% from July 2023 to September 2024.",
                        "sources": [
                            {
                                "title": "FRED - Federal Funds Effective Rate",
                                "url": "https://fred.stlouisfed.org/series/FEDFUNDS",
                                "snippet": "Federal funds effective rate data showing 5.25–5.50% range maintained from July 2023.",
                                "published_date": None,
                                "relevance_score": 0.95,
                            }
                        ],
                        "retrieved_at": "2025-01-15T10:01:45Z",
                    },
                },
                {
                    "text": "The Fed began cutting rates in September 2024 with a 50 basis point reduction",
                    "type": "historical_factual",
                    "claim_index": 2,
                    "verification": {
                        "status": "SUPPORTED",
                        "explanation": "The September 2024 50bps rate cut is well-documented across multiple sources.",
                        "evidence_summary": "Federal Reserve announced a 50bps cut in September 2024, the first cut since March 2020.",
                        "sources": [
                            {
                                "title": "Fed Cuts Interest Rates by Half a Point - Reuters",
                                "url": "https://www.reuters.com/business/finance/fed-cuts-rates-50-bps-2024-09-18/",
                                "snippet": "The Federal Reserve cut interest rates by half a percentage point on Wednesday.",
                                "published_date": "2024-09-18",
                                "relevance_score": 0.97,
                            }
                        ],
                        "retrieved_at": "2025-01-15T10:02:00Z",
                    },
                },
                {
                    "text": "Inflation has moderated toward the 2% target",
                    "type": "time_sensitive_factual",
                    "claim_index": 3,
                    "verification": {
                        "status": "POTENTIALLY_OUTDATED",
                        "explanation": "While inflation has declined significantly from its peak, evidence suggests PCE inflation remained above 2.5% in late 2024, not fully at the 2% target.",
                        "evidence_summary": "PCE inflation was approximately 2.4% in November 2024, still above but approaching the 2% target.",
                        "sources": [
                            {
                                "title": "PCE Inflation Data - Bureau of Economic Analysis",
                                "url": "https://www.bea.gov/data/personal-consumption-expenditures-price-index",
                                "snippet": "Personal consumption expenditures price index shows inflation at 2.4% year-over-year.",
                                "published_date": "2024-12-20",
                                "relevance_score": 0.89,
                            }
                        ],
                        "retrieved_at": "2025-01-15T10:02:15Z",
                    },
                },
                {
                    "text": "Some economists are forecasting two to three rate cuts in 2025",
                    "type": "time_sensitive_factual",
                    "claim_index": 4,
                    "verification": {
                        "status": "CONTRADICTED",
                        "explanation": "Fed's own dot plot from December 2024 projected only two cuts in 2025, and some analysts revised this down further after strong economic data.",
                        "evidence_summary": "Fed dot plot (December 2024) suggests 2 cuts; some Wall Street analysts now forecasting just 1 cut.",
                        "sources": [
                            {
                                "title": "Fed Signals Fewer Rate Cuts in 2025 - Wall Street Journal",
                                "url": "https://www.wsj.com/economy/central-banking/fed-rate-cuts-2025-outlook",
                                "snippet": "Federal Reserve officials projected just two interest rate cuts for 2025, fewer than markets expected.",
                                "published_date": "2024-12-18",
                                "relevance_score": 0.91,
                            }
                        ],
                        "retrieved_at": "2025-01-15T10:02:30Z",
                    },
                },
            ],
        },
        {
            "model_id": "anthropic/claude-3-5-haiku-20241022",
            "display_name": "Claude 3.5 Haiku",
            "provider": "anthropic",
            "status": "completed",
            "response_text": (
                "As of December 2024, the Federal Reserve's target federal funds rate stands at 4.25% to 4.50%. "
                "Over the past year, the Fed has undergone a notable policy shift from a tightening to an easing stance. "
                "In 2023, rates were held at their peak of 5.25%–5.50%. The Fed initiated rate cuts in September 2024, "
                "reducing rates by 50 basis points (0.50 percentage points), then implemented two additional 25 basis "
                "point cuts in November and December 2024. This represents a total reduction of 100 basis points from "
                "the peak rate. The Federal Reserve's decisions are guided by its dual mandate of maintaining price "
                "stability (targeting 2% inflation) and maximizing employment. Core PCE inflation, the Fed's preferred "
                "measure, stood at approximately 2.8% as of November 2024. The Fed has indicated a more cautious "
                "approach to future rate cuts given persistent services inflation and a resilient labor market. "
                "Market participants are currently pricing in one to two rate cuts for 2025."
            ),
            "latency_ms": 3215.8,
            "prompt_tokens": 92,
            "completion_tokens": 183,
            "total_tokens": 275,
            "estimated_cost_usd": 0.000953,
            "finish_reason": "stop",
            "trust_score": 85.2,
            "efficiency_score": 61.3,
            "task_completion_score": 0.89,
            "trust_score_explanation": "Trust Score: 5/6 verified claims × 100 − 0 contradicted × 15 − 0 outdated × 8 − 1 unverifiable × 3 + 0.89 × 20 = 85.2",
            "efficiency_score_explanation": "Latency 3215ms → 67.8pts (50%), 275 tokens → 94.5pts (30%), $0.000953 → 90.5pts (20%) = 61.3",
            "claims": [
                {
                    "text": "The Federal Reserve's target federal funds rate stands at 4.25% to 4.50% as of December 2024",
                    "type": "time_sensitive_factual",
                    "claim_index": 0,
                    "verification": {
                        "status": "SUPPORTED",
                        "explanation": "Confirmed by Federal Reserve official communications from the December 2024 FOMC meeting.",
                        "evidence_summary": "Fed officially set the rate at 4.25–4.50% at the December 18, 2024 meeting.",
                        "sources": [
                            {
                                "title": "Federal Reserve Press Release - December 2024",
                                "url": "https://www.federalreserve.gov/newsevents/pressreleases/monetary20241218a.htm",
                                "snippet": "The FOMC voted to lower the target range for the federal funds rate to 4-1/4 to 4-1/2 percent.",
                                "published_date": "2024-12-18",
                                "relevance_score": 0.99,
                            }
                        ],
                        "retrieved_at": "2025-01-15T10:01:30Z",
                    },
                },
                {
                    "text": "Total reduction of 100 basis points from the peak rate",
                    "type": "historical_factual",
                    "claim_index": 1,
                    "verification": {
                        "status": "SUPPORTED",
                        "explanation": "Mathematically verifiable: 50bps (Sep) + 25bps (Nov) + 25bps (Dec) = 100bps total reduction.",
                        "evidence_summary": "Three cuts of 50, 25, and 25 basis points confirmed by Fed press releases.",
                        "sources": [
                            {
                                "title": "FOMC Meeting Results 2024 - Federal Reserve",
                                "url": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
                                "snippet": "FOMC calendar shows three rate cut decisions in 2024.",
                                "published_date": "2024-12-18",
                                "relevance_score": 0.96,
                            }
                        ],
                        "retrieved_at": "2025-01-15T10:01:50Z",
                    },
                },
                {
                    "text": "Core PCE inflation stood at approximately 2.8% as of November 2024",
                    "type": "time_sensitive_factual",
                    "claim_index": 2,
                    "verification": {
                        "status": "SUPPORTED",
                        "explanation": "BEA data confirms Core PCE at 2.8% year-over-year for November 2024.",
                        "evidence_summary": "Bureau of Economic Analysis reported Core PCE at 2.8% for November 2024.",
                        "sources": [
                            {
                                "title": "BEA Personal Income and Outlays Report",
                                "url": "https://www.bea.gov/data/personal-consumption-expenditures-price-index",
                                "snippet": "Core PCE price index increased 2.8 percent from one year ago.",
                                "published_date": "2024-12-20",
                                "relevance_score": 0.94,
                            }
                        ],
                        "retrieved_at": "2025-01-15T10:02:10Z",
                    },
                },
                {
                    "text": "Market participants are pricing in one to two rate cuts for 2025",
                    "type": "time_sensitive_factual",
                    "claim_index": 3,
                    "verification": {
                        "status": "SUPPORTED",
                        "explanation": "Fed futures markets as of late December 2024 were pricing approximately 1-2 cuts for 2025.",
                        "evidence_summary": "CME FedWatch tool showed 1-2 cuts priced in for 2025 as of end of December 2024.",
                        "sources": [
                            {
                                "title": "CME FedWatch Tool - Fed Rate Probabilities",
                                "url": "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html",
                                "snippet": "Fed funds futures contracts indicate market expects 1-2 rate cuts in 2025.",
                                "published_date": None,
                                "relevance_score": 0.88,
                            }
                        ],
                        "retrieved_at": "2025-01-15T10:02:25Z",
                    },
                },
                {
                    "text": "The Fed has a dual mandate of price stability and maximizing employment",
                    "type": "general_factual",
                    "claim_index": 4,
                    "verification": {
                        "status": "SUPPORTED",
                        "explanation": "This is a well-established fact about the Federal Reserve's statutory mandate under the Federal Reserve Act.",
                        "evidence_summary": "Federal Reserve's official mandate established by Congress is price stability and maximum employment.",
                        "sources": [
                            {
                                "title": "Federal Reserve - About the Fed",
                                "url": "https://www.federalreserve.gov/aboutthefed/mission.htm",
                                "snippet": "The Federal Reserve works to promote maximum employment, stable prices, and moderate long-term interest rates.",
                                "published_date": None,
                                "relevance_score": 0.99,
                            }
                        ],
                        "retrieved_at": "2025-01-15T10:02:40Z",
                    },
                },
                {
                    "text": "The Fed has indicated a more cautious approach due to persistent services inflation",
                    "type": "time_sensitive_factual",
                    "claim_index": 5,
                    "verification": {
                        "status": "UNVERIFIABLE",
                        "explanation": "While Fed communications do reference services inflation, specific caution framing varies across sources and cannot be definitively confirmed.",
                        "evidence_summary": "Some sources reference Fed hawkishness, but specific language about 'persistent services inflation' as a primary driver is not clearly confirmed.",
                        "sources": [
                            {
                                "title": "FOMC Minutes December 2024",
                                "url": "https://www.federalreserve.gov/monetarypolicy/fomcminutes20241218.htm",
                                "snippet": "Participants noted that inflation remained somewhat elevated and discussed the path forward for rates.",
                                "published_date": "2025-01-08",
                                "relevance_score": 0.72,
                            }
                        ],
                        "retrieved_at": "2025-01-15T10:02:55Z",
                    },
                },
            ],
        },
    ],
}


def get_demo_evaluation():
    """Return the demo evaluation data with clear labelling."""
    return DEMO_EVALUATION
