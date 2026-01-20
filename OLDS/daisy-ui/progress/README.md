
# Progress Component

This component displays a progress bar to show the progress of a task or the passing of time.

## Usage

```html
<daisy-progress [value]="50" [max]="100"></daisy-progress>
```

## Inputs

- `value`: `number | null` - The current value of the progress. If `null`, the progress bar will be indeterminate.
- `max`: `number` - The maximum value of the progress. Defaults to `100`.
- `color`: `ProgressColor | null` - The color of the progress bar.
- `customClass`: `string` - Custom classes to add to the progress element.

## Example

```typescript
import { Component } from '@angular/core';
import { ProgressComponent } from './daisy-ui/progress/progress.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [ProgressComponent],
  template: `
    <div class="flex flex-col gap-2 items-center">
      <daisy-progress [value]="10" [max]="100" [color]="'primary'" customClass="w-56"></daisy-progress>
      <daisy-progress [value]="40" [max]="100" [color]="'secondary'" customClass="w-56"></daisy-progress>
      <daisy-progress [value]="70" [max]="100" [color]="'accent'" customClass="w-56"></daisy-progress>
      <daisy-progress [value]="null" [max]="100" customClass="w-56"></daisy-progress>
    </div>
  `,
})
export class AppComponent {}
```
