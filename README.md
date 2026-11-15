# ポートフォリオサイト

平 伸彦（Taira Nobuhiko）のポートフォリオサイトです。

## サイトの URL

https://tairanobuhiko.com/

## フォルダの中身

| ファイル・フォルダ | 中身 |
| --- | --- |
| `index.html` | トップページ |
| `works/02.html` | 実績「しりとり画像ジェネレーター」の詳細ページ |
| `css/style.css` | 見た目と動きの指定 |
| `js/script.js` | スクロールで現れる動き、スマホ用メニューなど |
| `images/` | 画像 |
| `favicon.svg` | ブラウザのタブに出る小さな印 |
| `CNAME` | 独自ドメインの設定。**消したり書き換えたりしないでください**（サイトが独自ドメインで開けなくなります） |
| `_config.yml` | サイトの URL から見えないようにするフォルダの指定 |
| `tests/` | サイトの検査 |
| `docs/` | 設計書と実装計画 |

ビルドの作業はありません。ファイルを直せば、それがそのままサイトになります。

## 手元で見る方法

1. Finder でこのフォルダを開きます。
2. `index.html` をダブルクリックします。
3. ブラウザが開いて、トップページが表示されます。

ファイルを直したあとは、ブラウザで再読み込み（Mac は `Command + R`）をすると変更が反映されます。
文字のデザインはインターネットから読み込むので、ネットにつながった状態で確認してください。

この開き方では、詳細ページの上のメニュー（About など）やロゴを押すと、トップページではなくフォルダの中身の一覧が出ます。公開したサイトでは正しくトップページへ移動します。手元でもメニューの動きまで確かめたいときは、次の手順を使います。

1. 「ターミナル」アプリを開きます。
2. `cd ` と入力し（最後に半角スペース）、Finder からこのフォルダをターミナルの画面にドラッグして、Enter キーを押します。
3. `python3 -m http.server 8000` と入力して、Enter キーを押します。
4. ブラウザのアドレス欄に `http://localhost:8000/` と入力して開きます。
5. 終わるときは、ターミナルで `Control + C` を押します。

## Zenn の記事を足す・入れ替える

記事の一覧は `index.html` に手で書いてあります。自動では増えません。

1. `index.html` をエディタ（VS Code など）で開きます。
2. `Command + F` で `WRITING:`（最後にコロン）を検索します。`<!-- WRITING:` で始まる行が見つかります。
3. その少し下に、次のような行が並んでいます。1 行が記事 1 本です。

   ```html
   <a class="post" href="https://zenn.dev/no215/articles/claude-code-api-cost-log" target="_blank" rel="noopener"><div><time datetime="2026-11-08">2026.11.08</time><b>サブスク利用でも API 換算コストを把握したい</b></div><i>↗</i></a>
   ```

4. 足したい場所に、この 1 行をコピーして貼り付けます。
5. 貼り付けた行の 4 か所を書き換えます。

   | 書き換える場所 | 例 | 入れるもの |
   | --- | --- | --- |
   | `href="..."` の中 | `https://zenn.dev/no215/articles/claude-code-api-cost-log` | 記事の URL |
   | `datetime="..."` の中 | `2026-11-08` | 公開日（ハイフン区切り） |
   | `<time ...>` と `</time>` の間 | `2026.11.08` | 公開日（ドット区切り。画面に出る表記） |
   | `<b>` と `</b>` の間 | `サブスク利用でも API 換算コストを把握したい` | 記事のタイトル |

6. 古い記事を外すときは、その記事の 1 行をまるごと消します。
7. 保存して、ブラウザで表示を確認します。

「NEW」の下が新しい記事、「POPULAR」の下がよく読まれた記事です。

## 実績を足す

1. `index.html` をエディタで開き、`Command + F` で `WORKS:` を検索します。
2. `<a class="work"` から `</a>` までが実績 1 件です。次の例をコピーして、一覧の最後の `</a>` の下に貼り付けます。

   ```html
   <a class="work" href="https://github.com/tairanobuhiko/Tetris" target="_blank" rel="noopener" data-peek-label="Tetris" data-peek-tone="ink" data-reveal>
     <span class="work__no">04</span>
     <div>
       <h3>Tetris</h3>
       <p>React Native と Expo で作ったテトリスです。スワイプやタップで操作します。</p>
       <p class="stack">React Native / Expo / TypeScript</p>
     </div>
     <span class="work__go">GitHub<i>↗</i></span>
   </a>
   ```

3. 次の場所を書き換えます。

   | 書き換える場所 | 入れるもの |
   | --- | --- |
   | `href="..."` | 行き先の URL |
   | `data-peek-label="..."` | マウスを乗せたときに出る札の文字（実績の名前） |
   | `data-peek-tone="..."` | 札の色。`navy`（紺）、`orange`（橙）、`ink`（黒）から選びます |
   | `<span class="work__no">` の中 | 通し番号（`05` など） |
   | `<h3>` の中 | 実績の名前 |
   | 1 つ目の `<p>` の中 | 説明文 |
   | `<p class="stack">` の中 | 使った技術 |
   | `<span class="work__go">` の中 | 行き先の表示（`GitHub`、`サイトを見る` など） |

4. 札の代わりに画像を出したいときは、画像を `images/work/` に置きます。そのうえで `data-peek-label` と `data-peek-tone` を消し、`data-peek-img="images/work/画像のファイル名"` を書きます。画像は 1 枚 400KB 以下にしてください。

## 検査の動かし方

リンク切れや、画像の重さ、載せてはいけない情報の消し忘れなどを自動で確かめられます。ファイルを直したあとに実行してください。

1. 「ターミナル」アプリを開きます。
2. `cd ` と入力し（最後に半角スペース）、Finder からこのフォルダをターミナルの画面にドラッグして、Enter キーを押します。
3. 次のコマンドを貼り付けて、Enter キーを押します。

   ```bash
   python3 -m unittest discover -s tests -v
   ```

4. 最後の行に `OK` と出れば問題ありません。`FAILED` と出たときは、その上に「どのファイルの何がいけないか」が書かれています。

記事や実績を入れ替えたときは、検査の中の文言の一覧（`tests/test_site.py` の `INDEX_TEXT` と `INDEX_LINKS`）も同じように直してください。直さないと、外した記事が「載っていない」と報告されます。

## 公開のしかた

GitHub の `main` ブランチに入った内容が、数分でそのままサイトに公開されます。

1. 作業用のブランチで変更をコミットし、GitHub にプッシュします。ターミナルでこのフォルダへ移動してから（移動のしかたは「検査の動かし方」の 1〜2 と同じ）、次の 3 行を 1 行ずつ実行します。`"..."` の中は、何を変えたかの一言に書き換えます。

   ```bash
   git add -A
   git commit -m "記事の一覧を更新"
   git push -u origin HEAD
   ```

2. GitHub のこのリポジトリのページを開き、「Compare & pull request」ボタンを押してプルリクエストを作ります。
3. 変更の中身を確認して、「Merge pull request」ボタンを押します。
4. 数分待ってから https://tairanobuhiko.com/ を開き、変更が反映されていることを確認します。

`main` に入れた時点で公開されるので、入れる前に上の「検査の動かし方」と「手元で見る方法」で確認してください。
