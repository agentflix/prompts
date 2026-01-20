
# Mask Component

This component applies a CSS mask to its content, cropping it to various shapes.

## Usage

```html
<daisy-mask [shape]="'heart'">
  <img src="https://img.daisyui.com/images/stock/photo-1567653418876-5bb0e566e1c2.webp" alt="Masked image" />
</daisy-mask>
```

## Inputs

- `shape`: `MaskShape | null` - The shape of the mask. Can be `squircle`, `heart`, `hexagon`, `hexagon-2`, `decagon`, `pentagon`, `diamond`, `square`, `circle`, `star`, `star-2`, `triangle`, `triangle-2`, `triangle-3`, or `triangle-4`.
- `customClass`: `string` - Custom classes to add to the mask container.

## Content Projection

The content inside the `<daisy-mask>` tags will be masked according to the specified `shape`. This typically includes an `<img>` tag.

## Example

```typescript
import { Component } from '@angular/core';
import { MaskComponent } from './daisy-ui/mask/mask.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [MaskComponent],
  template: `
    <div class="flex gap-4">
      <daisy-mask [shape]="'squircle'" customClass="w-40 h-40">
        <img src="https://img.daisyui.com/images/stock/photo-1567653418876-5bb0e566e1c2.webp" alt="Squircle mask" />
      </daisy-mask>

      <daisy-mask [shape]="'star'" customClass="w-40 h-40">
        <img src="https://img.daisyui.com/images/stock/photo-1567653418876-5bb0e566e1c2.webp" alt="Star mask" />
      </daisy-mask>
    </div>
  `,
})
export class AppComponent {}
```
