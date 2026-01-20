
# Indicator Component

This component is used to place an element (indicator item) on the corner of another element.

## Usage

```html
<daisy-indicator>
  <span indicator-item class="badge badge-primary">New</span>
  <div class="grid w-32 h-32 rounded bg-base-300 place-items-center">content</div>
</daisy-indicator>
```

## Inputs

- `horizontal`: `IndicatorHorizontal | null` - Aligns the indicator item horizontally. Can be `start`, `center`, or `end`.
- `vertical`: `IndicatorVertical | null` - Aligns the indicator item vertically. Can be `top`, `middle`, or `bottom`.
- `customClass`: `string` - Custom classes to add to the indicator container.
- `indicatorItemCustomClass`: `string` - Custom classes to add to the indicator item.

## Content Projection

The indicator component uses content projection for its main content and the indicator item.

- `[indicator-item]`: Use this attribute on an element to define the indicator item (e.g., a `<span>` with a badge).
- Any other content within `<daisy-indicator>` will be the main content around which the indicator item is placed.

## Example

```typescript
import { Component } from '@angular/core';
import { IndicatorComponent } from './daisy-ui/indicator/indicator.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [IndicatorComponent],
  template: `
    <daisy-indicator [horizontal]="'end'" [vertical]="'top'">
      <span indicator-item class="badge badge-secondary">12</span>
      <button class="btn">inbox</button>
    </daisy-indicator>

    <daisy-indicator [horizontal]="'center'" [vertical]="'middle'" customClass="max-w-xs">
      <span indicator-item class="badge">Only available for Pro users</span>
      <img alt="Tailwind CSS examples" class="rounded" src="https://img.daisyui.com/images/stock/photo-1606107557195-0e29a4b5b4aa.webp" />
    </daisy-indicator>
  `,
})
export class AppComponent {}
```
