
# Link Component

This component applies DaisyUI link styles to `<a>` or `<button>` elements.

## Usage

```html
<a daisy-link href="#">Click me</a>
<button daisy-link>Click me</button>
```

## Inputs

- `color`: `LinkColor | null` - The color of the link.
- `hover`: `boolean` - If true, the underline will only show on hover.
- `customClass`: `string` - Custom classes to add to the link element.

## Content Projection

The content inside the `<a daisy-link>` or `<button daisy-link>` tags will be displayed as the link text.

## Example

```typescript
import { Component } from '@angular/core';
import { LinkComponent } from './daisy-ui/link/link.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [LinkComponent],
  template: `
    <p>
      Tailwind CSS resets the style of links by default.
      <br />
      Add "link" class to make it look like a
      <a daisy-link [color]="'primary'" [hover]="true">normal link</a>
      again.
    </p>
    <button daisy-link [color]="'secondary'">Another Link</button>
  `,
})
export class AppComponent {}
```
