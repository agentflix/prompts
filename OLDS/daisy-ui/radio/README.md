
# Radio Component

This component provides a styled radio button, allowing users to select one option from a set.

## Usage

```html
<daisy-radio name="my-radio-group" value="option1" [(ngModel)]="selectedOption"></daisy-radio>
```

## Inputs

- `name`: `string` - The name attribute for the radio button group. All radio buttons in a group must have the same `name`.
- `value`: `any` - The value associated with this radio button.
- `checked`: `boolean` - Whether the radio button is checked.
- `disabled`: `boolean` - Whether the radio button is disabled.
- `color`: `RadioColor | null` - The color of the radio button.
- `size`: `RadioSize | null` - The size of the radio button.
- `customClass`: `string` - Custom classes to add to the radio button element.

## Two-way Data Binding

The `daisy-radio` component supports `ngModel` for two-way data binding. The `[(ngModel)]` should be bound to the `value` of the selected radio button.

## Example

```typescript
import { Component } from '@angular/core';
import { RadioComponent } from './daisy-ui/radio/radio.component';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RadioComponent, FormsModule],
  template: `
    <div class="flex flex-col gap-2">
      <label class="flex items-center gap-2">
        <daisy-radio name="fruit" value="apple" [(ngModel)]="selectedFruit" [color]="'primary'"></daisy-radio>
        Apple
      </label>
      <label class="flex items-center gap-2">
        <daisy-radio name="fruit" value="orange" [(ngModel)]="selectedFruit" [color]="'secondary'"></daisy-radio>
        Orange
      </label>
      <label class="flex items-center gap-2">
        <daisy-radio name="fruit" value="grape" [(ngModel)]="selectedFruit" [color]="'accent'" [disabled]="true"></daisy-radio>
        Grape (Disabled)
      </label>
    </div>
    <p class="mt-4">Selected fruit: {{ selectedFruit }}</p>
  `,
})
export class AppComponent {
  selectedFruit: string = 'apple';
}
```
