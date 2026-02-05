import os
import argparse
import re

def parse_proposal(filepath):
    """
    Parses a proposal file to extract the Core and Title.
    """
    filename = os.path.basename(filepath)
    # Extract Title from filename: "proposta_Title_Here.txt" -> "Title Here"
    # Replace underscores with spaces for readability
    title = filename.replace("proposta_", "").replace(".txt", "").replace("_", " ")

    core = "Unknown"

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Look for "--- PROPOSTA GERADA (Núcleo: X) ---"
            match = re.search(r"--- PROPOSTA GERADA \(Núcleo: (.*?)\) ---", content)
            if match:
                core = match.group(1).strip()
    except Exception as e:
        print(f"[WARN] Erro ao ler {filename}: {e}")

    return {
        "title": title,
        "core": core
    }

def generate_report(directory):
    """
    Scans the directory and generates the ASCII report.
    """
    if not os.path.exists(directory):
        print(f"[ERROR] Diretório não encontrado: {directory}")
        return

    files = [f for f in os.listdir(directory) if f.startswith("proposta_") and f.endswith(".txt")]

    if not files:
        print(f"[INFO] Nenhuma proposta encontrada em {directory}.")
        return

    data = []
    stats = {"Data": 0, "Tech": 0, "Marketing": 0}

    for f in files:
        filepath = os.path.join(directory, f)
        info = parse_proposal(filepath)
        data.append(info)

        # Update stats
        core_key = info['core']
        if core_key in stats:
            stats[core_key] += 1
        else:
            # Handle unknown cores if any
            stats[core_key] = stats.get(core_key, 0) + 1

    # Sort by Core for cleaner viewing
    data.sort(key=lambda x: x['core'])

    # Print Report
    print("\n" + "="*60)
    print(f"📄 RELATÓRIO DE GUERRA - {len(data)} PROPOSTAS GERADAS")
    print("="*60)

    # Table Header
    # Format: # | CORE | TITLE
    header = f"{'#':<3} | {'NÚCLEO':<10} | {'TÍTULO DA VAGA'}"
    print(header)
    print("-" * len(header) + "-" * 20) # Divider

    for i, item in enumerate(data, 1):
        # Truncate title if too long for terminal
        title_display = (item['title'][:50] + '..') if len(item['title']) > 50 else item['title']
        print(f"{i:<3} | {item['core']:<10} | {title_display}")

    print("\n" + "="*60)
    print("📊 RESUMO ESTATÍSTICO")
    print("="*60)

    print(f"🖥️  Tech:      {stats.get('Tech', 0)}")
    print(f"📊 Data:      {stats.get('Data', 0)}")
    print(f"📈 Marketing: {stats.get('Marketing', 0)}")
    print("="*60 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Proposals Architect - War Report Dashboard")
    parser.add_argument("--dir", default="propostas_geradas", help="Diretório das propostas (padrão: propostas_geradas)")

    args = parser.parse_args()

    generate_report(args.dir)

if __name__ == "__main__":
    main()
