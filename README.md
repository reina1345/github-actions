# 市場価格調査ツール (Market Price Checker)

## プロジェクト概要
Amazon、Yahoo!ショッピング、楽天市場、ビックカメラなどの主要通販サイトから、商品の価格相場を素早く正確に調査するためのWebアプリケーションです。

## 目的
ユーザー（自分）が商品を安く購入するため、あるいは市場価格を把握するために、複数のサイトを横断して効率的に価格を比較できるようにします。

## 主な機能
*   複数サイト（Amazon, Yahoo, Rakuten, BicCamera）の一括検索
*   検索結果の価格比較一覧
*   素早いレスポンスと正確な情報表示

## 実行方法

ターミナル（コマンドプロンプト）を開き、このプロジェクトのフォルダ（`pyproject.toml` ファイルがある場所）に移動してから、以下のコマンドを実行してください。

1. 依存関係のインストール
   ```bash
   uv sync
   uv run playwright install chromium
   ```

2. アプリケーションの起動
   ```bash
   uv run streamlit run src/market_price_checker/app.py
   ```
