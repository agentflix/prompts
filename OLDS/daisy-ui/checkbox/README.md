
# Checkbox Component

This component displays a checkbox.

## Usage

```html
<daisy-checkbox [(checked)]="isChecked"></daisy-checkbox>
```

## Inputs

- `checked`: `boolean` - Whether the checkbox is checked.
- `disabled`: `boolean` - Whether the checkbox is disabled.
- `indeterminate`: `boolean` - Whether the checkbox is in an indeterminate state.
- `color`: `CheckboxColor | null` - The color of the checkbox.
- `size`: `CheckboxSize | null` - The size of the checkbox.
- `customClass`: `string` - Custom classes to add to the component.

## Outputs

- `checkedChange`: `EventEmitter<boolean>` - Emits the new checked state when it changes.

## Example

```typescript
import { Component } from '@angular/core';
import { CheckboxComponent } from './daisy-ui/checkbox/checkbox.component';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CheckboxComponent, FormsModule],
  template: `
    <daisy-checkbox [(checked)]="isChecked" [color]="'primary'" [size]="'lg'"></daisy-checkbox>
    <p>Checkbox is: {{ isChecked }}</p>
  `,
})
export class AppComponent {
  isChecked = true;
}
```
