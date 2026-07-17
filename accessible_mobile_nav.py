"""Reusable accessible mobile navigation capability for this Stage 2 preview.

The CTA is rendered outside the collapsible panel. Base markup remains usable
without JavaScript; JS adds the enhancement class that enables mobile collapse.
"""
from html import escape

BREAKPOINT_PX = 768


def render_mobile_nav(
    *,
    nav_id: str,
    links: list[tuple[str, str]],
    cta_label: str,
    cta_href: str,
    current_href: str | None = None,
    toggle_label: str = "Open navigation menu",
) -> str:
    """Return header controls with a collapsible link panel and persistent CTA."""
    nav_id = escape(nav_id, quote=True)
    rendered_links = []
    for label, href in links:
        current = ' aria-current="page"' if href == current_href else ''
        rendered_links.append(
            f'<a href="{escape(href, quote=True)}"{current}>{escape(label)}</a>'
        )
    link_markup = "\n".join(rendered_links)
    return f'''<button class="mobile-nav-toggle" type="button" aria-expanded="false" aria-controls="{nav_id}" aria-label="{escape(toggle_label, quote=True)}">
  <span class="mobile-nav-toggle__icon" aria-hidden="true"><span></span><span></span><span></span></span>
</button>
<nav class="nav" id="{nav_id}" aria-label="Primary navigation">
{link_markup}
</nav>
<a class="header-cta call" href="{escape(cta_href, quote=True)}">{escape(cta_label)}</a>'''


CSS_SNIPPET = f'''
.mobile-nav-toggle {{
  display: none;
  min-width: 44px;
  min-height: 44px;
  align-items: center;
  justify-content: center;
  border: 2px solid currentColor;
  border-radius: .5rem;
  background: transparent;
  color: var(--navy, currentColor);
  cursor: pointer;
}}
.mobile-nav-toggle__icon,
.mobile-nav-toggle__icon span {{ display: block; }}
.mobile-nav-toggle__icon {{ width: 1.5rem; }}
.mobile-nav-toggle__icon span {{ height: 2px; margin: .28rem 0; background: currentColor; }}

@media (max-width: {BREAKPOINT_PX}px) {{
  /* Collapse only after JS proves the toggle is operable. */
  .mobile-nav-enhanced .mobile-nav-toggle {{ display: inline-flex; }}
  .mobile-nav-enhanced .nav {{
    position: absolute;
    inset-inline: 0;
    top: 100%;
    z-index: 1000;
    display: none;
    flex-direction: column;
    align-items: stretch;
    padding: .75rem;
    background: var(--nav-panel-bg, var(--white, #fff));
    border-block-start: 1px solid color-mix(in srgb, currentColor 20%, transparent);
    box-shadow: 0 .75rem 1.5rem rgb(0 0 0 / .18);
  }}
  .mobile-nav-enhanced .nav[data-mobile-open="true"] {{ display: flex; }}
  .mobile-nav-enhanced .nav a {{ min-height: 44px; display: flex; align-items: center; }}
  .mobile-nav-enhanced .header-cta {{ display: inline-flex; }}
}}
'''


JS_SNIPPET = r'''
document.querySelectorAll('.mobile-nav-toggle[aria-controls]').forEach((toggle) => {
  const panel = document.getElementById(toggle.getAttribute('aria-controls'));
  if (!panel) return;

  const mobileQuery = window.matchMedia('(max-width: 768px)');
  const closeMenu = ({ restoreFocus = false } = {}) => {
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Open navigation menu');
    panel.dataset.mobileOpen = 'false';
    if (restoreFocus) toggle.focus();
  };

  document.documentElement.classList.add('mobile-nav-enhanced');
  closeMenu();

  toggle.addEventListener('click', () => {
    const opening = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(opening));
    toggle.setAttribute('aria-label', opening ? 'Close navigation menu' : 'Open navigation menu');
    panel.dataset.mobileOpen = String(opening);
  });

  panel.addEventListener('click', (event) => {
    if (event.target.closest('a') && mobileQuery.matches) closeMenu();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
      closeMenu({ restoreFocus: true });
    }
  });

  document.addEventListener('click', (event) => {
    if (mobileQuery.matches && toggle.getAttribute('aria-expanded') === 'true' &&
        !panel.contains(event.target) && !toggle.contains(event.target)) closeMenu();
  });

  mobileQuery.addEventListener?.('change', () => closeMenu());
});
'''


def validation_markers() -> tuple[str, ...]:
    return (
        'class="mobile-nav-toggle"',
        'aria-expanded="false"',
        'aria-controls=',
        'class="header-cta call"',
        '.mobile-nav-enhanced .nav[data-mobile-open="true"]',
        "event.key === 'Escape'",
        "window.matchMedia('(max-width: 768px)')",
    )
