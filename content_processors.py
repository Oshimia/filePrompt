import re
import json

# --- Helper Functions for Content Processing ---

def remove_comments_from_line(line, comment_marker):
    """Removes comments from a single line given a single-line comment marker."""
    try:
        return line.split(comment_marker, 1)[0].rstrip()
    except:
        return line.rstrip()

def remove_c_style_multiline_comments(code):
    """Removes /* ... */ comments."""
    return re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)

def remove_html_xml_comments(code):
    """Removes <!-- ... --> comments."""
    return re.sub(r'<!--.*?-->', '', code, flags=re.DOTALL)

def process_code_content(content_str, file_ext):
    """Removes comments and normalizes whitespace for known code types."""
    lines = content_str.splitlines()
    processed_lines = []
    
    if file_ext in ['.js', '.jsw', '.css', '.c', '.cpp', '.java', '.cs', '.go', '.rs', '.swift', '.kt', '.scala', '.h', '.hpp']:
        content_str = remove_c_style_multiline_comments(content_str)
        lines = content_str.splitlines()

    if file_ext in ['.xml', '.html']:
        content_str = remove_html_xml_comments(content_str)
        lines = content_str.splitlines()

    in_python_multiline_string = False
    
    for i, line in enumerate(lines):
        original_line_for_shebang = line
        
        if file_ext in ['.py', '.sh', '.rb', '.pl', '.yml', '.yaml', '.ini', '.cfg', '.bat']:
            if file_ext == '.py':
                if '"""' in line:
                    if line.count('"""') % 2 != 0: 
                        in_python_multiline_string = not in_python_multiline_string
                elif "'''" in line:
                    if line.count("'''") % 2 != 0:
                        in_python_multiline_string = not in_python_multiline_string
            
            if not in_python_multiline_string and '#' in line:
                # NEW: Check if the '#' is inside a string
                idx = line.find('#')
                if line[:idx].count("'") % 2 == 0 and line[:idx].count('"') % 2 == 0:
                    if i == 0 and (original_line_for_shebang.startswith("#!") or original_line_for_shebang.startswith("::#")):
                         line = original_line_for_shebang.rstrip()
                    else:
                        stripped_line_for_hash = line.strip()
                        if stripped_line_for_hash.startswith('#'):
                            if not processed_lines or processed_lines[-1].strip() != "":
                                processed_lines.append("") 
                            continue
                        else:
                            line = remove_comments_from_line(line, '#')
                # If the '#' is in a string, do nothing and let the original line pass through.

            elif in_python_multiline_string and file_ext == '.py':
                pass

        elif file_ext in ['.js', '.jsw', '.c', '.cpp', '.java', '.cs', '.go', '.rs', '.swift', '.kt', '.scala', '.h', '.hpp']:
            if '//' in line:
                idx = line.find('//')
                single_quotes_before = line[:idx].count("'")
                double_quotes_before = line[:idx].count('"')
                if (single_quotes_before % 2 == 0) and (double_quotes_before % 2 == 0):
                    line = remove_comments_from_line(line, '//')
        
        if line.strip() or (processed_lines and processed_lines[-1].strip()):
            processed_lines.append(line.rstrip())

    final_lines = []
    for i, line_item in enumerate(processed_lines):
        if line_item.strip() == "" and (i > 0 and not final_lines[-1].strip()):
            continue 
        final_lines.append(line_item)
        
    return "\n".join(final_lines)