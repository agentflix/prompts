
# Range Component

This component provides a styled range slider for selecting a value.

## Usage

```html
<daisy-range [(ngModel)]="rangeValue" [min]="0" [max]="100"></daisy-range>
```

## Inputs

- `min`: `number` - The minimum value of the range slider. Defaults to `0`.
- `max`: `number` - The maximum value of the range slider. Defaults to `100`.
- `value`: `number` - The current value of the range slider. Defaults to `0`.
- `step`: `number | null` - The step increment for the range slider.
- `color`: `RangeColor | null` - The color of the range slider.
- `size`: `RangeSize | null` - The size of the range slider.
- `disabled`: `boolean` - Whether the range slider is disabled.
- `customClass`: `string` - Custom classes to add to the range input element.

## Two-way Data Binding

The `daisy-range` component supports `ngModel` for two-way data binding.

## Example

```typescript
import { Component } from '@angular/core';
import { RangeComponent } from './daisy-ui/range/range.component';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RangeComponent, FormsModule],
  template: `
    <div class="flex flex-col gap-4 w-full max-w-xs">
      <daisy-range
        [(ngModel)]="volume"
        [min]="0"
        [max]="100"
        [step]="10"
        [color]="'primary'"
        [size]="'lg'"
      ></daisy-range>
      <p>Volume: {{ volume }}</p>

      <daisy-range
        [(ngModel)]="brightness"
        [min]="0"
        [max]="100"
        [step]="25"
        [color]="'accent'"
        [size]="'md'"
        [disabled]="true"
      ></daisy-range>
      <p>Brightness: {{ brightness }} (Disabled)</p>
    </div>
  `,
})
export class AppComponent {
  volume = 50;
  brightness = 75;
}
```
