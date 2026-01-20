
# Select Component

This component provides a styled select dropdown for picking a value from a list of options.

## Usage

```html
<daisy-select
  [options]="colors"
  [placeholder]="'Pick a color'"
  [(ngModel)]="selectedColor"
></daisy-select>
```

## Inputs

- `options`: `SelectOption[]` - An array of objects, each representing an option in the dropdown.
- `placeholder`: `string | null` - The placeholder text for the select input.
- `color`: `SelectColor | null` - The color of the select input.
- `size`: `SelectSize | null` - The size of the select input.
- `ghost`: `boolean` - If true, applies the ghost style.
- `disabled`: `boolean` - Whether the select input is disabled.
- `customClass`: `string` - Custom classes to add to the select element.

## Two-way Data Binding

The `daisy-select` component supports `ngModel` for two-way data binding.

## Interface

```typescript
export interface SelectOption {
  value: any;
  label: string;
  disabled?: boolean;
}
```

## Example

```typescript
import { Component } from '@angular/core';
import { SelectComponent, SelectOption } from './daisy-ui/select/select.component';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [SelectComponent, FormsModule],
  template: `
    <div class="flex flex-col gap-4 w-full max-w-xs">
      <daisy-select
        [options]="frameworks"
        [placeholder]="'Pick a Framework'"
        [(ngModel)]="selectedFramework"
        [color]="'info'"
        [size]="'lg'"
      ></daisy-select>
      <p>Selected Framework: {{ selectedFramework }}</p>

      <daisy-select
        [options]="osOptions"
        [placeholder]="'Pick an OS'"
        [(ngModel)]="selectedOS"
        [color]="'warning'"
        [ghost]="true"
      ></daisy-select>
      <p>Selected OS: {{ selectedOS }}</p>
    </div>
  `,
})
export class AppComponent {
  frameworks: SelectOption[] = [
    { value: 'react', label: 'React' },
    { value: 'vue', label: 'Vue' },
    { value: 'angular', label: 'Angular' },
  ];
  selectedFramework: string | null = null;

  osOptions: SelectOption[] = [
    { value: 'windows', label: 'Windows' },
    { value: 'macos', label: 'MacOS' },
    { value: 'linux', label: 'Linux' },
  ];
  selectedOS: string | null = null;
}
```
