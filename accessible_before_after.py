"""Reusable accessible before/after component for this Stage 2 generator."""
from __future__ import annotations

import html


def validate_pair(pair: dict) -> None:
    assert pair.get("approved") is True, "comparison pair is not explicitly approved"
    assert pair.get("id") and pair.get("source_page_url")
    for role in ("before", "after"):
        side = pair.get(role) or {}
        assert side.get("source_url"), f"{role} source_url missing"
        assert side.get("local_path"), f"{role} local_path missing"
        assert side.get("label") in {"Before", "After"}, f"{role} label invalid"


def render_before_after(
    pair: dict,
    *,
    before_href: str,
    after_href: str,
    before_alt: str,
    after_alt: str,
    input_id: str | None = None,
) -> str:
    """Return provenance-marked HTML with a native range and no-JS fallback."""
    validate_pair(pair)
    if not before_alt.strip() or not after_alt.strip():
        raise ValueError("comparison alt text must be non-empty")
    pair_id = str(pair["id"])
    control_id = input_id or f"comparison-{pair_id}"
    esc = lambda value: html.escape(str(value), quote=True)
    return f'''<section class="comparison" data-comparison-id="{esc(pair_id)}">
  <div class="comparison-stage">
    <div class="comparison-before">
      <img src="{esc(before_href)}" alt="{esc(before_alt)}" data-source-url="{esc(pair['before']['source_url'])}">
      <span class="comparison-label comparison-label-before">Before</span>
    </div>
    <div class="comparison-after">
      <img src="{esc(after_href)}" alt="{esc(after_alt)}" data-source-url="{esc(pair['after']['source_url'])}">
      <span class="comparison-label comparison-label-after">After</span>
    </div>
  </div>
  <div class="comparison-control">
    <label for="{esc(control_id)}">Move slider to compare before and after</label>
    <input id="{esc(control_id)}" type="range" min="0" max="100" value="50" aria-valuetext="50% after image revealed">
  </div>
</section>'''


CSS_SNIPPET = r'''
/* Base state is the no-JS fallback: two ordinary, labeled images. */
.comparison-stage{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.75rem}
.comparison-stage img{width:100%;height:auto;aspect-ratio:4/3;object-fit:cover}
.comparison-label{display:block;font-weight:700}
.comparison-control{display:none}
/* JavaScript opts into the overlay only after finding a working range. */
.comparison.is-enhanced .comparison-stage{display:block;position:relative;overflow:hidden;aspect-ratio:4/3}
.comparison.is-enhanced .comparison-stage>div{position:absolute;inset:0}
.comparison.is-enhanced .comparison-stage img{position:absolute;inset:0;width:100%;height:100%}
.comparison.is-enhanced .comparison-after{clip-path:inset(0 calc(100% - var(--comparison-position,50%)) 0 0)}
.comparison.is-enhanced .comparison-control{display:grid}
@media(max-width:520px){.comparison-stage{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){.comparison-after{transition:none}}
'''.strip()


JS_SNIPPET = r'''
document.querySelectorAll('[data-comparison-id]').forEach((comparison) => {
  const range = comparison.querySelector('input[type="range"]');
  if (!range) return;
  comparison.classList.add('is-enhanced');
  const sync = () => {
    comparison.style.setProperty('--comparison-position', `${range.value}%`);
    range.setAttribute('aria-valuetext', `${range.value}% after image revealed`);
  };
  range.addEventListener('input', sync);
  sync();
});
'''.strip()
