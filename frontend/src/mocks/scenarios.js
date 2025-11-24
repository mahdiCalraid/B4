export const SCENARIOS = [
    {
        trace_id: "mock-1",
        timestamp: new Date().toISOString(),
        input_preview: "Analyze: Tech market trends 2025",
        step_count: 8,
        steps: [
            {
                step_id: "step-1",
                node_name: "Router",
                input_data: { text: "Analyze: Tech market trends 2025" },
                output_data: { route: "AnalyzerModule", confidence: 0.98 },
                timestamp: new Date().toISOString()
            },
            {
                step_id: "step-2",
                node_name: "AnalyzerModule",
                input_data: { text: "Analyze: Tech market trends 2025" },
                output_data: { intent: "market_analysis", entities: ["Tech", "2025"] },
                parent_id: "step-1",
                timestamp: new Date().toISOString()
            },
            {
                step_id: "step-3",
                node_name: "SearchAgent",
                input_data: { query: "Tech market trends 2025" },
                output_data: { results: 15, source: "Google Search" },
                parent_id: "step-2",
                timestamp: new Date().toISOString()
            },
            {
                step_id: "step-4",
                node_name: "SentimentAnalysis",
                input_data: { text: "Search Results..." },
                output_data: { sentiment: "Positive", score: 0.85 },
                parent_id: "step-3",
                timestamp: new Date().toISOString()
            },
            {
                step_id: "step-5",
                node_name: "StatsExtractor",
                input_data: { text: "Search Results..." },
                output_data: { growth: "15%", sector: "AI" },
                parent_id: "step-3",
                timestamp: new Date().toISOString()
            },
            {
                step_id: "step-6",
                node_name: "SummaryAgent",
                input_data: { sentiment: "Positive", stats: { growth: "15%" } },
                output_data: { summary: "Tech sector showing strong growth driven by AI." },
                parent_id: "step-4", // Merging back
                timestamp: new Date().toISOString()
            },
            {
                step_id: "step-7",
                node_name: "Formatter",
                input_data: { summary: "..." },
                output_data: { format: "markdown" },
                parent_id: "step-6",
                timestamp: new Date().toISOString()
            },
            {
                step_id: "step-8",
                node_name: "Router",
                input_data: { result: "Final Report" },
                output_data: { status: "complete" },
                parent_id: "step-7",
                timestamp: new Date().toISOString()
            }
        ]
    },
    {
        trace_id: "mock-2",
        timestamp: new Date(Date.now() - 100000).toISOString(),
        input_preview: "Hello, who are you?",
        step_count: 3,
        steps: [
            {
                step_id: "m2-1",
                node_name: "Router",
                input_data: { text: "Hello, who are you?" },
                output_data: { route: "ChatAgentModule" },
                timestamp: new Date().toISOString()
            },
            {
                step_id: "m2-2",
                node_name: "ChatAgentModule",
                input_data: { text: "Hello, who are you?" },
                output_data: { response: "I am B4, your AI assistant." },
                parent_id: "m2-1",
                timestamp: new Date().toISOString()
            },
            {
                step_id: "m2-3",
                node_name: "Router",
                input_data: { response: "I am B4..." },
                output_data: { status: "sent" },
                parent_id: "m2-2",
                timestamp: new Date().toISOString()
            }
        ]
    },
    {
        trace_id: "mock-3",
        timestamp: new Date(Date.now() - 500000).toISOString(),
        input_preview: "Extract data from Twitter",
        step_count: 5,
        steps: [
            {
                step_id: "m3-1",
                node_name: "Router",
                input_data: { text: "Extract data from Twitter" },
                output_data: { route: "DataBotOrchestrator" },
                timestamp: new Date().toISOString()
            },
            {
                step_id: "m3-2",
                node_name: "DataBotOrchestrator",
                input_data: { source: "twitter" },
                output_data: { action: "initiate_extraction" },
                parent_id: "m3-1",
                timestamp: new Date().toISOString()
            },
            {
                step_id: "m3-3",
                node_name: "TwitterConnector",
                input_data: { auth: "valid" },
                output_data: { connection: "established" },
                parent_id: "m3-2",
                timestamp: new Date().toISOString()
            },
            {
                step_id: "m3-4",
                node_name: "StreamListener",
                input_data: { keywords: ["AI", "Crypto"] },
                output_data: { error: "Rate Limit Exceeded" },
                parent_id: "m3-3",
                timestamp: new Date().toISOString()
            },
            {
                step_id: "m3-5",
                node_name: "ErrorHandler",
                input_data: { error: "Rate Limit" },
                output_data: { action: "backoff", wait: "15m" },
                parent_id: "m3-4",
                timestamp: new Date().toISOString()
            }
        ]
    }
];
