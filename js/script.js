(function () {
  // OS で「動きを減らす」にしている人には、演出の動きを出さない
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // スクロールで画面に入った要素を表示する（1 回だけ）
  var targets = document.querySelectorAll('[data-reveal]');
  if (reduceMotion || !('IntersectionObserver' in window)) {
    targets.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-in');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.15 });
    targets.forEach(function (el) { observer.observe(el); });
  }

  // 読み進んだ量を、画面上端の線の長さにする
  var progress = document.getElementById('progress');
  if (progress) {
    var updateProgress = function () {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      progress.style.transform = 'scaleX(' + (max > 0 ? Math.min(window.scrollY / max, 1) : 0) + ')';
    };
    window.addEventListener('scroll', updateProgress, { passive: true });
    window.addEventListener('resize', updateProgress);
    updateProgress();
  }

  // スマホ幅のメニューの開閉
  var toggle = document.getElementById('menu-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    var setMenu = function (open) {
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.setAttribute('aria-label', open ? 'メニューを閉じる' : 'メニューを開く');
      nav.classList.toggle('is-open', open);
    };
    toggle.addEventListener('click', function () {
      setMenu(toggle.getAttribute('aria-expanded') !== 'true');
    });
    nav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () { setMenu(false); });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        setMenu(false);
        toggle.focus();
      }
    });
  }

  // WORKS の行に乗せたとき、画像（なければ色付きの札）をマウスに付いてこさせる
  var peek = document.getElementById('peek');
  if (peek && !reduceMotion && window.matchMedia('(hover: hover)').matches) {
    document.querySelectorAll('.work').forEach(function (row) {
      row.addEventListener('mouseenter', function () {
        var img = row.getAttribute('data-peek-img');
        peek.style.backgroundImage = img ? 'url("' + img + '")' : '';
        peek.textContent = img ? '' : (row.getAttribute('data-peek-label') || '');
        peek.setAttribute('data-tone', img ? '' : (row.getAttribute('data-peek-tone') || ''));
        peek.classList.add('is-on');
      });
      row.addEventListener('mouseleave', function () { peek.classList.remove('is-on'); });
      row.addEventListener('mousemove', function (e) {
        // 画面の右端からはみ出さない位置に置く
        peek.style.left = Math.min(e.clientX + 190, window.innerWidth - 180) + 'px';
        peek.style.top = e.clientY + 'px';
      });
    });
  }
})();
