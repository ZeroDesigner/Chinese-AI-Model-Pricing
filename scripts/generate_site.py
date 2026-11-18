#!/usr/bin/env python3
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRICING = ROOT / "data" / "pricing.json"
OUT = ROOT / "docs" / "index.html"


def price(value):
    if value is None:
        return '<span class="unknown">待核验</span>'
    return f"{html.escape(str(value))}"


def main():
    data = json.loads(PRICING.read_text(encoding="utf-8"))
    providers = sorted({model["provider"] for model in data["models"]})
    rows = []
    for model in sorted(data["models"], key=lambda item: (item["provider"], item["name"].lower())):
        context = f"{model['context_window']:,}" if model.get("context_window") else "—"
        cache = price(model.get("cache_input_cny_per_million"))
        verified = model.get("verified_at") or "待核验"
        source = html.escape(model["source_url"])
        name = html.escape(model["name"])
        model_id = html.escape(model["model_id"])
        provider = html.escape(model["provider"])
        rows.append(
            "<tr>"
            f'<td><strong>{name}</strong><br><code>{model_id}</code></td>'
            f"<td>{provider}</td>"
            f"<td>{context}</td>"
            f"<td>{price(model.get('input_cny_per_million'))}</td>"
            f"<td>{cache}</td>"
            f"<td>{price(model.get('output_cny_per_million'))}</td>"
            f"<td>{html.escape(verified)}</td>"
            f'<td><a href="{source}" target="_blank" rel="noopener">官方</a></td>'
            "</tr>"
        )

    provider_options = "".join(
        f'<option value="{html.escape(provider)}">{html.escape(provider)}</option>'
        for provider in providers
    )
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>中国 AI 模型 Token 价目表</title>
  <style>
    :root {{ color-scheme: light dark; --line: #9aa0a6; --muted: #687078; }}
    body {{ max-width: 1180px; margin: 0 auto; padding: 24px; font-family: system-ui, sans-serif; }}
    h1 {{ margin-bottom: 8px; }} .meta {{ color: var(--muted); margin-bottom: 20px; }}
    .controls {{ display:flex; gap:12px; margin-bottom:16px; flex-wrap:wrap; }}
    input, select {{ padding:9px 11px; border:1px solid var(--line); border-radius:6px; font-size:14px; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; }}
    th, td {{ border-bottom:1px solid var(--line); padding:10px 8px; text-align:left; vertical-align:top; }}
    th {{ position:sticky; top:0; background:Canvas; }} code {{ font-size:12px; }}
    .unknown {{ color:#b54708; }} .hidden {{ display:none; }}
  </style>
</head>
<body>
  <h1>中国 AI 模型 Token 价目表</h1>
  <div class="meta">单价：人民币/百万 Token；最后检查：{html.escape(data['last_checked'])}</div>
  <p>价格仅供参考，缓存命中、活动折扣、区域和计费方式可能影响实际费用。</p>
  <div class="controls">
    <input id="search" type="search" placeholder="搜索模型或厂商" aria-label="搜索">
    <select id="provider" aria-label="厂商筛选">
      <option value="">全部厂商</option>{provider_options}
    </select>
  </div>
  <table>
    <thead><tr><th>模型</th><th>厂商</th><th>上下文</th><th>输入</th><th>缓存输入</th><th>输出</th><th>核验日期</th><th>来源</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  <script>
    const search = document.getElementById('search');
    const provider = document.getElementById('provider');
    function filter() {{
      const q = search.value.trim().toLowerCase();
      const p = provider.value;
      document.querySelectorAll('tbody tr').forEach(row => {{
        const providerCell = row.children[1].textContent.trim();
        row.classList.toggle('hidden', (p && providerCell !== p) ||
          (q && !row.textContent.toLowerCase().includes(q)));
      }});
    }}
    search.addEventListener('input', filter);
    provider.addEventListener('change', filter);
  </script>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"Generated {OUT} with {len(data['models'])} models")


if __name__ == "__main__":
    main()
