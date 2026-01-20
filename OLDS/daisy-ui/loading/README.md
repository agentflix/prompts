
# Loading Component

This component displays an animation to indicate that something is loading.

## Usage

```html
<daisy-loading [type]="'spinner'" [size]="'md'"></daisy-loading>
```

## Inputs

- `type`: `LoadingType` - The type of loading animation. Can be `spinner`, `dots`, `ring`, `ball`, `bars`, or `infinity`. Defaults to `spinner`.
- `size`: `LoadingSize | null` - The size of the loading animation. Can be `xs`, `sm`, `md`, `lg`, or `xl`.
- `customClass`: `string` - Custom classes to add to the loading element.

## Example

```typescript
import { Component } from '@angular/core';
import { LoadingComponent } from './daisy-ui/loading/loading.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [LoadingComponent],
  template: `
    <div class="flex flex-col gap-4 items-center">
      <daisy-loading [type]="'spinner'" [size]="'lg'" customClass="text-primary"></daisy-loading>
      <daisy-loading [type]="'dots'" [size]="'md'" customClass="text-secondary"></daisy-loading>
      <daisy-loading [type]="'bars'" [size]="'sm'" customClass="text-accent"></daisy-loading>
    </div>
  `,
})
export class AppComponent {}
```
