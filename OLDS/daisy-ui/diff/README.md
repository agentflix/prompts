
# Diff Component

This component displays a side-by-side comparison of two items with a resizer.

## Usage

```html
<daisy-diff>
  <div diff-item-1>
    <img src="https://img.daisyui.com/images/stock/photo-1560717789-0ac7c58ac90a.webp" alt="daisy" />
  </div>
  <div diff-item-2>
    <img src="https://img.daisyui.com/images/stock/photo-1560717789-0ac7c58ac90a-blur.webp" alt="daisy" />
  </div>
</daisy-diff>
```

## Inputs

- `customClass`: `string` - Custom classes to add to the component.

## Content Projection

The diff component uses content projection for the two items to compare.

- `[diff-item-1]`: Use this attribute on an element to define the first item.
- `[diff-item-2]`: Use this attribute on an element to define the second item.

## Example

```typescript
import { Component } from '@angular/core';
import { DiffComponent } from './daisy-ui/diff/diff.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [DiffComponent],
  template: `
    <daisy-diff>
      <div diff-item-1 class="bg-primary text-primary-content text-4xl lg:text-9xl font-black grid place-content-center">DAISY</div>
      <div diff-item-2 class="bg-base-200 text-4xl lg:text-9xl font-black grid place-content-center">DAISY</div>
    </daisy-diff>
  `,
})
export class AppComponent {}
```
