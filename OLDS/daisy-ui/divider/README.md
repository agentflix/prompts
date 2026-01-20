
# Divider Component

This component displays a horizontal or vertical divider, optionally with text.

## Usage

```html
<daisy-divider>OR</daisy-divider>
```

## Inputs

- `direction`: `DividerDirection | null` - The direction of the divider. Can be `horizontal` or `vertical`.
- `color`: `DividerColor | null` - The color of the divider.
- `placement`: `DividerPlacement | null` - The placement of the text within the divider. Can be `start` or `end`.
- `customClass`: `string` - Custom classes to add to the component.

## Content Projection

The content of the divider (e.g., "OR") is projected into the component using `<ng-content>`.

## Example

```typescript
import { Component } from '@angular/core';
import { DividerComponent } from './daisy-ui/divider/divider.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [DividerComponent],
  template: `
    <div class="flex flex-col w-full">
      <div class="grid h-20 card bg-base-300 rounded-box place-items-center">content</div>
      <daisy-divider [color]="'primary'">OR</daisy-divider>
      <div class="grid h-20 card bg-base-300 rounded-box place-items-center">content</div>
    </div>
  `,
})
export class AppComponent {}
```
