/**
 * 日本臨床ライフサポート協会 ホームページ「お問い合わせフォーム」受付
 *
 * 置き場所：協会のGoogleアカウントで作ったスプレッドシート「HPお問い合わせ」の
 *           拡張機能 → Apps Script に、このファイルの中身をそのまま貼り付ける。
 * 動き    ：フォームが送信されると、①このスプレッドシートに1行追加し、②NOTIFY_TO にメールで知らせる。
 *           お知らせメールに「返信」すれば、そのまま問い合わせた人へ返信できる。
 */

const NOTIFY_TO = 'info@japan-clinical-lifesupport.org';
const SHEET_NAME = '受付';
const HEADERS = ['受付日時', 'ご用件', '団体名', 'お名前', 'メール', '電話', '希望日時', '人数・対象', '会場', '内容', '対応状況'];

function doPost(e) {
  const p = (e && e.parameter) || {};

  // 迷惑投稿よけ：人には見えない欄（website）に何か入っていたら、記録せずに終える
  if (p.website) return ok_();

  const clip = (v, n) => String(v || '').trim().slice(0, n || 500);
  const name = clip(p.name, 100);
  const email = clip(p.email, 200);
  const message = clip(p.message, 5000);
  if (!name || !message || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return ok_();

  // 同じメールアドレスから短時間に大量に送られたときは止める（10分に5件まで）
  const cache = CacheService.getScriptCache();
  const key = 'n:' + email.toLowerCase();
  const n = Number(cache.get(key) || 0);
  if (n >= 5) return ok_();
  cache.put(key, String(n + 1), 600);

  const row = {
    topic: clip(p.topic, 50), org: clip(p.org, 200), name: name, email: email, tel: clip(p.tel, 50),
    dates: clip(p.dates), people: clip(p.people), place: clip(p.place), message: message,
  };

  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const sheet = sheet_();
    // 先頭が = + - @ の入力は、表計算の式として動かないよう ' を付けて文字として保存する
    const safe = (v) => (/^[=+\-@]/.test(v) ? "'" + v : v);
    sheet.appendRow([new Date(), row.topic, row.org, row.name, row.email, row.tel, row.dates, row.people, row.place, row.message, '未対応'].map((v) => (typeof v === 'string' ? safe(v) : v)));
  } finally {
    lock.releaseLock();
  }

  const lines = [
    'ホームページのフォームからお問い合わせがありました。',
    'このメールに「返信」すると、問い合わせた方へそのまま返信できます。',
    '',
    'ご用件　：' + row.topic,
    '団体名　：' + (row.org || '—'),
    'お名前　：' + row.name,
    'メール　：' + row.email,
    '電話　　：' + (row.tel || '—'),
  ];
  if (row.dates || row.people || row.place) {
    lines.push('希望日時：' + (row.dates || '—'), '人数対象：' + (row.people || '—'), '会場　　：' + (row.place || '—'));
  }
  lines.push('', '【内容】', row.message, '', '受付一覧：' + SpreadsheetApp.getActiveSpreadsheet().getUrl());

  MailApp.sendEmail({
    to: NOTIFY_TO,
    replyTo: row.email,
    subject: '【HPお問い合わせ】' + row.topic + '（' + (row.org ? row.org + ' ' : '') + row.name + '様）',
    body: lines.join('\n'),
    name: 'ホームページ お問い合わせフォーム',
  });

  return ok_();
}

function sheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) {
    sh = ss.insertSheet(SHEET_NAME);
    sh.appendRow(HEADERS);
    sh.setFrozenRows(1);
    sh.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold').setBackground('#EFE8DC');
  }
  return sh;
}

function ok_() {
  return ContentService.createTextOutput('ok');
}

/** 設定の確認用：Apps Script の画面でこの関数を選んで「実行」すると、許可の画面が出て、テストの1行とメールが届く */
function testSubmit() {
  doPost({ parameter: { topic: 'その他（取材など）', name: 'テスト送信', email: 'info@japan-clinical-lifesupport.org', message: 'フォームの動作確認です。この行は消してかまいません。' } });
}
