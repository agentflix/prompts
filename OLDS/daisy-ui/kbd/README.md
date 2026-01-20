
# Kbd Component

This component is used to display keyboard shortcuts.

## Usage

```html
<daisy-kbd>K</daisy-kbd>
```

## Inputs

- `size`: `KbdSize | null` - The size of the keyboard key. Can be `xs`, `sm`, `md`, `lg`, or `xl`.
- `customClass`: `string` - Custom classes to add to the kbd element.

## Content Projection

The content inside the `<daisy-kbd>` tags will be displayed as the keyboard key or shortcut.

## Example

```typescript
import { Component } from '@angular/core';
import { KbdComponent } from './daisy-ui/kbd/kbd.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [KbdComponent],
  template: `
    <span>Press <daisy-kbd [size]="'sm'">F</daisy-kbd> to pay respects.</span>

    <div class="flex justify-center gap-1 w-full mb-1">
      <daisy-kbd>ctrl</daisy-kbd>
      +
      <daisy-kbd>shift</daisy-kbd>
      +
      <daisy-kbd>del</daisy-kbd>
    </div>
  `,
})
export class AppComponent {}
```
