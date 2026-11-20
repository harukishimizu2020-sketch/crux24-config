# Crux-24 LINE 通知の置き場

- `msg_<YYYYMMDD>_early.txt`(19時の1位)と `msg_<YYYYMMDD>_late.txt`(23:30 取得後の最終TOP3)をここに置くと、
  GitHub Actions(`.github/workflows/line_send.yml`)が 19:20 と 0:20 JST に LINE 公式アカウントから broadcast で送る。
- 選び方: JST 正午前=今日、正午以降=明日。late があれば late だけ、無ければ early。1回に1通。
- 同じ文は `sent.jsonl` のハッシュで二度送らない(送信後に Actions が記録を commit する)。
- 鍵はリポジトリのシークレット `LINE_CHANNEL_ACCESS_TOKEN`。値はどこにも書かない。
- 手で今すぐ送るとき: GitHub の Actions タブ → Crux-24 LINE send → Run workflow。
