
# Filter Component

This component provides a group of radio buttons for filtering items, with an optional reset button.

## Usage

```html
<daisy-filter [options]="frameworks" [(selectedOption)]="selectedFramework"></daisy-filter>
```

## Inputs

- `options`: `FilterOption[]` - An array of objects, each with a `label` and `value` for the filter options.
- `name`: `string` - The name attribute for the radio buttons. Defaults to `filter-group`.
- `selectedOption`: `string | null` - The currently selected option's value. Use `[(selectedOption)]` for two-way binding.
- `customClass`: `string` - Custom classes to add to the filter container.

## Outputs

- `selectionChange`: `EventEmitter<string | null>` - Emits the value of the newly selected option, or `null` if the filter is reset.

## Interface

```typescript
export interface FilterOption {
  label: string;
  value: string;
}
```

## Example

```typescript
import { Component } from '@angular/core';
import { FilterComponent, FilterOption } from './daisy-ui/filter/filter.component';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FilterComponent, FormsModule],
  template: `
    <daisy-filter
      [options]="frameworks"
      [(selectedOption)]="selectedFramework"
      (selectionChange)="onSelectionChange($event)"
    ></daisy-filter>
    <p>Selected framework: {{ selectedFramework }}</p>
  `,
})
export class AppComponent {
  frameworks: FilterOption[] = [
    { label: 'Svelte', value: 'svelte' },
    { label: 'Vue', value: 'vue' },
    { label: 'React', value: 'react' },
  ];
  selectedFramework: string | null = null;

  onSelectionChange(selection: string | null) {
    console.log('Selection changed to:', selection);
  }
}
```
