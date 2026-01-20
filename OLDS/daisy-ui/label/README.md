
# Label Component

This component is used to provide a name or title for an input field, and can also function as a floating label.

## Usage

```html
<daisy-label>
  <span class="label-text">Your Email</span>
  <input type="email" placeholder="mail@site.com" class="input input-md" />
</daisy-label>
```

## Inputs

- `floating`: `boolean` - If true, the label will act as a floating label.
- `customClass`: `string` - Custom classes to add to the label element.

## Content Projection

The content inside the `<daisy-label>` tags will be projected into the component. This typically includes a `<span>` for the label text and an `<input>` or `<select>` element.

## Example

```typescript
import { Component } from '@angular/core';
import { LabelComponent } from './daisy-ui/label/label.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [LabelComponent],
  template: `
    <div class="grid gap-4 w-xs">
      <daisy-label>
        <span class="label-text">https://</span>
        <input type="text" placeholder="URL" class="input" />
      </daisy-label>

      <daisy-label [floating]="true" customClass="w-full max-w-xs">
        <span>Your Email</span>
        <input type="email" placeholder="mail@site.com" class="input input-md" />
      </daisy-label>
    </div>
  `,
})
export class AppComponent {}
```
