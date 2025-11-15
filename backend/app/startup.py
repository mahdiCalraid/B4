"""Startup tasks for the application."""

from modules.registry import registry


def register_modules():
    """
    Register all available modules on application startup.

    This function discovers and registers all modules so they're
    available for routing and processing.
    """
    print("\n" + "="*70)
    print("📦 Registering Modules")
    print("="*70)

    # Import and register interactive modules
    try:
        from modules.interactive.chat_agent.module import ChatAgentModule
        registry.register(ChatAgentModule)
    except ImportError as e:
        print(f"⚠️  Could not import ChatAgentModule: {e}")

    try:
        from modules.interactive.analyzer.module import AnalyzerModule
        registry.register(AnalyzerModule)
    except ImportError as e:
        print(f"⚠️  Could not import AnalyzerModule: {e}")

    # Register new AI Chat module with multi-provider support
    try:
        from modules.interactive.ai_chat.module import AIChatModule
        registry.register(AIChatModule)
        print("✅ Registered AIChatModule (Gemini, OpenAI, Groq, Ollama)")
    except ImportError as e:
        print(f"⚠️  Could not import AIChatModule: {e}")

    # Future: Add more modules here as they are created
    # from modules.background.news_scraper.module import NewsScraperModule
    # registry.register(NewsScraperModule)

    print(f"\n✅ Total modules registered: {registry.get_module_count()}")
    print("="*70 + "\n")


def startup():
    """Run all startup tasks."""
    register_modules()
