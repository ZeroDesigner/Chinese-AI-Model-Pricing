# Chinese-AI-Model-Pricing

一个面向中国大陆及全球平台的 AI 模型 Token 价格索引。仓库通过 GitHub Actions 每天检查官方定价源，并更新数据快照与静态页面。

> 定价可能随活动、缓存命中、上下文长度、区域和计费方式变化。使用前请以官方定价页面为准。

## 查看价目表

- [在线表格](https://zerodesigner.github.io/Chinese-AI-Model-Pricing/)
- [原始 JSON 数据](data/pricing.json)
- [定价来源](data/sources.json)

## 已覆盖的厂商

- 阿里云通义千问（阿里云百炼）
- 百度千帆（文心）
- 字节火山引擎（豆包）
- DeepSeek
- 腾讯云（混元）
- 智谱 AI（GLM）
- 月之暗面（Kimi）
- MiniMax
- 零一万物
- 硅基流动（SiliconFlow）
- 国内及国际聚合平台

## 数据更新

定价快照存放在 `data/pricing.json`，来源元数据存放在 `data/sources.json`。

```bash
python3 scripts/update_pricing.py
python3 scripts/generate_site.py
python3 -m unittest -v
```

`.github/workflows/update.yml` 每天运行一次更新脚本，并在数据发生变化时提交并部署 GitHub Pages。

## 字段说明

| 字段 | 含义 |
|---|---|
| `input_cny_per_million` | 输入/提示 Token，每百万人民币元 |
| `output_cny_per_million` | 输出/生成 Token，每百万人民币元 |
| `cache_input_cny_per_million` | 缓冲命中输入价（若厂商提供） |
| `verified_at` | 数据人工核验日期 |
| `source_url` | 官方定价链接 |

## 贡献

欢迎提交官方定价、区域差异、缓存价、批量 API 等信息。请附带官方链接和核验日期，不要只依据第三方博客或平台页面截图。
