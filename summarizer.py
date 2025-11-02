import json
from content_processors import process_code_content

def _get_full_content(content_str, file_ext, config):
    """Processes the full content of a file by cleaning comments and whitespace."""
    processed_content = process_code_content(content_str, file_ext)
    return [f"  ---[FILE_CONTENT]---", processed_content]

def _summarize_json(content_str, filename, config):
    """Creates a compact summary for specific JSON files, otherwise returns full content."""
    try:
        data = json.loads(content_str)
        summary = None

        if filename == "package.json":
            summary = {
                "name": data.get("name"),
                "version": data.get("version"),
                "dependencies": data.get("dependencies"),
                "devDependencies": data.get("devDependencies"),
                "scripts": data.get("scripts")
            }
            summary = {k: v for k, v in summary.items() if v is not None}
        elif filename in ["jsconfig.json", "tsconfig.json"]:
            summary = {
                "compilerOptions_paths": data.get("compilerOptions", {}).get("paths"),
                "references": data.get("references"),
                "include": data.get("include"),
                "exclude": data.get("exclude")
            }
            summary = {k: v for k, v in summary.items() if v is not None}

        if summary:
            compact_json = json.dumps(summary, separators=(',', ':'))
            return [f"  [SUMMARY_JSON] {compact_json}"]

    except json.JSONDecodeError:
        # Malformed JSON, fall back to full content
        pass

    # If not a special JSON or if it's malformed, treat as regular text
    return _get_full_content(content_str, '.json', config)


STRATEGIES = {
    "full_content": _get_full_content,
    "summarize_json": _summarize_json,
}

def summarize_file(content_str, filename, config):
    """
    Summarizes or processes file content based on rules in the configuration.
    """
    file_ext = f".{filename.split('.')[-1]}" if '.' in filename else ''
    rules = config.get("summarization_rules", {})
    
    # Check for filename-specific rule
    strategy_name = rules.get("by_filename", {}).get(filename)
    
    # If no filename rule, check for extension-specific rule
    if not strategy_name:
        strategy_name = rules.get("by_extension", {}).get(file_ext)

    # Fallback to default strategy
    strategy_name = strategy_name or rules.get("default_strategy", "full_content")
    
    strategy_func = STRATEGIES.get(strategy_name, _get_full_content)
    
    return strategy_func(content_str, filename if strategy_name == "summarize_json" else file_ext, config)