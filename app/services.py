import ast

def analyze_code(code_snippet: str) -> list:
    suggestions = []

    try:
        # Tenta analisar o código em formato de árvore de sintaxe abstrata (AST)
        tree = ast.parse(code_snippet)
    except SyntaxError as e:
        suggestions.append(f"Erro de sintaxe: {e}")
        return suggestions

    # Verificar uso de eval
    if "eval" in code_snippet:
        suggestions.append("Evite usar 'eval' devido a riscos de segurança. Use alternativas seguras como 'ast.literal_eval'.")

    # Verificar uso de exec
    if "exec" in code_snippet:
        suggestions.append("Evite usar 'exec', pois pode introduzir vulnerabilidades de segurança.")

    # Verificar comentários ausentes
    if len(code_snippet.splitlines()) > 5 and "#" not in code_snippet:
        suggestions.append("Considere adicionar comentários para melhorar a clareza do código.")

    # Verificar variáveis com nomes pouco descritivos
    short_variable_names = [node.id for node in ast.walk(tree) if isinstance(node, ast.Name) and len(node.id) < 3]
    if short_variable_names:
        suggestions.append(f"Evite usar nomes de variáveis muito curtos ({', '.join(short_variable_names)}). Use nomes mais descritivos.")

    # Verificar complexidade do código
    if len(code_snippet.splitlines()) > 20:
        suggestions.append("O código tem muitas linhas. Considere dividir em funções menores para melhorar a legibilidade.")

    # Verificar uso de imports não utilizados
    imports = [node.name for node in ast.walk(tree) if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom)]
    used_names = [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]
    unused_imports = [imp for imp in imports if imp not in used_names]
    if unused_imports:
        suggestions.append(f"Remova imports não utilizados: {', '.join(unused_imports)}.")

    # Verificar funções sem docstrings
    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    for func in functions:
        if not ast.get_docstring(func):
            suggestions.append(f"A função '{func.name}' não possui docstring. Considere adicionar uma descrição.")

    # Verificar uso de listas aninhadas ou loops complexos
    nested_loops = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.For) and any(isinstance(child, ast.For) for child in ast.iter_child_nodes(node))
    ]
    if nested_loops:
        suggestions.append("Evite loops aninhados profundos. Considere simplificar a lógica.")

    # Se nenhuma sugestão foi gerada
    if not suggestions:
        suggestions.append("O código segue boas práticas. Nenhuma melhoria necessária.")

    return suggestions
