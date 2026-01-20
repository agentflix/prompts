
# Alert Component

This component displays an alert message.

## Usage

```html
<daisy-alert [color]="'info'" [style]="'soft'">
  <span>This is an informational message.</span>
</daisy-alert>
```

## Inputs

- `color`: `AlertColor | null` - The color of the alert. Can be `info`, `success`, `warning`, or `error`.
- `style`: `AlertStyle | null` - The style of the alert. Can be `outline`, `dash`, or `soft`.
- `direction`: `AlertDirection | null` - The direction of the alert. Can be `vertical` or `horizontal`.
- `customClass`: `string` - Custom classes to add to the component.

## Content Projection

The content of the alert is projected into the component using `<ng-content>`.

## Example

```typescript
import { Component } from '@angular/core';
import { AlertComponent } from './daisy-ui/alert/alert.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [AlertComponent],
  template: `
    <daisy-alert [color]="'success'">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
      <span>Your purchase has been confirmed!</span>
    </daisy-alert>
  `,
})
export class AppComponent {}
```
