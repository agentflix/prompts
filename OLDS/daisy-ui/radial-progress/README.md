
# Radial Progress Component

This component displays a circular progress indicator, useful for showing the progress of a task or a value.

## Usage

```html
<daisy-radial-progress [value]="70">70%</daisy-radial-progress>
```

## Inputs

- `value`: `number` - The current value of the progress (0-100).
- `size`: `string | null` - The size of the radial progress (e.g., `'5rem'`, `'12rem'`).
- `thickness`: `string | null` - The thickness of the progress bar (e.g., `'2px'`, `'2rem'`).
- `customClass`: `string` - Custom classes to add to the radial progress container.

## Content Projection

The content inside the `<daisy-radial-progress>` tags will be displayed in the center of the radial progress indicator.

## Example

```typescript
import { Component } from '@angular/core';
import { RadialProgressComponent } from './daisy-ui/radial-progress/radial-progress.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RadialProgressComponent],
  template: `
    <div class="flex gap-4">
      <daisy-radial-progress [value]="70" customClass="text-primary" [size]="'12rem'" [thickness]="'2px'">
        70%
      </daisy-radial-progress>
      <daisy-radial-progress [value]="20" customClass="bg-primary text-primary-content border-4 border-primary">
        20%
      </daisy-radial-progress>
    </div>
  `,
})
export class AppComponent {}
```
