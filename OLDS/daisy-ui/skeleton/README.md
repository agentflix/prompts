
# Skeleton Component

This component displays a placeholder with a loading animation, commonly used to indicate that content is being loaded.

## Usage

```html
<daisy-skeleton [width]="'w-32'" [height]="'h-32'"></daisy-skeleton>
```

## Inputs

- `width`: `string | null` - The width of the skeleton. Can be a Tailwind CSS width class (e.g., `'w-32'`, `'w-full'`) or a CSS value (e.g., `'128px'`).
- `height`: `string | null` - The height of the skeleton. Can be a Tailwind CSS height class (e.g., `'h-32'`, `'h-4'`) or a CSS value (e.g., `'128px'`).
- `shape`: `SkeletonShape` - The shape of the skeleton. Can be `square`, `circle`, or `text`. Defaults to `square`.
- `customClass`: `string` - Custom classes to add to the skeleton element.

## Example

```typescript
import { Component } from '@angular/core';
import { SkeletonComponent } from './daisy-ui/skeleton/skeleton.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [SkeletonComponent],
  template: `
    <div class="flex flex-col gap-4 w-52">
      <div class="flex gap-4 items-center">
        <daisy-skeleton [width]="'w-16'" [height]="'h-16'" [shape]="'circle'"></daisy-skeleton>
        <div class="flex flex-col gap-4">
          <daisy-skeleton [width]="'w-20'" [height]="'h-4'" [shape]="'text'"></daisy-skeleton>
          <daisy-skeleton [width]="'w-28'" [height]="'h-4'" [shape]="'text'"></daisy-skeleton>
        </div>
      </div>
      <daisy-skeleton [width]="'w-full'" [height]="'h-32'"></daisy-skeleton>
    </div>
  `,
})
export class AppComponent {}
```
