
# Stack Component

This component visually puts elements on top of each other, creating a stacked effect.

## Usage

```html
<daisy-stack>
  <div class="grid rounded-box bg-primary text-primary-content place-content-center">1</div>
  <div class="grid rounded-box bg-accent text-accent-content place-content-center">2</div>
  <div class="grid rounded-box bg-secondary text-secondary-content place-content-center">3</div>
</daisy-stack>
```

## Inputs

- `alignVertical`: `StackVerticalAlignment | null` - Aligns the children elements vertically. Can be `top` or `bottom`.
- `alignHorizontal`: `StackHorizontalAlignment | null` - Aligns the children elements horizontally. Can be `start` or `end`.
- `customClass`: `string` - Custom classes to add to the stack container.

## Content Projection

The `daisy-stack` component projects its content. Each direct child element will be stacked on top of the previous one.

## Example

```typescript
import { Component } from '@angular/core';
import { StackComponent } from './daisy-ui/stack/stack.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [StackComponent],
  template: `
    <daisy-stack [alignVertical]="'top'" [alignHorizontal]="'start'" customClass="h-20 w-32">
      <div class="grid rounded-box bg-primary text-primary-content place-content-center">1</div>
      <div class="grid rounded-box bg-accent text-accent-content place-content-center">2</div>
      <div class="grid rounded-box bg-secondary text-secondary-content place-content-center">3</div>
    </daisy-stack>

    <daisy-stack customClass="mb-4 w-48">
      <img src="https://img.daisyui.com/images/stock/photo-1572635148818-ef6fd45eb394.webp" alt="Tailwind CSS example 1" class="rounded-box" />
      <img src="https://img.daisyui.com/images/stock/photo-1565098772267-60af42b81ef2.webp" alt="Tailwind CSS example 2" class="rounded-box" />
      <img src="https://img.daisyui.com/images/stock/photo-1559703248-dcaaec9fab78.webp" alt="Tailwind CSS example 3" class="rounded-box" />
    </daisy-stack>
  `,
})
export class AppComponent {}
```
