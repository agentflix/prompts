
# Button Component

This component displays a button.

## Usage

```html
<button daisy-button [color]="'primary'">Primary</button>
```

## Inputs

- `color`: `ButtonColor | null` - The color of the button.
- `size`: `ButtonSize | 'responsive' | null` - The size of the button.
- `style`: `ButtonStyle | null` - The style of the button.
- `shape`: `ButtonShape | null` - The shape of the button.
- `wide`: `boolean` - Whether the button should be wide.
- `block`: `boolean` - Whether the button should be a block element.
- `disabled`: `boolean` - Whether the button is disabled.
- `loading`: `boolean` - Whether the button is in a loading state.
- `customClass`: `string` - Custom classes to add to the component.

## Content Projection

The content of the button is projected into the component using `<ng-content>`.

## Example

```typescript
import { Component } from '@angular/core';
import { ButtonComponent } from './daisy-ui/button/button.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [ButtonComponent],
  template: `
    <button daisy-button [color]="'success'" [style]="'outline'">
      Success
    </button>
    <button daisy-button [color]="'primary'" [loading]="true">
      Loading
    </button>
  `,
})
export class AppComponent {}
```
