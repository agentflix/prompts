
# Input Component

This component provides a styled input field with various customization options.

## Usage

```html
<daisy-input [(ngModel)]="inputValue" placeholder="Type something"></daisy-input>
```

## Inputs

- `type`: `InputType` - The type of the input field (e.g., `text`, `password`, `email`, `number`, `date`, etc.). Defaults to `text`.
- `placeholder`: `string` - The placeholder text for the input field.
- `color`: `InputColor | null` - The color of the input field.
- `size`: `InputSize | null` - The size of the input field.
- `ghost`: `boolean` - If true, applies the ghost style.
- `disabled`: `boolean` - Whether the input field is disabled.
- `customClass`: `string` - Custom classes to add to the input element.

## Two-way Data Binding

The `daisy-input` component supports `ngModel` for two-way data binding.

```html
<daisy-input [(ngModel)]="myValue"></daisy-input>
```

## Example

```typescript
import { Component } from '@angular/core';
import { InputComponent } from './daisy-ui/input/input.component';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [InputComponent, FormsModule],
  template: `
    <div class="grid gap-4 w-xs">
      <daisy-input
        [(ngModel)]="name"
        placeholder="Your Name"
        [color]="'primary'"
        [size]="'lg'"
      ></daisy-input>
      <daisy-input
        [(ngModel)]="email"
        type="email"
        placeholder="Your Email"
        [ghost]="true"
      ></daisy-input>
      <p>Name: {{ name }}</p>
      <p>Email: {{ email }}</p>
    </div>
  `,
})
export class AppComponent {
  name = '';
  email = '';
}
```
