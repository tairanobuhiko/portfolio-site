"""サイト全体の検査。

リポジトリの直下で次のように実行する。

    python3 -m unittest discover -s tests -v

Python の標準機能だけを使う。確かめる内容は
docs/superpowers/specs/2026-11-14-portfolio-redesign-design.md の 9.1 にある。
"""
import re
import struct
import unittest
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = "index.html"
DETAIL = "works/02.html"
PAGES = [INDEX, DETAIL]
CSS = "css/style.css"
JS = "js/script.js"
SITE_URL = "https://tairanobuhiko.com/"

# 閉じタグの要らない要素
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

# 転職活動用の情報や、やめた仕組みの名残り（大文字小文字を区別しない）
FORBIDDEN = [
    "1986", "test@com", "test7890", "fuga", "4242424242424242",
    "onrender.com", "jquery", "ofi.min.js", "qiita",
    "tairanobuhiko.github.io", "PdM",
]

ZENN = "https://zenn.dev/no215/articles/"
DESCRIPTION = "AI の研究・PoC 開発に取り組むエンジニア、平 伸彦（Taira Nobuhiko）のポートフォリオサイトです。"

# 設計書 5.2〜5.9: トップページに載せる文言
INDEX_TEXT = [
    # 冒頭
    "Software Engineer", "TAIRA", "NOBUHIKO.", "平 伸彦", "群馬県出身",
    "マルチクラウドを扱う SIer で、AI の研究・推進と PoC 開発に取り組んでいます。個人開発で工夫したことは Zenn で発信しています。",
    "AI RESEARCH · PoC · RAG · AZURE ·",
    # 流れる帯
    "TYPESCRIPT", "REACT", "NEXT.JS", "C#", "PYTHON", "RUBY ON RAILS",
    # ABOUT
    "ABOUT", "プロフィール",
    "AI ソリューションの SaaS を開発する企業で、Azure を基盤とした RAG チャットボットアプリの開発・運用・障害対応・保守を一貫して担当しました。",
    "現在はマルチクラウドを扱う SIer 企業で、AI 研究・AI 推進・PoC 開発を行っています。",
    "エンジニアになる前は、VBA・GAS を活用した情報ポータルツールや自動化ツールの開発など、業務効率化に携わり 2022 年に社長賞を受賞。",
    "自身のアイデアや周りから得たフィードバックを反映し開発したツールで喜んでくれる人がいることが嬉しく、技術をもっと深く学び社内だけではなく世の中に価値を提供できるようなサービスに関わりたいと思うようになっていきました。",
    "個人学習に加え、Web 開発に必要なスキルを体系的に学びたくプログラミングスクールに通い、2024 年にエンジニアへ転職しました。",
    "10 代・20 代で音楽制作、映像制作などで培ってきたクリエイティビティとプログラミングスキルを掛け合わせ、人が喜ぶサービスづくりをして世の中に価値を発揮していきたいと考えています。",
    "業務効率化ツールの開発で社長賞を受賞", "プログラミングスクールで Web 開発を学ぶ",
    "エンジニアへ転職。RAG チャットボットを担当", "NOW", "SIer で AI 研究・AI 推進・PoC 開発",
    # SKILLS
    "SKILLS", "スキル",
    "RAG（検索拡張生成）", "生成 AI を使ったアプリ開発", "PoC 開発",
    "フロントエンド", "HTML", "CSS", "Tailwind CSS", "JavaScript", "TypeScript", "React", "Next.js", "React Native（Expo）",
    "バックエンド", "C#（ASP.NET Core Blazor）", "Python（FastAPI）", "Ruby（Ruby on Rails）",
    "クラウド・データベース", "Azure", "AWS", "Vercel", "Render", "MySQL", "PostgreSQL",
    "ツール", "Git", "GitHub", "Slack", "Notion", "Figma",
    # WORKS
    "WORKS", "実績",
    "しりとり画像ジェネレーター", "ローマ字タイピングの習得を目的とした小学生向けアプリケーションです。",
    "Ruby on Rails / Tailwind CSS / PostgreSQL / Stable Diffusion / OpenAI（DALL-E 3）", "詳細を見る",
    "Plus One 社 コーポレートサイト",
    "住宅リフォーム会社 Plus One 社のコーポレートサイトです。構成の検討からデザイン、実装、公開、更新までを一人で担当しました。",
    "Next.js / TypeScript / MUI / Vercel", "サイトを見る",
    "おうちでBEAT", "React Native と Expo で作ったリズムゲームです。譜面と音源のファイルを置くと、ゲーム内の楽曲リストが自動で作られます。",
    "Tetris", "React Native と Expo で作ったテトリスです。スワイプやタップで操作します。",
    "React Native / Expo / TypeScript",
    # WRITING
    "WRITING", "Zenn の記事", "新しい記事", "よく読まれた記事",
    "2026.11.10", "楽天モバイル「あんしんコントロール」の見守り通知を、GAS を使って LINE 通知化",
    "2026.11.09", "アプリのインストールが制限された 業務PC（Windows） で、Markdown の表をターミナルで見やすくする",
    "2026.11.08", "サブスク利用でも API 換算コストを把握したい",
    "2026.11.07", "iTerm2のタブ色をgitブランチごとに自動で変える",
    "2024.08.17", "【Vercel / Next.js】環境変数設定の注意点アレコレ",
    "2024.07.06", "ポートフォリオサイトの公開と公開手順【GitHub Pages】",
    "2024.03.15", "Renderで無料デプロイしたアプリをキープアライブする方法",
    "Zenn ですべての記事を見る",
    # CONTACT とフッター
    "CONTACT.", "お仕事のご相談やご連絡は、メールまたは X からお願いします。", "メールを送る", "X で連絡する",
    "© Taira Nobuhiko.", "Back to top",
]

# 設計書 5.5: スキルの札。並び順も含めてこのとおり
SKILL_PILLS = [
    "RAG（検索拡張生成）", "生成 AI を使ったアプリ開発", "PoC 開発",
    "HTML", "CSS", "Tailwind CSS", "JavaScript", "TypeScript", "React", "Next.js", "React Native（Expo）",
    "C#（ASP.NET Core Blazor）", "Python（FastAPI）", "Ruby（Ruby on Rails）",
    "Azure", "AWS", "Vercel", "Render", "MySQL", "PostgreSQL",
    "Git", "GitHub", "Slack", "Notion", "Figma",
]

# 設計書 5.2、5.6、5.7、5.8: トップページのリンク先
INDEX_LINKS = [
    "https://github.com/tairanobuhiko",
    "https://zenn.dev/no215",
    "https://x.com/tairanobuhiko",
    "works/02.html",
    "https://plusone-kk.vercel.app",
    "https://github.com/tairanobuhiko/outi-de-beat",
    "https://github.com/tairanobuhiko/Tetris",
    ZENN + "anshin-control-line-notify",
    ZENN + "terminal-markdown-table-uv-rich",
    ZENN + "claude-code-api-cost-log",
    ZENN + "iterm2-tab-color-by-git-branch",
    ZENN + "d0585982ba1116",
    ZENN + "331bc656b6d79d",
    ZENN + "ff4f1670c080e4",
    "mailto:no.215.tyler@gmail.com",
]

# 設計書 5.10: 詳細ページに載せる文言（本文は作り直す前のページの文そのまま）
DETAIL_TEXT = [
    "しりとり画像ジェネレーター", "Word Chain Image Generator",
    "開発環境",
    "Ruby / Ruby on Rails / Tailwind CSS / JavaScript / PostgreSQL / Render / AWS S3 / StableDiffusion / OpenAI(DALL-E3) / Google Apps Script / Twitter API / Tiny_URL / GitHub / GitHub Actions / Figma / draw.io / Cursor / Google Analytics",
    "制作時間", "150時間", "現在サービス停止中",
    "OUTLINE", "アプリケーションの概要",
    "ローマ字タイピングの習得を目的とした小学生向けアプリケーションです。",
    "画像生成機能が興味・動機づけとなり、プロンプトとなるしりとりをタイピング形式で行うことで結果的にローマ字タイピングの習得につながります。",
    "しりとりの結果をプロンプトとして画像生成を行い、どんな画像ができるかを楽しみながらローマ字タイピングの練習に取り組むことができます。",
    "開発に至った経緯",
    "2020年より小学1年生からラップトップPCが貸与され幼少期からITリテラシーが求められる時代になりました。",
    "PCを扱うためには基本的なキーボードタイピングが必要で、我が子に対し早いうちからキーボードタイピングを覚えさせることが大切だと考える親御さんも多くいます。",
    "実際に私の長女がローマ字タイピングの習得ができず、かと言って「練習するのもつまらない！ローマ字も覚えたくない！！」といった課題を抱えておりました...",
    "ローマ字そのものを教えることはできるがなんとか主体的に学習につながる環境づくりをサポートできないか。",
    "といった考えから『子供たちがローマ字入力でのキーボードタイピングを習得しやすく、楽しく学べる環境を提供し、ITリテラシー向上のきっかけになることで世の中への貢献になれば』という想いで企画、開発に至りました。",
    "開発で工夫したこと",
    "テストコード実装においてテストのたびに画像生成APIを叩く処理をエミュレートし外部APIによる依存を制御することでAPIコストを抑制しテストの安定性を向上させました。",
    "画像生成機能において適切な生成AIモデルを選択し、ネガティブプロンプトをあらかじめ制御することで不適切な画像を生成させない仕様としました。",
    "画像生成のリクエスト制限（429エラー）やサーバーエラー（500, 503）の対策として指数バックオフ方式（2秒〜32秒、最大5回）でリトライを行うロジックにしました。",
    "また、429エラーの場合は別の生成モデルのAPIへフォールバックする仕様とし、画像生成の安定性向上に努めました。",
    "関連記事",
    "【個人開発】しりとり画像ジェネレーター【オリジナルアプリの完成】",
    "【WebMock＋RSpec】テストコードで外部APIを模倣する【余分なAPIコストを抑制】",
    "【個人開発記録】画像生成機能を実装する【しりとり画像ジェネレーター】",
    "【例外処理】画像生成エラー時に代替モデルへフォールバック【429エラー対策】",
    "WORKS へ戻る",
]

# 設計書 5.10: 詳細ページから外す欄
DETAIL_REMOVED = ["今後実装したい", "動作テスト", "テスト用アカウント", "その他実績", "スコアリング機能"]

DETAIL_LINKS = [
    "https://github.com/tairanobuhiko/word_chain_image_generator",
    ZENN + "a1ac635343870b",
    ZENN + "00a0e54fb43980",
    ZENN + "9490defad6948b",
    ZENN + "fab9b3a58629d4",
    "../#works",
]

# 設計書 5.2 と 5.12: 画像の代替テキスト
ALT_TEXTS = {
    INDEX: ["平 伸彦のイラスト"],
    DETAIL: [
        "しりとり画像ジェネレーターの画面（パソコン表示）",
        "しりとり画像ジェネレーターの画面（スマホ表示）",
        "DALL-E 3 のロゴ",
        "Stable Diffusion のロゴ",
    ],
}


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def squash(text):
    """空白をすべて取り除く。HTML の改行位置に左右されずに文言を比べるため。"""
    return re.sub(r"\s+", "", text)


class Doc(HTMLParser):
    """1 ページ分のタグ、本文、id、開き閉じの食い違いを集める。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []          # (タグ名, 属性の辞書)
        self.ids = set()
        self.text = []          # script と style を除いた本文
        self.title = ""
        self.errors = []        # 開き閉じの食い違い
        self._stack = []

    def handle_starttag(self, tag, attrs):
        attrs = {k: (v if v is not None else "") for k, v in attrs}
        self.tags.append((tag, attrs))
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag not in VOID:
            self._stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        # <path ... /> のような、その場で閉じるタグ
        attrs = {k: (v if v is not None else "") for k, v in attrs}
        self.tags.append((tag, attrs))
        if "id" in attrs:
            self.ids.add(attrs["id"])

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self._stack and self._stack[-1] == tag:
            self._stack.pop()
        else:
            line, _ = self.getpos()
            self.errors.append(f"{line} 行目: </{tag}> が合わない（開いているのは {self._stack[-3:]}）")

    def handle_data(self, data):
        current = self._stack[-1] if self._stack else ""
        if current in ("script", "style"):
            return
        if current == "title":
            self.title += data
        self.text.append(data)

    def close(self):
        super().close()
        if self._stack:
            self.errors.append(f"閉じていないタグ: {self._stack}")

    def attrs_of(self, tag):
        return [a for t, a in self.tags if t == tag]

    def meta(self):
        """<meta> の name / property から content を引く辞書。"""
        found = {}
        for a in self.attrs_of("meta"):
            key = a.get("name") or a.get("property")
            if key:
                found[key] = a.get("content", "")
        return found


@lru_cache(maxsize=None)
def parse(rel):
    doc = Doc()
    doc.feed(read(rel))
    doc.close()
    return doc


def page_text(rel):
    return squash("".join(parse(rel).text))


def is_external(url):
    return url.startswith(("http://", "https://", "mailto:", "data:", "//"))


def page_refs(rel):
    """ページがファイルを指している属性の値を集める。"""
    refs = []
    for _tag, attrs in parse(rel).tags:
        for name in ("href", "src", "data-peek-img"):
            if attrs.get(name):
                refs.append(attrs[name])
        if attrs.get("srcset"):
            refs.extend(part.split()[0] for part in attrs["srcset"].split(",") if part.strip())
    return refs


def resolve(base_rel, url):
    """ページやスタイルから見た相対パスを、実際の場所に直す。フォルダなら index.html を指す。"""
    path = url.split("#")[0].split("?")[0]
    target = (ROOT / base_rel).parent / path
    target = target.resolve()
    if target.is_dir():
        target = target / "index.html"
    return target


def css_rules(css, context=()):
    """CSS を (囲んでいる @media などの並び, セレクタ, 中身) の組にばらす。"""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    rules = []
    pos = 0
    while True:
        open_at = css.find("{", pos)
        if open_at == -1:
            break
        prelude = css[pos:open_at].strip()
        depth, i = 1, open_at + 1
        while depth and i < len(css):
            depth += {"{": 1, "}": -1}.get(css[i], 0)
            i += 1
        body = css[open_at + 1:i - 1]
        if prelude.startswith(("@media", "@supports")):
            rules.extend(css_rules(body, context + (prelude,)))
        elif not prelude.startswith("@"):
            rules.append((context, " ".join(prelude.split()), body))
        pos = i
    return rules


def css_urls():
    return [u.strip("'\" ") for u in re.findall(r"url\(([^)]+)\)", read(CSS))]


class TestRepo(unittest.TestCase):
    def test_cname_unchanged(self):
        self.assertEqual(read("CNAME").strip(), "tairanobuhiko.com")

    def test_removed_files_absent(self):
        for rel in ["works/01.html", "scss", "css/style.css.map", "js/ofi.min.js"]:
            with self.subTest(rel):
                self.assertFalse((ROOT / rel).exists(), f"{rel} が残っている")

    def test_config_excludes(self):
        path = ROOT / "_config.yml"
        self.assertTrue(path.exists(), "_config.yml がない")
        lines = path.read_text(encoding="utf-8").splitlines()
        self.assertIn("exclude:", [line.strip() for line in lines])
        items = {line.strip()[2:].strip() for line in lines if line.strip().startswith("- ")}
        self.assertLessEqual({"docs", "tests", "README.md"}, items)


class TestLinks(unittest.TestCase):
    def test_local_references_exist(self):
        for rel in PAGES:
            for url in page_refs(rel):
                if is_external(url) or url.startswith("#"):
                    continue
                with self.subTest(page=rel, url=url):
                    self.assertTrue(resolve(rel, url).exists(), f"{rel} の {url} の行き先がない")
        for url in css_urls():
            if is_external(url):
                continue
            with self.subTest(page=CSS, url=url):
                self.assertTrue(resolve(CSS, url).exists(), f"{CSS} の {url} の行き先がない")

    def test_fragment_targets_exist(self):
        checked = 0
        for rel in PAGES:
            for attrs in parse(rel).attrs_of("a"):
                href = attrs.get("href", "")
                if "#" not in href or is_external(href):
                    continue
                path, fragment = href.split("#", 1)
                if not fragment:
                    continue
                target = resolve(rel, path) if path else ROOT / rel
                with self.subTest(page=rel, href=href):
                    self.assertTrue(target.exists(), f"{href} の行き先のページがない")
                    self.assertIn(fragment, parse(str(target.relative_to(ROOT))).ids)
                checked += 1
        self.assertGreaterEqual(checked, 10, "ページ内リンクが見つからない")

    def test_blank_links_have_noopener(self):
        for rel in PAGES:
            external = [a for a in parse(rel).attrs_of("a") if a.get("href", "").startswith("http")]
            self.assertTrue(external, f"{rel} に外部リンクがない")
            for attrs in external:
                with self.subTest(page=rel, href=attrs["href"]):
                    self.assertEqual(attrs.get("target"), "_blank", "外部リンクは別タブで開く")
                    self.assertIn("noopener", attrs.get("rel", "").split())


class TestForbidden(unittest.TestCase):
    def test_forbidden_strings_absent(self):
        for rel in PAGES + [CSS, JS, "README.md"]:
            text = read(rel).lower()
            for word in FORBIDDEN:
                with self.subTest(file=rel, word=word):
                    self.assertNotIn(word.lower(), text)


class TestCopy(unittest.TestCase):
    def assert_text(self, rel, phrases):
        text = page_text(rel)
        for phrase in phrases:
            with self.subTest(page=rel, phrase=phrase[:30]):
                self.assertIn(squash(phrase), text)

    def assert_links(self, rel, urls):
        hrefs = {a.get("href", "") for a in parse(rel).attrs_of("a")}
        for url in urls:
            with self.subTest(page=rel, url=url):
                self.assertIn(url, hrefs)

    def test_index_text(self):
        self.assert_text(INDEX, INDEX_TEXT)

    def test_skill_pills_exact(self):
        # 「Git」は「GitHub」に含まれるなど、本文への部分一致では札の消し忘れ・消しすぎに気づけない
        pills = re.findall(r'<li class="pill">(.*?)</li>', read(INDEX))
        self.assertEqual(pills, SKILL_PILLS)

    def test_index_links(self):
        self.assert_links(INDEX, INDEX_LINKS)

    def test_detail_text(self):
        self.assert_text(DETAIL, DETAIL_TEXT)

    def test_detail_removed_sections_absent(self):
        text = page_text(DETAIL)
        for phrase in DETAIL_REMOVED:
            with self.subTest(phrase=phrase):
                self.assertNotIn(squash(phrase), text)

    def test_detail_links(self):
        self.assert_links(DETAIL, DETAIL_LINKS)


class TestMeta(unittest.TestCase):
    def test_lang_ja(self):
        for rel in PAGES:
            with self.subTest(rel):
                self.assertEqual(parse(rel).attrs_of("html")[0].get("lang"), "ja")

    def test_index_meta(self):
        doc = parse(INDEX)
        meta = doc.meta()
        self.assertEqual(doc.title.strip(), "Taira Nobuhiko Portfolio-Site")
        expected = {
            "description": DESCRIPTION,
            "og:description": DESCRIPTION,
            "twitter:description": DESCRIPTION,
            "og:url": SITE_URL,
            "og:image": SITE_URL + "images/og-image.png",
            "twitter:image": SITE_URL + "images/og-image.png",
        }
        for key, value in expected.items():
            with self.subTest(key):
                self.assertEqual(meta.get(key), value)

    def test_detail_title(self):
        self.assertEqual(parse(DETAIL).title.strip(), "しりとり画像ジェネレーター（Word Chain Image Generator）")

    def test_og_image_size(self):
        data = (ROOT / "images/og-image.png").read_bytes()[:24]
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n", "PNG ではない")
        self.assertEqual(struct.unpack(">II", data[16:24]), (1200, 630))

    def test_ga_tag(self):
        for rel in PAGES:
            with self.subTest(rel):
                html = read(rel)
                self.assertIn("googletagmanager.com/gtag/js?id=G-LES68TYGT9", html)
                self.assertIn("gtag('config', 'G-LES68TYGT9')", html)

    def test_favicon_linked(self):
        for rel in PAGES:
            with self.subTest(rel):
                icons = [a for a in parse(rel).attrs_of("link") if a.get("rel") == "icon"]
                self.assertEqual(len(icons), 1)
                self.assertTrue(icons[0]["href"].endswith("favicon.svg"))
                self.assertTrue(resolve(rel, icons[0]["href"]).exists(), "favicon.svg がない")


class TestImages(unittest.TestCase):
    def image_files(self):
        return [p for p in (ROOT / "images").rglob("*") if p.is_file() and not p.name.startswith(".")]

    def test_each_image_size(self):
        for path in self.image_files():
            with self.subTest(str(path.relative_to(ROOT))):
                self.assertLessEqual(path.stat().st_size, 400 * 1024)

    def test_total_image_size(self):
        total = sum(p.stat().st_size for p in self.image_files())
        self.assertLessEqual(total, 2 * 1024 * 1024, f"合計 {total / 1024:.0f}KB")

    def test_no_unused_images(self):
        used = set()
        for rel in PAGES:
            for url in page_refs(rel):
                if not is_external(url) and not url.startswith("#"):
                    used.add(resolve(rel, url))
            # 共有用画像は公開 URL で書かれている
            for content in parse(rel).meta().values():
                if content.startswith(SITE_URL + "images/"):
                    used.add((ROOT / content[len(SITE_URL):]).resolve())
        for url in css_urls():
            if not is_external(url):
                used.add(resolve(CSS, url))
        for path in self.image_files():
            with self.subTest(str(path.relative_to(ROOT))):
                self.assertIn(path.resolve(), used, "どこからも使われていない")

    def test_img_alt(self):
        for rel in PAGES:
            alts = [a.get("alt", "") for a in parse(rel).attrs_of("img")]
            self.assertTrue(alts, f"{rel} に画像がない")
            for alt in alts:
                with self.subTest(page=rel):
                    self.assertTrue(alt.strip(), "alt が空の画像がある")
            for expected in ALT_TEXTS[rel]:
                with self.subTest(page=rel, alt=expected):
                    self.assertIn(expected, alts)


class TestMotion(unittest.TestCase):
    def rules(self):
        return css_rules(read(CSS))

    def test_css_reduced_motion(self):
        reduced = [r for r in self.rules() if any("prefers-reduced-motion: reduce" in c for c in r[0])]
        self.assertTrue(reduced, "「動きを減らす」設定への対応がない")

    def test_js_reduced_motion(self):
        self.assertIn("prefers-reduced-motion", read(JS))

    def test_reveal_hidden_only_with_js(self):
        # JavaScript が動かないときに中身が隠れたままにならないこと
        selectors = [
            part.strip()
            for _ctx, selector, _body in self.rules()
            for part in selector.split(",")
            if "[data-reveal]" in part
        ]
        self.assertTrue(selectors, "[data-reveal] の指定がない")
        for selector in selectors:
            with self.subTest(selector):
                self.assertTrue(selector.startswith(".js "), "`.js ` で始まっていない")

    def test_script_load_failure_shows_content(self):
        # script.js が読み込めなかったとき、隠した欄がそのまま残らないこと
        for rel in PAGES:
            scripts = [a for a in parse(rel).attrs_of("script") if a.get("src", "").endswith("js/script.js")]
            self.assertEqual(len(scripts), 1, f"{rel} が script.js を読み込んでいない")
            with self.subTest(rel):
                self.assertIn("classList.remove('js')", scripts[0].get("onerror", ""))

    def test_print_shows_all(self):
        # 印刷や PDF 保存のとき、まだスクロールしていない欄が空白にならないこと
        printed = [r for r in self.rules() if any("print" in c for c in r[0]) and "[data-reveal]" in r[1]]
        self.assertTrue(printed, "印刷用の指定がない")
        for _context, _selector, body in printed:
            self.assertIn("opacity: 1", body)

    def test_hover_effects_gated(self):
        # タッチ端末で反転が残ったり、マウス用の画像が出たりしないこと
        for needle in (".work:hover", ".peek.is-on"):
            hits = [r for r in self.rules() if needle in r[1]]
            self.assertTrue(hits, f"{needle} の指定がない")
            for context, selector, _body in hits:
                with self.subTest(selector):
                    self.assertTrue(any("hover: hover" in c for c in context), "@media (hover: hover) の外にある")

    def test_font_fallbacks(self):
        css = read(CSS)
        for name in ['"Arial Black"', '"Hiragino Kaku Gothic ProN"', "sans-serif"]:
            with self.subTest(name):
                self.assertIn(name, css)


class TestHtml(unittest.TestCase):
    def test_tags_balanced(self):
        for rel in PAGES:
            with self.subTest(rel):
                self.assertEqual(parse(rel).errors, [])

    def test_menu_button(self):
        for rel in PAGES:
            with self.subTest(rel):
                doc = parse(rel)
                buttons = [a for a in doc.attrs_of("button") if a.get("id") == "menu-toggle"]
                self.assertEqual(len(buttons), 1, "メニューのボタンがない")
                self.assertEqual(buttons[0].get("aria-expanded"), "false")
                self.assertEqual(buttons[0].get("aria-controls"), "site-nav")
                self.assertEqual(buttons[0].get("aria-label"), "メニューを開く")
                self.assertIn("site-nav", doc.ids)


if __name__ == "__main__":
    unittest.main()
