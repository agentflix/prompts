
# Hero Component

This component displays a hero section, often with a background image and overlaid content.

## Usage

```html
<daisy-hero [backgroundImage]="'https://img.daisyui.com/images/stock/photo-1507358522600-9f71e620c44e.webp'">
  <div class="max-w-md">
    <h1 class="mb-5 text-5xl font-bold">Hello there</h1>
    <p class="mb-5">Provident cupiditate voluptatem et in. Quaerat fugiat ut assumenda excepturi exercitationem quasi. In deleniti eaque aut repudiandae et a id nisi.</p>
    <button class="btn btn-primary">Get Started</button>
  </div>
</daisy-hero>
```

## Inputs

- `backgroundImage`: `string | null` - The URL of the background image for the hero section.
- `minHeight`: `string` - The minimum height of the hero section (e.g., '30rem', '100vh'). Defaults to '30rem'.
- `customClass`: `string` - Custom classes to add to the hero container.

## Content Projection

The content inside the `<daisy-hero>` tags will be projected into the hero content area.

## Example

```typescript
import { Component } from '@angular/core';
import { HeroComponent } from './daisy-ui/hero/hero.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [HeroComponent],
  template: `
    <daisy-hero
      [backgroundImage]="'https://img.daisyui.com/images/stock/photo-1507358522600-9f71e620c44e.webp'"
      [minHeight]="'min-h-screen'"
      [customClass]="'text-neutral-content'"
    >
      <div class="max-w-md">
        <h1 class="mb-5 text-5xl font-bold">Hello there</h1>
        <p class="mb-5">Provident cupiditate voluptatem et in. Quaerat fugiat ut assumenda excepturi exercitationem quasi. In deleniti eaque aut repudiandae et a id nisi.</p>
        <button class="btn btn-primary">Get Started</button>
      </div>
    </daisy-hero>
  `,
})
export class AppComponent {}
```
