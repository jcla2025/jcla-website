# 一般社団法人日本臨床ライフサポート協会 ホームページ

公開URL：https://www.japan-clinical-lifesupport.org

## 仕組み
- `src/content.py` … 文章・講習会・活動報告・写真の設定（更新はほぼここだけ）
- `src/static/` … デザイン（CSS）・ロゴ・画像
- `src/build.py` … `python3 src/build.py` で `docs/` にサイトを書き出す
- `docs/` … 公開されるサイト本体（GitHub Pages の公開元：main ブランチ / docs フォルダ）

## よくある更新
- 活動報告を追加：`REPORTS` に1件追加 → build
- 講習会を追加：`EVENTS` に1件追加（日付が今日以降なら「開催予定」に表示）→ build
- 写真：`src/static/assets/photos/` に置き、`PHOTOS` または報告の `photo` にファイル名を書く → build
