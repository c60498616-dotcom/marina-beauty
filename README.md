# МАРИНА БЬЮТИ — Deep Blue Beauty Studio

Премиум-сайт салона красоты в эстетике *Modern Nautical Elegance*.
Сгенерирован в [Stitch](https://stitch.withgoogle.com) (project `10199307101743259618`),
вручную пересобран и обогащён motion-слоем по мотивам SuperDesign **Motion** / **Kinetic**.

## Страницы

| Файл            | Содержимое                       |
| --------------- | -------------------------------- |
| `index.html`    | Главная: hero, услуги, бренд     |
| `gallery.html`  | Галерея работ                    |
| `price.html`    | Прайс-лист                       |
| `booking.html`  | Онлайн-запись                    |

## Стек

- Чистый HTML.
- [Tailwind CSS](https://tailwindcss.com) через CDN, конфиг встроен в каждый HTML.
- Шрифты `Outfit` / `Manrope` через Google Fonts.
- Иконки — `Material Symbols Outlined`.
- `assets/animations.css` + `assets/scripts.js` — собственный motion-слой.

## Motion-слой

`assets/animations.css`:

- **Page fade-in** при загрузке.
- **Scroll reveal** через `data-reveal` (+ `data-reveal-delay`, варианты `left|right|scale`).
- **Hero parallax** на `.hero-parallax` (rAF + `scrollY`).
- **Brand float**, **pulse-dot**, **blob drift** — мягкие декоративные циклы.
- **Btn shimmer** — glare-эффект на основных CTA.
- **Lift / kinetic** — поднятие карточек на hover.
- **Underline draw** для навигации (`.nav-link`).
- **Marquee** — горизонтальная лента (готов к использованию).
- Полностью уважает `prefers-reduced-motion: reduce`.

`assets/scripts.js`:

- `IntersectionObserver` для scroll-reveal.
- `requestAnimationFrame` parallax.
- Авто-подсветка активного пункта меню по имени файла (`data-route`).

## Локальный запуск

Любой статический сервер. Пример:

```powershell
python -m http.server 5500
# открыть http://localhost:5500
```

## Деплой

Подходит любая статика — GitHub Pages, Vercel, Netlify.

## Источник

- Stitch проект: `projects/10199307101743259618` — *Deep Blue Beauty Studio*.
- Скриншоты оригинальных макетов: `screenshots/`.
